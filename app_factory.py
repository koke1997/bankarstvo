# app_factory.py
import logging
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from flask import Flask, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO

# Updated imports for new architecture
from utils.extensions import create_extensions, db, bcrypt, login_manager
from infrastructure.auth.keycloak_client import KeycloakOpenID  # Will be moved to this location

# Register the new app paths
PROJECT_ROOT = Path(__file__).parent.absolute()
for directory in ['api', 'core', 'database', 'infrastructure', 'utils', 'web']:
    sys.path.append(str(PROJECT_ROOT / directory))

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    # --- Configure Logging ---
    configure_logging(app)
    
    # --- Basic App Configuration ---
    app.static_folder = "static"
    app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI",
                                                     f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- Testing Configuration ---
    configure_test_environment(app)
    
    # --- Initialize Extensions ---
    create_extensions(app)
    socketio.init_app(app)

    # --- Set up Login Manager ---
    configure_login_manager(app)
    
    # --- Initialize Keycloak ---
    if not app.config.get("SKIP_KEYCLOAK", False):
        configure_keycloak(app)

    # --- Register Blueprints ---
    register_blueprints(app)

    # --- Enable CORS support ---
    CORS(app)

    # --- Register Error Handlers ---
    register_error_handlers(app)

    return app


def configure_logging(app):
    """Configure application logging."""
    # Updated path to config file
    config_path = os.path.join('config', 'logging.conf')
    if os.path.exists(config_path):
        fileConfig(config_path)
    else:
        # Fallback to original path during transition
        fileConfig(os.path.join('configuration', 'logging.conf'))

    # Set up a separate logger
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Write a test log message
    logger.info('App started with new architecture')
    
    # Set logging level to WARNING (or higher) to reduce log messages
    log_handler = logging.StreamHandler()
    log_handler.setLevel(logging.DEBUG)  # Change to WARNING if needed
    logger.addHandler(log_handler)

    # Configure module loggers
    configure_module_loggers(logger)


def configure_module_loggers(logger):
    """Configure loggers for specific modules."""
    # Updated module paths for new architecture
    modules = [
        'werkzeug',
        'database.repositories.connection',
        'web.account.dashboard',
        'database.repositories.auth_repo',
        'database.repositories.user_repo',
        'core.services.transaction_service',
    ]
    
    for module in modules:
        module_logger = logging.getLogger(module)
        module_logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s - %(message)s'))
            module_logger.addHandler(handler)


def configure_test_environment(app):
    """Configure application for testing if needed."""
    if app.config.get("TESTING") or "pytest" in sys.modules:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        # Skip Keycloak setup in test mode
        app.config["SKIP_KEYCLOAK"] = True


def configure_login_manager(app):
    """Configure Flask-Login."""
    # Updated endpoint for user routes
    login_manager.login_view = "user.login"  # Updated from "user_routes.login"
    login_manager.login_message_category = "info"


def configure_keycloak(app):
    """Configure Keycloak integration."""
    logger = logging.getLogger('root')
    
    # Load Keycloak configuration from environment variables
    keycloak_config = {
        "realm": os.getenv("KEYCLOAK_REALM", "bankarstvo"),
        "auth-server-url": os.getenv("KEYCLOAK_AUTH_SERVER_URL", "http://localhost:3790/auth"),
        "ssl-required": os.getenv("KEYCLOAK_SSL_REQUIRED", "external"),
        "resource": os.getenv("KEYCLOAK_RESOURCE", "bankarstvo-client"),
        "credentials": {
            "secret": os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")
        },
        "confidential-port": int(os.getenv("KEYCLOAK_CONFIDENTIAL_PORT", 0))
    }

    # Initialize Keycloak client
    try:
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_config["auth-server-url"],
            client_id=keycloak_config["resource"],
            realm_name=keycloak_config["realm"],
            client_secret_key=keycloak_config["credentials"]["secret"]
        )
        app.config["KEYCLOAK_OPENID"] = keycloak_openid
    except Exception as e:
        logger.warning(f"Error initializing Keycloak: {e}")
        if not app.debug:
            logger.error("Failed to initialize Keycloak in production mode")


def register_blueprints(app):
    """Register all application blueprints."""
    # Updated imports for new architecture
    from web.transaction.routes import transaction_bp
    from web.account.routes import account_bp
    from web.user.routes import user_bp
    
    # These imports will be adapted during the transition
    # Make sure to import from the new locations once files are moved
    try:
        # Try new structure imports first
        from web.search.routes import search_bp
        from web.logger.routes import log_bp
        from web.crypto.routes import crypto_bp
        from web.stock.routes import stock_bp
        from web.marketplace.routes import marketplace_bp
    except ImportError:
        # Fall back to old structure during transition
        from routes.search_routes.search import search_routes as search_bp
        from routes.logger_routes.log_routes import log_routes as log_bp
        from routes.transaction_routes.crypto import crypto_routes as crypto_bp
        from routes.transaction_routes.stock import stock_routes as stock_bp
        from routes.marketplace_routes import marketplace_routes as marketplace_bp

    # Register blueprints with new names and URL prefixes
    blueprints = [
        {"bp": transaction_bp, "url_prefix": "/transaction"},
        {"bp": account_bp, "url_prefix": "/account"},
        {"bp": user_bp, "url_prefix": "/user"},
        {"bp": search_bp, "url_prefix": "/search"},
        {"bp": log_bp, "url_prefix": "/logs"},
        {"bp": crypto_bp, "url_prefix": "/crypto"},
        {"bp": stock_bp, "url_prefix": "/stock"},
        {"bp": marketplace_bp, "url_prefix": "/marketplace"},
    ]
    
    for blueprint in blueprints:
        bp = blueprint["bp"]
        url_prefix = blueprint["url_prefix"]
        
        # Use the provided URL prefix if the blueprint doesn't already have one
        if not getattr(bp, "url_prefix", None):
            app.register_blueprint(bp, url_prefix=url_prefix)
        else:
            app.register_blueprint(bp)

    # Log blueprint registration
    logger = logging.getLogger('root')
    logger.info("\nRegistered Blueprints:")
    for blueprint in blueprints:
        bp = blueprint["bp"]
        prefix = getattr(bp, "url_prefix", None) or blueprint["url_prefix"]
        logger.info(f"• {bp.name} -> {prefix}")
    
    # Log all application routes
    logger.info("\nAll Application Routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"• {rule}")


def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(404)
    def page_not_found(e):
        # Log available URLs
        available_urls = [rule.rule for rule in app.url_map.iter_rules()]
        logging.error(
            f"404 Not Found: {request.url}. The requested URL was not found on the server. Available URLs: {available_urls}")

        # Render the error page
        return render_template("error.html",
                               error_message=f"404 Not Found: {request.url}. The requested URL was not found on the server. If you entered the URL manually, please check your spelling and try again."), 404

    @app.errorhandler(401)
    def unauthorized_error(e):
        logging.error(f"Unauthorized access attempt: {request.url}")
        return render_template("error.html", error_message="401 Unauthorized: Access is denied."), 401

    @app.errorhandler(403)
    def forbidden_error(e):
        logging.error(f"Forbidden access attempt: {request.url}")
        return render_template("error.html", error_message="403 Forbidden: You do not have permission to access this resource."), 403

    @app.errorhandler(Exception)
    def log_error(exception):
        # Get the exception details
        error_message = str(exception)

        # Render the error template with the error message
        return render_template("error.html", error_message=error_message), 500
