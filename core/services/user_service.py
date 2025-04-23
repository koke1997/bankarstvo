# User service - contains business logic for user operations
import logging
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

# Import repositories
from database.repositories.auth_repo import verify_user_credentials
from database.repositories.user_repo import create_user, get_user_by_id, update_user

# Import models
from core.models.user import User

logger = logging.getLogger(__name__)

def authenticate_user(username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
    """
    Authenticate a user with the given credentials.
    
    Args:
        username: The username to authenticate
        password: The password to verify
        
    Returns:
        Tuple containing (User object or None, Error message or None)
    """
    try:
        # Use repository layer to verify credentials
        user = verify_user_credentials(username, password)
        
        if user:
            # Update last login time
            user.last_login = datetime.now()
            update_user(user)
            return user, None
        
        return None, "Invalid username or password"
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None, f"Authentication error: {str(e)}"

def register_new_user(username: str, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
    """
    Register a new user.
    
    Args:
        username: The username for the new user
        email: The email for the new user
        password: The password for the new user
        
    Returns:
        Tuple containing (User object or None, Error message or None)
    """
    try:
        # Basic validation
        if not username or not email or not password:
            return None, "All fields are required"
            
        if len(password) < 8:
            return None, "Password must be at least 8 characters long"
            
        # Use repository layer to create user
        user = create_user(username, email, password)
        return user, None
    except ValueError as e:
        return None, str(e)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return None, f"Registration error: {str(e)}"

def get_user_profile(user_id: int) -> Dict[str, Any]:
    """
    Get user profile information.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dictionary with user profile information
    """
    try:
        # Get user from repository
        user = get_user_by_id(user_id)
        
        if not user:
            return {"error": "User not found"}
            
        # Return profile information
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "account_created": user.account_created,
            "last_login": user.last_login,
            "two_factor_auth": user.two_factor_auth
        }
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        return {"error": f"Error retrieving user profile: {str(e)}"}

def update_user_profile(user_id: int, profile_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Update user profile information.
    
    Args:
        user_id: The ID of the user
        profile_data: Dictionary with fields to update
        
    Returns:
        Tuple containing (Success boolean, Error message or None)
    """
    try:
        # Get user from repository
        user = get_user_by_id(user_id)
        
        if not user:
            return False, "User not found"
            
        # Update user fields
        for key, value in profile_data.items():
            if hasattr(user, key) and key not in ['user_id', 'password_hash']:
                setattr(user, key, value)
                
        # Save changes
        update_user(user)
        return True, None
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return False, f"Error updating user profile: {str(e)}"