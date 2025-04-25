"""
User synchronization service for Keycloak integration
"""
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import threading
import time

# Import keycloak client
from infrastructure.auth.keycloak_client import KeycloakClient

# Import database models and utilities
from database.models.user import User
from utils.extensions import db

logger = logging.getLogger(__name__)

class UserSyncService:
    """
    Service for synchronizing users between the application database and Keycloak
    """
    def __init__(self, keycloak_client: KeycloakClient):
        """
        Initialize the user synchronization service
        
        Args:
            keycloak_client: Initialized KeycloakClient instance
        """
        self.keycloak_client = keycloak_client
        self._sync_lock = threading.RLock()  # Reentrant lock for thread safety
        
    def create_user_in_keycloak(self, user: User, password: str) -> Optional[str]:
        """
        Create a user in Keycloak based on a local user
        
        Args:
            user: Local User model instance
            password: Plain text password for the new Keycloak user
            
        Returns:
            Keycloak user ID if successful, None otherwise
        """
        if user.keycloak_id:
            logger.warning(f"User {user.username} already has a Keycloak ID: {user.keycloak_id}")
            return user.keycloak_id
            
        # Split full name into first and last name for Keycloak
        name_parts = (user.full_name or "").split(maxsplit=1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Create user in Keycloak
        keycloak_id = self.keycloak_client.create_user(
            username=user.username,
            email=user.email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            enabled=True
        )
        
        if keycloak_id:
            # Update local user with Keycloak ID
            user.keycloak_id = keycloak_id
            db.session.commit()
            logger.info(f"Created Keycloak user for {user.username} with ID {keycloak_id}")
        
        return keycloak_id
    
    def import_user_from_keycloak(self, keycloak_user: Dict) -> Optional[User]:
        """
        Import a user from Keycloak into the local database
        
        Args:
            keycloak_user: Keycloak user data dictionary
            
        Returns:
            User model instance if successful, None otherwise
        """
        keycloak_id = keycloak_user.get('id')
        if not keycloak_id:
            logger.error("Keycloak user missing ID field")
            return None
            
        # Check if user already exists in local database
        existing_user = User.query.filter_by(keycloak_id=keycloak_id).first()
        if existing_user:
            logger.info(f"User with Keycloak ID {keycloak_id} already exists locally")
            return existing_user
            
        # Extract user details from Keycloak data
        username = keycloak_user.get('username')
        email = keycloak_user.get('email')
        
        if not username or not email:
            logger.error(f"Keycloak user {keycloak_id} missing required fields")
            return None
            
        # Construct full name from Keycloak first and last name
        first_name = keycloak_user.get('firstName', '')
        last_name = keycloak_user.get('lastName', '')
        full_name = f"{first_name} {last_name}".strip()
        
        # Create new user in local database
        try:
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                keycloak_id=keycloak_id,
                account_created=datetime.utcnow()
            )
            
            # Note: Password is managed by Keycloak, so we set a placeholder
            # This ensures the user can only log in via Keycloak
            new_user.password_hash = "KEYCLOAK_MANAGED"
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"Imported user {username} from Keycloak with ID {keycloak_id}")
            return new_user
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to import user {username} from Keycloak: {e}")
            return None
    
    def update_local_user_from_keycloak(self, user: User) -> bool:
        """
        Update a local user with data from Keycloak
        
        Args:
            user: Local User model instance with keycloak_id
            
        Returns:
            True if successful, False otherwise
        """
        if not user.keycloak_id:
            logger.error(f"User {user.username} has no Keycloak ID")
            return False
            
        # Get user data from Keycloak
        keycloak_user = self.keycloak_client.get_user_by_id(user.keycloak_id)
        if not keycloak_user:
            logger.error(f"User {user.username} not found in Keycloak with ID {user.keycloak_id}")
            return False
            
        # Update local user data
        try:
            # Update email if different
            if keycloak_user.get('email') and keycloak_user['email'] != user.email:
                user.email = keycloak_user['email']
                
            # Update full name if available
            first_name = keycloak_user.get('firstName', '')
            last_name = keycloak_user.get('lastName', '')
            full_name = f"{first_name} {last_name}".strip()
            
            if full_name and full_name != user.full_name:
                user.full_name = full_name
                
            # Update other fields as needed
            
            db.session.commit()
            logger.info(f"Updated local user {user.username} from Keycloak")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update local user {user.username} from Keycloak: {e}")
            return False
    
    def update_keycloak_user_from_local(self, user: User) -> bool:
        """
        Update a Keycloak user with data from the local database
        
        Args:
            user: Local User model instance with keycloak_id
            
        Returns:
            True if successful, False otherwise
        """
        if not user.keycloak_id:
            logger.error(f"User {user.username} has no Keycloak ID")
            return False
            
        # Get current Keycloak user data
        keycloak_user = self.keycloak_client.get_user_by_id(user.keycloak_id)
        if not keycloak_user:
            logger.error(f"User {user.username} not found in Keycloak with ID {user.keycloak_id}")
            return False
            
        # Split full name for Keycloak
        name_parts = (user.full_name or "").split(maxsplit=1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Prepare update data
        update_data = {}
        
        # Only update fields that have changed
        if user.email != keycloak_user.get('email'):
            update_data['email'] = user.email
            
        if first_name != keycloak_user.get('firstName', ''):
            update_data['firstName'] = first_name
            
        if last_name != keycloak_user.get('lastName', ''):
            update_data['lastName'] = last_name
            
        # If nothing to update, return early
        if not update_data:
            logger.info(f"No changes needed for user {user.username} in Keycloak")
            return True
            
        # Update Keycloak user
        success = self.keycloak_client.update_user(user.keycloak_id, update_data)
        if success:
            logger.info(f"Updated Keycloak user {user.username} with ID {user.keycloak_id}")
        
        return success
    
    def sync_user(self, user: User, two_way: bool = True) -> bool:
        """
        Synchronize a user between the local database and Keycloak
        
        Args:
            user: Local User model instance
            two_way: If True, sync both ways; if False, only sync from Keycloak to local
            
        Returns:
            True if successful, False otherwise
        """
        with self._sync_lock:
            if not user.keycloak_id:
                logger.warning(f"User {user.username} has no Keycloak ID, cannot sync")
                return False
                
            # First update local user from Keycloak
            local_update_success = self.update_local_user_from_keycloak(user)
            
            # If two-way sync is enabled, also update Keycloak from local
            if two_way and local_update_success:
                keycloak_update_success = self.update_keycloak_user_from_local(user)
                return keycloak_update_success
                
            return local_update_success
    
    def sync_all_users(self, two_way: bool = False, create_missing: bool = True) -> Tuple[int, int, int]:
        """
        Synchronize all users between the local database and Keycloak
        
        Args:
            two_way: If True, sync both ways; if False, only sync from Keycloak to local
            create_missing: If True, create users that exist in Keycloak but not locally
            
        Returns:
            Tuple of (total_processed, successful, failed)
        """
        with self._sync_lock:
            try:
                # Get all users from Keycloak
                keycloak_users = self.keycloak_client.get_all_users()
                
                # Track metrics
                total_processed = 0
                successful = 0
                failed = 0
                
                # Process each Keycloak user
                for kc_user in keycloak_users:
                    total_processed += 1
                    keycloak_id = kc_user.get('id')
                    
                    if not keycloak_id:
                        logger.error(f"Keycloak user missing ID field: {kc_user}")
                        failed += 1
                        continue
                        
                    # Find corresponding local user
                    local_user = User.query.filter_by(keycloak_id=keycloak_id).first()
                    
                    if local_user:
                        # Update existing user
                        if self.sync_user(local_user, two_way):
                            successful += 1
                        else:
                            failed += 1
                    elif create_missing:
                        # Import user from Keycloak
                        imported_user = self.import_user_from_keycloak(kc_user)
                        if imported_user:
                            successful += 1
                        else:
                            failed += 1
                    else:
                        # Skip creating missing users
                        logger.info(f"Skipping Keycloak user {kc_user.get('username')} (ID: {keycloak_id}) - not found locally")
                        
                # If two-way sync, also check for local users not in Keycloak
                if two_way:
                    # Get all keycloak IDs
                    keycloak_ids = {user.get('id') for user in keycloak_users if user.get('id')}
                    
                    # Find local users without a match in Keycloak
                    local_users_without_keycloak = User.query.filter(
                        (User.keycloak_id.is_(None)) | 
                        (User.keycloak_id.notin_(keycloak_ids))
                    ).all()
                    
                    # Warn about users that exist locally but not in Keycloak
                    for user in local_users_without_keycloak:
                        logger.warning(f"Local user {user.username} (ID: {user.user_id}) not found in Keycloak")
                        
                return total_processed, successful, failed
                
            except Exception as e:
                logger.error(f"Error during user synchronization: {e}")
                return 0, 0, 0
    
    def find_user_by_credentials(self, username: str, email: str = None) -> Optional[User]:
        """
        Find a user by credentials, checking both local database and Keycloak
        
        Args:
            username: Username to look up
            email: Email to look up (optional)
            
        Returns:
            User model instance if found, None otherwise
        """
        # First check local database
        local_user = User.query.filter_by(username=username).first()
        if local_user:
            return local_user
            
        if email:
            local_user = User.query.filter_by(email=email).first()
            if local_user:
                return local_user
                
        # If not found locally, check Keycloak
        keycloak_user = self.keycloak_client.get_user_by_username(username)
        if not keycloak_user and email:
            keycloak_user = self.keycloak_client.get_user_by_email(email)
            
        if keycloak_user:
            # Import the user from Keycloak
            imported_user = self.import_user_from_keycloak(keycloak_user)
            return imported_user
            
        return None
    
    def schedule_periodic_sync(self, interval_seconds: int = 3600, two_way: bool = False, create_missing: bool = True):
        """
        Schedule periodic synchronization between local database and Keycloak
        
        Args:
            interval_seconds: Interval between synchronization runs in seconds
            two_way: If True, sync both ways; if False, only sync from Keycloak to local
            create_missing: If True, create users that exist in Keycloak but not locally
        """
        def sync_job():
            while True:
                logger.info(f"Starting scheduled user synchronization (two_way={two_way}, create_missing={create_missing})")
                try:
                    total, success, failed = self.sync_all_users(two_way, create_missing)
                    logger.info(f"Scheduled sync completed: {total} processed, {success} successful, {failed} failed")
                except Exception as e:
                    logger.error(f"Error during scheduled synchronization: {e}")
                    
                time.sleep(interval_seconds)
                
        # Start the sync thread
        sync_thread = threading.Thread(target=sync_job, daemon=True)
        sync_thread.start()
        
        logger.info(f"Scheduled user synchronization every {interval_seconds} seconds")