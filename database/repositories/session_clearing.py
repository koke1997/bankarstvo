# session_clearing.py - Handles session clearing functionality
from flask import session

def clear_session():
    """
    Clear all session data when a user logs out.
    This helps prevent session data leakage between different user sessions.
    """
    # Clear all keys from the session
    session.clear()