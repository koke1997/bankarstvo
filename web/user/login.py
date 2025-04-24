# user_routes/login.py

from flask import request, flash, redirect, url_for, render_template, session
import logging
import os
from flask_login import login_user
from utils.extensions import db, bcrypt
from core.models import User
import traceback

# Set up detailed logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configure Keycloak if available
try:
    from keycloak import KeycloakOpenID
    keycloak_available = True
    keycloak_openid = KeycloakOpenID(
        server_url=os.getenv("KEYCLOAK_AUTH_SERVER_URL", "http://localhost:3790/auth"),
        client_id=os.getenv("KEYCLOAK_RESOURCE", "bankarstvo-client"),
        realm_name=os.getenv("KEYCLOAK_REALM", "bankarstvo"),
        client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    )
except ImportError:
    logger.warning("Keycloak module not available. Using form-based authentication only.")
    keycloak_available = False

def db_available():
    """Check if database is available."""
    try:
        result = db.session.query(User).limit(1).all()
        logger.debug(f"Database check successful, found {len(result)} users")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        logger.error(traceback.format_exc())
        return False

def login():
    """Handle user login through form or Keycloak."""
    # Log all request information
    logger.debug(f"Login request: Method={request.method}, Path={request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    # If already logged in, go to dashboard
    if 'user_id' in session:
        logger.debug(f"Already logged in, redirecting to dashboard. Session: {session}")
        return redirect(url_for("account_routes.dashboard"))
    
    # Handle GET request - show login form
    if request.method == 'GET':
        logger.debug("Showing login form")
        return render_template('login.html')
    
    # Handle POST request - process form login
    if request.method == 'POST':
        # Log all form data (except password)
        form_data = {k: v for k, v in request.form.items() if k != 'password'}
        logger.debug(f"Login form submitted: {form_data}")
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        if not username or not password:
            logger.warning(f"Missing login credentials: username={bool(username)}, password={bool(password)}")
            flash("Please provide both username and password", "danger")
            return render_template('login.html')
        
        # Attempt database login
        if db_available():
            try:
                logger.debug(f"Attempting to find user: {username}")
                user_data = db.session.query(User).filter_by(username=username).first()
                
                if user_data:
                    logger.debug(f"User found: id={user_data.user_id}, username={user_data.username}")
                    
                    # Check if password hash exists
                    if not hasattr(user_data, 'password_hash') or not user_data.password_hash:
                        logger.error(f"User {username} has no password hash")
                        flash("Account error. Please contact support.", "danger")
                        return render_template('login.html')
                    
                    # Verify password
                    if bcrypt.check_password_hash(user_data.password_hash, password):
                        logger.debug(f"Password verified for user {username}")
                        
                        # Login user
                        login_user(user_data)
                        session['user_id'] = user_data.user_id
                        session['username'] = user_data.username
                        
                        logger.info(f"User {username} logged in successfully. Session: {session}")
                        flash("Logged in successfully!", "success")
                        
                        # Log the redirect destination
                        dashboard_url = url_for("account_routes.dashboard")
                        logger.debug(f"Redirecting to: {dashboard_url}")
                        return redirect(dashboard_url)
                    else:
                        logger.warning(f"Invalid password for user {username}")
                else:
                    logger.warning(f"User not found: {username}")
            except Exception as e:
                logger.error(f"Error during login process: {str(e)}")
                logger.error(traceback.format_exc())
        else:
            logger.error("Database not available during login attempt")
        
        # Login failed
        flash("Invalid username or password", "danger")
        return render_template('login.html')

def callback():
    """Handle Keycloak callback."""
    logger.debug(f"Callback request: {request.args}")
    flash("Authentication service callback received but not configured.", "warning")
    return redirect(url_for("user_routes.login"))
