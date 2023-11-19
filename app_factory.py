import traceback
from flask import Flask
from extensions import db, bcrypt, login_manager, create_extensions
from routes.user_routes import configure_user_routes
from routes.account_routes import configure_account_routes
from routes.transaction_routes import configure_transaction_routes

def create_app():
    app = Flask(__name__)

    # Configuration settings
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ikokalovic:Mikrovela1!@localhost:3306/banking_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    create_extensions(app)

    login_manager.login_view = 'user_routes.login'
    login_manager.login_message_category = 'info'

    # Import blueprints and register them
    from routes.user_routes import configure_user_routes
    from routes.account_routes import configure_account_routes
    from routes.transaction_routes import configure_transaction_routes

    configure_user_routes(app)
    configure_account_routes(app)
    configure_transaction_routes(app)

    # Add a custom exception handler to log the traceback
    @app.errorhandler(Exception)
    def log_error(e):
        traceback_str = traceback.format_exc()
        app.logger.error(f"An exception occurred: {str(e)}\n{traceback_str}")
        return 'An internal server error occurred.', 500
    app.debug = True
    return app



