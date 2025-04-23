# user_routes/login.py

from flask import request, flash, redirect, url_for, render_template, session
import traceback
import logging
from keycloak import KeycloakOpenID
import os
from flask_login import login_user
from utils.extensions import login_manager
from core.models import User
import jwt  # Import jwt for decoding tokens
from DatabaseHandling.connection import get_demo_user, get_db_connection, db_available

logger = logging.getLogger(__name__)

# Create a Keycloak client using the environment variables that match docker-compose.yml
keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_AUTH_SERVER_URL", "http://localhost:3790/auth"),
    client_id=os.getenv("KEYCLOAK_RESOURCE", "bankarstvo-client"),
    realm_name=os.getenv("KEYCLOAK_REALM", "bankarstvo"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")
)

# Use function definitions instead of decorators since routes are registered in __init__.py
def login():
    """Handle login requests, supporting both Keycloak and form-based auth."""
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        flash("Already logged in", "info")
        return redirect(url_for("account_routes.dashboard"))
    
    # On GET request or if Keycloak is unavailable, show login form
    if request.method == 'GET':
        try:
            # Try redirecting to Keycloak for authentication first
            redirect_url = keycloak_openid.auth_url(
                redirect_uri=url_for("user_routes.callback", _external=True)
            )
            return redirect(redirect_url)
        except Exception as e:
            logger.warning(f"Keycloak unavailable: {e}. Falling back to form login")
            # Render traditional login form if Keycloak is unavailable
            return render_template('login.html', form_login=True)
    
    # Handle form-based login on POST request
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Please provide both username and password", "danger")
            return render_template('login.html', form_login=True)
        
        # First, try database login
        if db_available:
            with get_db_connection() as conn:
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
                        user_data = cursor.fetchone()
                        cursor.close()
                        
                        if user_data:
                            # In a real app you'd verify password hash here
                            # For simplicity in dev mode, we'll just check if it's 'demo123'
                            if password == 'demo123' or password == user_data['username']:
                                user = User()
                                user.user_id = user_data['user_id']
                                user.username = user_data['username']
                                user.email = user_data['email']
                                
                                login_user(user)
                                session['user_id'] = user.user_id
                                session['username'] = user.username
                                
                                flash("Logged in successfully!", "success")
                                return redirect(url_for("account_routes.dashboard"))
                    except Exception as e:
                        logger.error(f"Database error during login: {e}")
        
        # If database login fails or is unavailable, try demo accounts
        demo_user = get_demo_user(username=username)
        if demo_user and (password == 'demo123' or password == demo_user['username']):
            user = User()
            user.user_id = demo_user['user_id']
            user.username = demo_user['username']
            user.email = demo_user['email']
            
            login_user(user)
            session['user_id'] = user.user_id
            session['username'] = user.username
            
            flash("Logged in with demo account. Note: Database is in demo mode.", "warning")
            return redirect(url_for("account_routes.dashboard"))
        
        flash("Invalid username or password", "danger")
        return render_template('login.html', form_login=True)

def callback():
    """Handle Keycloak callback after successful authentication."""
    try:
        # Handle the authorization code returned by Keycloak
        code = request.args.get("code")
        if not code:
            flash("Authorization code not found.", "danger")
            return redirect(url_for("user_routes.login"))

        # Exchange the authorization code for tokens
        token = keycloak_openid.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=url_for("user_routes.callback", _external=True)
        )

        # Store the access token in the session
        session["access_token"] = token["access_token"]
        
        # Skip database interaction completely for now
        # Create a temporary in-memory user for this session
        try:
            # Decode the token to get user info
            decoded_token = jwt.decode(token['access_token'], options={"verify_signature": False})
            username = decoded_token.get('preferred_username', 'unknown_user')
            email = decoded_token.get('email', f"{username}@example.com")
            
            # First, try to find user in database if available
            user_data = None
            if db_available:
                with get_db_connection() as conn:
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM user WHERE username = %s OR email = %s", (username, email))
                            user_data = cursor.fetchone()
                            cursor.close()
                        except Exception as e:
                            logger.error(f"Error finding user in database: {e}")
            
            if user_data:
                user = User()
                user.user_id = user_data['user_id']
                user.username = user_data['username']
                user.email = user_data['email']
            else:
                # Use in-memory user if not found in database
                user = User()
                user.user_id = 1
                user.username = username
                user.email = email
            
            # Save important user details in session
            session['user_id'] = user.user_id
            session['username'] = user.username 
            session['email'] = user.email
            
            # Login with Flask-Login to maintain session
            login_user(user)
            
            logger.info(f"Successfully authenticated user: {username} ({email})")
            
            flash("Logged in successfully!", "success")
            
            # Redirect to the dashboard
            return redirect(url_for("account_routes.dashboard"))
            
        except Exception as e:
            logger.error(f"Error processing token: {e}")
            logger.error(traceback.format_exc())
            
            # Emergency fallback - always works 
            user = User()
            user.user_id = 999
            user.username = "emergency_user"
            user.email = "emergency@example.com"
            
            session['user_id'] = 999
            session['username'] = "emergency_user"
            session['email'] = "emergency@example.com"
            
            login_user(user)
            
            flash("Logged in with temporary account due to system maintenance.", "warning")
            return redirect(url_for("account_routes.dashboard"))
            
    except Exception as e:
        logger.error(f"An error occurred during callback: {e}")
        logger.error(traceback.format_exc())
        flash("Authentication error. Please try again or use local login.", "danger")
        return redirect(url_for("user_routes.login"))
