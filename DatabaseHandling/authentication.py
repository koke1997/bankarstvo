import traceback

#DatabaseHandling/authentication.py
from utils.extensions import bcrypt
from core.models import User
from flask_login import login_user, logout_user
from flask import session
from .session_clearing  import clear_session
import logging
logger = logging.getLogger(__name__)

def login_func(username, password):
    try:
        logger.info(f"Attempting to log in with username {username} and password {password}")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
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