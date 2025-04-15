# app_factory.py
import logging
import os
from logging.config import fileConfig

from flask import Flask, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO

from utils.extensions import create_extensions, db, bcrypt, login_manager
from keycloak import KeycloakOpenID

socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    # Load the logging configuration
    fileConfig(os.path.join('configuration', 'logging.conf'))

    # Set up a separate logger
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Write a test log message
    logger.info('App started')

    app.static_folder = "static"

    # Configuration settings
    app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI",
                                                      f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if app.config["TESTING"]:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    create_extensions(app)
    socketio.init_app(app)

    login_manager.login_view = "user_routes.login"
    login_manager.login_message_category = "info"

    # Load Keycloak configuration from environment variables
    keycloak_config = {
        "realm": os.getenv("KEYCLOAK_REALM", "bankarstvo"),
        "auth-server-url": os.getenv("KEYCLOAK_AUTH_SERVER_URL", "http://localhost:8080/auth"),
        "ssl-required": os.getenv("KEYCLOAK_SSL_REQUIRED", "external"),
        "resource": os.getenv("KEYCLOAK_RESOURCE", "bankarstvo-client"),
        "credentials": {
            "secret": os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")
        },
        "confidential-port": int(os.getenv("KEYCLOAK_CONFIDENTIAL_PORT", 0))
    }

    # Initialize Keycloak client
    keycloak_openid = KeycloakOpenID(
        server_url=keycloak_config["auth-server-url"],
        client_id=keycloak_config["resource"],
        realm_name=keycloak_config["realm"],
        client_secret_key=keycloak_config["credentials"]["secret"]
    )

    # Register Blueprints
    from routes.transaction_routes import transaction_routes
    from routes.account_routes import account_routes
    from routes.user_routes import user_routes
    from routes.search_routes.search import search_routes  # Import the search_routes blueprint
    from routes.logger_routes.log_routes import log_routes
    from routes.transaction_routes.crypto import crypto_routes
    from routes.transaction_routes.stock import stock_routes
    from routes.marketplace_routes import marketplace_routes
    # from routes.documentation_routes import documentation_routes  # Import the documentation_routes blueprint

    app.register_blueprint(transaction_routes)
    app.register_blueprint(account_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(search_routes)  # Register the search_routes blueprint
    app.register_blueprint(log_routes)
    app.register_blueprint(crypto_routes)
    app.register_blueprint(stock_routes)
    app.register_blueprint(marketplace_routes)
    # app.register_blueprint(documentation_routes)  # Register the documentation_routes blueprint

    # Log rules for each Blueprint
    logger.info("\nMain Application Rules:")
    for rule in app.url_map.iter_rules():
        logger.info(rule)

    # Set logging level to WARNING (or higher) to reduce log messages
    log_handler = logging.StreamHandler()
    log_handler.setLevel(logging.DEBUG)  # Change to WARNING if needed
    logger.addHandler(log_handler)

    # Set logging from werkzeug to app.log file
    werkzeug_logger = logging.getLogger('werkzeug')
    for handler in logger.handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s - %(message)s'))
        werkzeug_logger.addHandler(handler)

    # Set logging from DatabaseHandling.connection to app.log file
    database_logger = logging.getLogger('DatabaseHandling.connection')
    database_logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s - %(message)s'))
        database_logger.addHandler(handler)

    # Set logging from routes.account_routes.dashboard to app.log file
    account_logger = logging.getLogger('routes.account_routes.dashboard')
    account_logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s - %(message)s'))
        account_logger.addHandler(handler)

    # Set logging from DatabaseHandling.authentication to app.log file
    auth_logger = logging.getLogger('DatabaseHandling.authentication')
    auth_logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s - %(message)s'))
        auth_logger.addHandler(handler)

    # Set logging from DatabaseHandling.registration_func to app.log file
    registration_logger = logging.getLogger('DatabaseHandling.registration_func')
    registration_logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s - %(message)s'))
        registration_logger.addHandler(handler)

    # Set logging from DatabaseHandling.withdraw to app.log file
    withdraw_logger = logging.getLogger('DatabaseHandling.withdraw')
    withdraw_logger.setLevel(logging.INFO)
    for handler in logger.handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(name)s - %(message)s'))
        withdraw_logger.addHandler(handler)

    # Enable CORS support
    CORS(app)

    # Custom 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        # Log available URLs
        available_urls = [rule.rule for rule in app.url_map.iter_rules()]
        logging.error(
            f"404 Not Found: {request.url}. The requested URL was not found on the server. Available URLs: {available_urls}")

        # Render the error page
        return render_template("error.html",
                               error_message=f"404 Not Found: {request.url}. The requested URL was not found on the server. If you entered the URL manually, please check your spelling and try again."), 404

    # Add error handling for authentication-related issues
    @app.errorhandler(401)
    def unauthorized_error(e):
        logger.error(f"Unauthorized access attempt: {request.url}")
        return render_template("error.html", error_message="401 Unauthorized: Access is denied."), 401

    @app.errorhandler(403)
    def forbidden_error(e):
        logger.error(f"Forbidden access attempt: {request.url}")
        return render_template("error.html", error_message="403 Forbidden: You do not have permission to access this resource."), 403

    @app.errorhandler(Exception)
    def log_error(exception):
        # Get the exception details
        error_message = str(exception)

        # Render the error template with the error message
        return render_template("error.html", error_message=error_message), 500

    return app
