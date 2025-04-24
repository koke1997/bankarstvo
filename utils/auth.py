# utils/auth.py
import os
import logging

from utils.extensions import login_manager


def configure_login_manager(app):
    """Configure Flask-Login."""
    login_manager.init_app(app)
    login_manager.login_view = "user_bp.login"
    login_manager.login_message_category = "info"
    login_manager.login_message = "Please log in to access this page."
    
    @login_manager.user_loader
    def load_user(user_id):
        # Import here to avoid circular imports
        from database.models.user import User
        return User.query.get(int(user_id))


def configure_keycloak(app):
    """Configure Keycloak integration."""
    logger = app.logger
    
    # Handle KeycloakOpenID import with graceful fallback if not available
    try:
        from infrastructure.auth.keycloak_client import KeycloakClient
        keycloak_import_success = True
    except ImportError:
        keycloak_import_success = False
        logger.error("Keycloak client module not found. Authentication will be disabled.")
        return False
    
    # Load Keycloak configuration
    keycloak_config = {
        "realm": os.getenv("KEYCLOAK_REALM", "bankarstvo"),
        "server_url": os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/auth"),
        "client_id": os.getenv("KEYCLOAK_CLIENT_ID", "bankarstvo-client"),
        "client_secret": os.getenv("KEYCLOAK_CLIENT_SECRET", ""),
        "verify": os.getenv("KEYCLOAK_VERIFY_SSL", "true").lower() == "true"
    }

    # Initialize Keycloak client
    try:
        keycloak_client = KeycloakClient(**keycloak_config)
        app.config["KEYCLOAK_CLIENT"] = keycloak_client
        logger.info(f"Initialized Keycloak client for realm {keycloak_config['realm']}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Keycloak: {e}")
        if not app.debug:
            logger.critical("Keycloak initialization failed in production mode")
        return False