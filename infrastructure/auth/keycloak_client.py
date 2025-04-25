"""
Keycloak client implementation for authentication and user management
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any

from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakError

logger = logging.getLogger(__name__)

class KeycloakClient:
    """
    Client for interacting with Keycloak
    """
    def __init__(self, server_url: str, realm_name: str, client_id: str, client_secret: str = None):
        """
        Initialize the Keycloak client
        
        Args:
            server_url: Keycloak server URL
            realm_name: Realm name
            client_id: Client ID
            client_secret: Client secret (optional)
        """
        self.server_url = server_url
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Configure the OpenID client for authentication
        self.keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret_key=client_secret
        )
        
        # Configure the Admin client for user management
        self.keycloak_admin = self._get_admin_client()
        
    def _get_admin_client(self) -> KeycloakAdmin:
        """
        Create a Keycloak admin client for user management operations
        
        Returns:
            KeycloakAdmin instance
        """
        try:
            # Try to use client credentials if available
            if self.client_secret:
                return KeycloakAdmin(
                    server_url=self.server_url,
                    realm_name=self.realm_name,
                    client_id=self.client_id,
                    client_secret_key=self.client_secret,
                    verify=True
                )
            else:
                # If no client secret, use admin credentials from environment
                admin_username = os.environ.get('KEYCLOAK_ADMIN', 'admin')
                admin_password = os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'admin')
                
                return KeycloakAdmin(
                    server_url=self.server_url,
                    username=admin_username,
                    password=admin_password,
                    realm_name=self.realm_name,
                    verify=True
                )
        except KeycloakError as e:
            logger.error(f"Failed to initialize Keycloak admin client: {e}")
            raise
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user with username and password
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Dict with token information if successful, None otherwise
        """
        try:
            token = self.keycloak_openid.token(username, password)
            user_info = self.keycloak_openid.userinfo(token['access_token'])
            return {
                'access_token': token['access_token'],
                'refresh_token': token['refresh_token'],
                'user_info': user_info
            }
        except KeycloakError as e:
            logger.error(f"Authentication failed for user {username}: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Get a user by username
        
        Args:
            username: Username to look up
            
        Returns:
            User data if found, None otherwise
        """
        try:
            users = self.keycloak_admin.get_users({"username": username})
            if users and len(users) > 0:
                return users[0]
            return None
        except KeycloakError as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get a user by email
        
        Args:
            email: Email to look up
            
        Returns:
            User data if found, None otherwise
        """
        try:
            users = self.keycloak_admin.get_users({"email": email})
            if users and len(users) > 0:
                return users[0]
            return None
        except KeycloakError as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Get a user by ID
        
        Args:
            user_id: Keycloak user ID
            
        Returns:
            User data if found, None otherwise
        """
        try:
            return self.keycloak_admin.get_user(user_id)
        except KeycloakError as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    def create_user(self, username: str, email: str, password: str, 
                   first_name: str = "", last_name: str = "", 
                   enabled: bool = True, attributes: Dict = None) -> Optional[str]:
        """
        Create a new user in Keycloak
        
        Args:
            username: Username for the new user
            email: Email for the new user
            password: Password for the new user
            first_name: First name
            last_name: Last name
            enabled: Whether the account is enabled
            attributes: Additional attributes
            
        Returns:
            User ID if created successfully, None otherwise
        """
        try:
            # Prepare user data
            user_data = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": enabled,
                "emailVerified": True
            }
            
            if attributes:
                user_data["attributes"] = attributes
                
            # Create the user
            user_id = self.keycloak_admin.create_user(user_data)
            
            # Set the password
            self.keycloak_admin.set_user_password(user_id, password, temporary=False)
            
            logger.info(f"Created user {username} with ID {user_id} in Keycloak")
            return user_id
            
        except KeycloakError as e:
            logger.error(f"Failed to create user {username}: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """
        Update a user in Keycloak
        
        Args:
            user_id: Keycloak user ID
            user_data: User data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.keycloak_admin.update_user(user_id, user_data)
            return True
        except KeycloakError as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from Keycloak
        
        Args:
            user_id: Keycloak user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.keycloak_admin.delete_user(user_id)
            return True
        except KeycloakError as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
    
    def get_all_users(self, max_users: int = 1000) -> List[Dict]:
        """
        Get all users from Keycloak
        
        Args:
            max_users: Maximum number of users to retrieve
            
        Returns:
            List of user data dictionaries
        """
        try:
            # Get users in batches to handle large user bases
            all_users = []
            first = 0
            count = 100  # Fetch 100 users per request
            
            while True:
                users = self.keycloak_admin.get_users({}, first=first, max=count)
                if not users:
                    break
                    
                all_users.extend(users)
                first += count
                
                if len(all_users) >= max_users:
                    all_users = all_users[:max_users]
                    break
            
            return all_users
        except KeycloakError as e:
            logger.error(f"Failed to get all users: {e}")
            return []
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """
        Get roles assigned to a user
        
        Args:
            user_id: Keycloak user ID
            
        Returns:
            List of role names
        """
        try:
            realm_roles = self.keycloak_admin.get_realm_roles_of_user(user_id)
            return [role['name'] for role in realm_roles]
        except KeycloakError as e:
            logger.error(f"Failed to get roles for user {user_id}: {e}")
            return []
    
    def add_user_to_role(self, user_id: str, role_name: str) -> bool:
        """
        Assign a role to a user
        
        Args:
            user_id: Keycloak user ID
            role_name: Role name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            role = self.keycloak_admin.get_realm_role(role_name)
            self.keycloak_admin.assign_realm_roles(user_id, [role])
            return True
        except KeycloakError as e:
            logger.error(f"Failed to add role {role_name} to user {user_id}: {e}")
            return False
            
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate an access token
        
        Args:
            token: Access token
            
        Returns:
            Token info if valid, None otherwise
        """
        try:
            return self.keycloak_openid.introspect(token)
        except KeycloakError as e:
            logger.error(f"Failed to validate token: {e}")
            return None
