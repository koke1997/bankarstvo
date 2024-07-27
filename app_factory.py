# app_factory.py
import traceback
import logging
from flask import Flask, render_template, request
from utils.extensions import db, bcrypt, login_manager, create_extensions
from logging.config import fileConfig
import os
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    #Load the logging configuration
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
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "mysql+pymysql://ikokalovic:Mikrovela1!@localhost:3306/banking_app")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    create_extensions(app)

    login_manager.login_view = "user_routes.login"
    login_manager.login_message_category = "info"

    # Register Blueprints
    from routes.transaction_routes import transaction_routes
    from routes.account_routes import account_routes
    from routes.user_routes import user_routes
    from routes.search_routes.search import search_routes  # Import the search_routes blueprint
    from routes.logger_routes.log_routes import log_routes
    from routes.transaction_routes.crypto import crypto_routes
    from routes.transaction_routes.stock import stock_routes
    from routes.marketplace_routes import marketplace_routes
    from routes.documentation_routes import documentation_routes  # Import the documentation_routes blueprint

    app.register_blueprint(transaction_routes)
    app.register_blueprint(account_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(search_routes)  # Register the search_routes blueprint
    app.register_blueprint(log_routes)
    app.register_blueprint(crypto_routes)
    app.register_blueprint(stock_routes)
    app.register_blueprint(marketplace_routes)
    app.register_blueprint(documentation_routes)  # Register the documentation_routes blueprint

    # Log rules for each Blueprint
    logger.info("\nMain Application Rules:")
    for rule in app.url_map.iter_rules():
        logger.info(rule)

    # Set logging level to WARNING (or higher) to reduce log messages
    log_handler = logging.StreamHandler()
    log_handler.setLevel(logging.DEBUG)  # Change to WARNING if needed
    logger.addHandler(log_handler)

    #Set logging from werkzeug to app.log file
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

    # Enable CORS support
    CORS(app)

    # Custom 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        # Log available URLs
        available_urls = [rule.rule for rule in app.url_map.iter_rules()]
        logging.error(f"404 Not Found: {request.url}. The requested URL was not found on the server. Available URLs: {available_urls}")

        # Render the error page
        return render_template("error.html", error_message=f"404 Not Found: {request.url}. The requested URL was not found on the server. If you entered the URL manually, please check your spelling and try again."), 404

    @app.errorhandler(Exception)
    def log_error(exception):
        # Get the exception details
        error_message = str(exception)

        # Render the error template with the error message
        return render_template("error.html", error_message=error_message), 500
    return app
