"""
User synchronization service between local database and Keycloak
"""
import logging
from typing import Optional, Dict, Any, List, Tuple
from flask import current_app

from core.models import User
from utils.extensions import db, bcrypt
from infrastructure.auth.keycloak_client import KeycloakClient

logger = logging.getLogger(__name__)

class UserSyncService:
    """Service for synchronizing users between the local database and Keycloak"""
    
    @staticmethod
    def get_keycloak_client() -> Optional[KeycloakClient]:
        """Get the Keycloak client from the Flask app config"""
        try:
            return current_app.config.get("KEYCLOAK_CLIENT")
        except Exception as e:
            logger.error(f"Error getting Keycloak client: {e}")
            return None
    
    @classmethod
    def create_user_in_keycloak(cls, user: User, password: str) -> Optional[str]:
        """
        Create a user in Keycloak.
        
        Args:
            user: User model instance
            password: Clear-text password (only used for Keycloak, not stored in database)
            
        Returns:
            Keycloak user ID if successful, None otherwise
        """
        keycloak_client = cls.get_keycloak_client()
        if not keycloak_client:
            logger.warning("Cannot create user in Keycloak: client not available")
            return None
        
        try:
            # Split full name into first and last name if available
            first_name, last_name = "", ""
            if user.full_name:
                name_parts = user.full_name.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Additional attributes to store
            attributes = {
                "db_user_id": [str(user.user_id)]
            }
            
            # Create user in Keycloak
            user_id = keycloak_client.create_user(
                username=user.username,
                email=user.email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                attributes=attributes
            )
            
            if user_id:
                # Update local user with Keycloak ID
                user.keycloak_id = user_id
                db.session.commit()
                logger.info(f"Created user {user.username} in Keycloak with ID {user_id}")
                return user_id
            
            return None
        except Exception as e:
            logger.error(f"Error creating user {user.username} in Keycloak: {e}")
            return None
    
    @classmethod
    def update_user_in_keycloak(cls, user: User) -> bool:
        """
        Update a user in Keycloak with data from the local database.
        
        Args:
            user: User model instance
            
        Returns:
            True if successful, False otherwise
        """
        if not user.keycloak_id:
            logger.warning(f"Cannot update user {user.username} in Keycloak: no Keycloak ID")
            return False
            
        keycloak_client = cls.get_keycloak_client()
        if not keycloak_client:
            logger.warning("Cannot update user in Keycloak: client not available")
            return False
        
        try:
            # Split full name into first and last name if available
            first_name, last_name = "", ""
            if user.full_name:
                name_parts = user.full_name.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Additional attributes to store
            attributes = {
                "db_user_id": [str(user.user_id)]
            }
            
            # Update user data in Keycloak
            updated = keycloak_client.update_user(
                user_id=user.keycloak_id,
                email=user.email,
                first_name=first_name,
                last_name=last_name,
                attributes=attributes
            )
            
            if updated:
                logger.info(f"Updated user {user.username} in Keycloak")
                return True
            
            logger.warning(f"Failed to update user {user.username} in Keycloak")
            return False
        except Exception as e:
            logger.error(f"Error updating user {user.username} in Keycloak: {e}")
            return False
    
    @classmethod
    def import_user_from_keycloak(cls, username: str) -> Optional[User]:
        """
        Import a user from Keycloak to the local database.
        
        Args:
            username: Username of the user to import
            
        Returns:
            User model instance if successful, None otherwise
        """
        keycloak_client = cls.get_keycloak_client()
        if not keycloak_client:
            logger.warning("Cannot import user from Keycloak: client not available")
            return None
        
        try:
            # Get user data from Keycloak
            kc_user = keycloak_client.get_user_by_username(username)
            if not kc_user:
                logger.warning(f"User {username} not found in Keycloak")
                return None
            
            # Check if user already exists in database
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                # Update existing user with Keycloak ID if not already set
                if not existing_user.keycloak_id:
                    existing_user.keycloak_id = kc_user["id"]
                    db.session.commit()
                    logger.info(f"Updated existing user {username} with Keycloak ID {kc_user['id']}")
                return existing_user
            
            # Create new user in database
            email = kc_user.get("email", "")
            first_name = kc_user.get("firstName", "")
            last_name = kc_user.get("lastName", "")
            full_name = f"{first_name} {last_name}".strip()
            
            # Create a temporary password hash (user will need to reset password when logging in directly to app)
            temp_password_hash = bcrypt.generate_password_hash("temp_password").decode('utf-8')
            
            new_user = User(
                username=username,
                email=email,
                password_hash=temp_password_hash,
                full_name=full_name,
                keycloak_id=kc_user["id"]
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"Imported user {username} from Keycloak to database with ID {new_user.user_id}")
            return new_user
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error importing user {username} from Keycloak: {e}")
            return None
    
    @classmethod
    def sync_all_users_from_keycloak(cls) -> Tuple[int, int, int]:
        """
        Synchronize all users from Keycloak to the local database.
        
        Returns:
            Tuple of (total_users, success_count, error_count)
        """
        keycloak_client = cls.get_keycloak_client()
        if not keycloak_client:
            logger.warning("Cannot sync users from Keycloak: client not available")
            return (0, 0, 0)
        
        try:
            # Get all users from Keycloak
            kc_users = keycloak_client.get_all_users()
            
            total = len(kc_users)
            success = 0
            errors = 0
            
            logger.info(f"Syncing {total} users from Keycloak to database")
            
            for kc_user in kc_users:
                try:
                    username = kc_user.get("username")
                    if not username:
                        logger.warning(f"Skipping Keycloak user without username: {kc_user.get('id')}")
                        errors += 1
                        continue
                    
                    # Check if user already exists in database
                    existing_user = User.query.filter_by(username=username).first()
                    
                    if existing_user:
                        # Update Keycloak ID if needed
                        if not existing_user.keycloak_id:
                            existing_user.keycloak_id = kc_user["id"]
                            db.session.commit()
                            logger.info(f"Updated existing user {username} with Keycloak ID {kc_user['id']}")
                    else:
                        # Create new user in database
                        email = kc_user.get("email", "")
                        first_name = kc_user.get("firstName", "")
                        last_name = kc_user.get("lastName", "")
                        full_name = f"{first_name} {last_name}".strip()
                        
                        # Create a temporary password hash (user will need to reset password)
                        temp_password_hash = bcrypt.generate_password_hash("temp_password").decode('utf-8')
                        
                        new_user = User(
                            username=username,
                            email=email,
                            password_hash=temp_password_hash,
                            full_name=full_name,
                            keycloak_id=kc_user["id"]
                        )
                        
                        db.session.add(new_user)
                        db.session.commit()
                        
                        logger.info(f"Imported user {username} from Keycloak to database with ID {new_user.user_id}")
                    
                    success += 1
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error syncing Keycloak user {kc_user.get('username', kc_user.get('id'))}: {e}")
                    errors += 1
            
            logger.info(f"Keycloak sync complete: {success} users synced successfully, {errors} errors")
            return (total, success, errors)
        except Exception as e:
            logger.error(f"Error syncing users from Keycloak: {e}")
            return (0, 0, 0)
            
    @classmethod
    def export_all_users_to_keycloak(cls, default_password="TemporaryPassword123") -> Tuple[int, int, int]:
        """
        Export all users from the local database to Keycloak.
        Note: This method requires setting temporary passwords for users.
        
        Args:
            default_password: Default password to set for users in Keycloak
            
        Returns:
            Tuple of (total_users, success_count, error_count)
        """
        # Get users that don't have a Keycloak ID
        users_to_export = User.query.filter(User.keycloak_id.is_(None)).all()
        
        total = len(users_to_export)
        success = 0
        errors = 0
        
        logger.info(f"Exporting {total} users from database to Keycloak")
        
        for user in users_to_export:
            try:
                keycloak_id = cls.create_user_in_keycloak(user, default_password)
                if keycloak_id:
                    success += 1
                else:
                    errors += 1
            except Exception as e:
                logger.error(f"Error exporting user {user.username} to Keycloak: {e}")
                errors += 1
        
        logger.info(f"Database export complete: {success}/{total} users exported successfully, {errors} errors")
        return (total, success, errors)
        
    @classmethod
    def sync_user_changes_to_keycloak(cls) -> Tuple[int, int, int]:
        """
        Synchronize changes to existing users from the local database to Keycloak.
        
        Returns:
            Tuple of (total_users, success_count, error_count)
        """
        # Get users that have a Keycloak ID
        users_to_sync = User.query.filter(User.keycloak_id.isnot(None)).all()
        
        total = len(users_to_sync)
        success = 0
        errors = 0
        
        logger.info(f"Syncing {total} users from database to Keycloak")
        
        for user in users_to_sync:
            try:
                updated = cls.update_user_in_keycloak(user)
                if updated:
                    success += 1
                else:
                    errors += 1
            except Exception as e:
                logger.error(f"Error syncing user {user.username} to Keycloak: {e}")
                errors += 1
        
        logger.info(f"Database sync complete: {success}/{total} users synced successfully, {errors} errors")
        return (total, success, errors)