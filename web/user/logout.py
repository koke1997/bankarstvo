import os
from flask import redirect, url_for, session, flash
from flask_login import logout_user
import logging
from . import user_routes
from utils.extensions import token_required

logger = logging.getLogger(__name__)

# Create a Keycloak client using the environment variables from docker-compose.yml
try:
    # Import inside the try block to handle potential missing module gracefully
    from keycloak_realm_configs import KeycloakOpenID
    keycloak_openid = KeycloakOpenID(
        server_url=os.getenv("KEYCLOAK_AUTH_SERVER_URL", "http://localhost:3790/auth"),
        client_id=os.getenv("KEYCLOAK_RESOURCE", "bankarstvo-client"),
        realm_name=os.getenv("KEYCLOAK_REALM", "bankarstvo"),
        client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")
    )
    keycloak_available = True
except ImportError:
    logger.warning("Keycloak module not installed, SSO logout won't be available")
    keycloak_available = False
    # Define a complete dummy class to avoid Pylance errors
    class KeycloakOpenID:
        def __init__(self, server_url=None, client_id=None, realm_name=None, client_secret_key=None):
            self.server_url = server_url
            self.client_id = client_id
            self.realm_name = realm_name
            self.client_secret_key = client_secret_key
        
        def logout(self, refresh_token=None):
            # Dummy method for Pylance compatibility
            logger.debug("Mock Keycloak logout called")
            return True
            
    keycloak_openid = KeycloakOpenID(
        server_url=os.getenv("KEYCLOAK_AUTH_SERVER_URL", "http://localhost:3790/auth"),
        client_id=os.getenv("KEYCLOAK_RESOURCE", "bankarstvo-client"),
        realm_name=os.getenv("KEYCLOAK_REALM", "bankarstvo")
    )
except Exception as e:
    logger.warning(f"Keycloak configuration error: {e}")
    keycloak_available = False
    # Reuse the KeycloakOpenID class from above to avoid redeclaration
    if 'KeycloakOpenID' not in locals():
        class KeycloakOpenID:
            def __init__(self, server_url=None, client_id=None, realm_name=None, client_secret_key=None):
                self.server_url = server_url
                self.client_id = client_id
                self.realm_name = realm_name
                self.client_secret_key = client_secret_key
            
            def logout(self, refresh_token=None):
                # Dummy method for Pylance compatibility
                logger.debug("Mock Keycloak logout called")
                return True
                
    keycloak_openid = KeycloakOpenID(
        server_url=os.getenv("KEYCLOAK_AUTH_SERVER_URL", "http://localhost:3790/auth"),
        client_id=os.getenv("KEYCLOAK_RESOURCE", "bankarstvo-client"),
        realm_name=os.getenv("KEYCLOAK_REALM", "bankarstvo")
    )

@user_routes.route('/logout', methods=['GET'], endpoint="logout")
@token_required
def logout():
    """Handle user logout with fallbacks for both database and Keycloak issues."""
    try:
        # Clear Flask-Login session
        logout_user()
    except Exception as e:
        logger.warning(f"Error during Flask-Login logout: {e}")
    
    # Clear our custom session data
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('access_token', None)
    session.pop('selected_account_id', None)
    
    # Try to logout from Keycloak if available
    if keycloak_available and session.get('access_token'):
        try:
            # If we have a refresh token, use it to logout from Keycloak
            if session.get('refresh_token'):
                keycloak_openid.logout(session['refresh_token'])
            # Otherwise try a direct logout
            else:
                keycloak_openid.logout()
        except Exception as e:
            logger.warning(f"Error during Keycloak logout: {e}")
    
    flash("You have been logged out successfully", "success")
    return redirect(url_for('user_routes.login'))
