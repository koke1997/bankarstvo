# app_factory.py
import traceback
import logging
from flask import Flask, render_template, request   
from extensions import db, bcrypt, login_manager, create_extensions

def create_app():
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)


    app.static_folder = "static"

    # Configuration settings
    app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://ikokalovic:Mikrovela1!@localhost:3306/banking_app"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    create_extensions(app)

    login_manager.login_view = "user_routes.login"
    login_manager.login_message_category = "info"

    # Register Blueprints
    from routes.transaction_routes import transaction_routes
    from routes.account_routes import account_routes
    from routes.user_routes import user_routes

    app.register_blueprint(transaction_routes)
    app.register_blueprint(account_routes)
    app.register_blueprint(user_routes)


    # Print rules for each Blueprint
    print("\nMain Application Rules:")
    for rule in app.url_map.iter_rules():
        print(rule)

    # Set logging level to WARNING (or higher) to reduce log messages
    log_handler = logging.StreamHandler()
    log_handler.setLevel(logging.DEBUG)  # Change to WARNING if needed
    app.logger.addHandler(log_handler)

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
