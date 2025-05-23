import traceback
import pyotp
# Fix the import to use the external package instead of local module
from keycloak import KeycloakOpenID  # Changed from 'keycloak' to 'python_keycloak'
import os

#DatabaseHandling/authentication.py
from utils.extensions import bcrypt
from core.models import User
from flask_login import login_user, logout_user
from flask import session
from .session_clearing  import clear_session
import logging
logger = logging.getLogger(__name__)

keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_SERVER_URL"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    realm_name=os.getenv("KEYCLOAK_REALM_NAME"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET_KEY")
)

def login_func(username, password, otp_code=None):
    try:
        logger.info(f"Attempting to log in with username {username} and password {password}")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if user.two_factor_auth:
                if otp_code is None:
                    logger.warning("OTP code is required for users with two-factor authentication enabled")
                    return False
                totp = pyotp.TOTP(user.two_factor_auth_secret)
                if not totp.verify(otp_code):
                    logger.warning("Invalid OTP code")
                    return False
            login_user(user)
            logger.info("Login successful")
            return True
        else:
            logger.warning("Login failed")
            return False
    except Exception as e:
        logger.exception(f"An error occurred during login: {e}")
        traceback.print_exc()
        return False

def logout_func():
    clear_session()
    logout_user()

def verify_user_credentials(username, password):
    """
    Verify user credentials and return the user object if valid.
    
    Args:
        username: The username to verify
        password: The password to check
        
    Returns:
        User object if credentials are valid, None otherwise
    """
    try:
        # Find the user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        
        return None
    except Exception as e:
        logger.exception(f"Error verifying user credentials: {e}")
        return None
