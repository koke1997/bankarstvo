# app_factory.py
import logging
import os
import sys
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Import refactored modules
from utils.config import load_configuration
from utils.logging_setup import configure_logging, configure_module_loggers
from utils.blueprints import register_blueprints
from utils.error_handlers import register_error_handlers
from utils.auth import configure_login_manager, configure_keycloak
from utils.extensions import create_extensions, db

# Register the app paths
PROJECT_ROOT = Path(__file__).parent.absolute()
CORE_DIRS = ['api', 'core', 'database', 'infrastructure', 'utils', 'web']
for directory in CORE_DIRS:
    path = PROJECT_ROOT / directory
    if path.exists() and str(path) not in sys.path:
        sys.path.append(str(path))

# Initialize SocketIO with threading mode instead of eventlet
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

def create_app():
    app = Flask(__name__)

    # --- Load Configuration ---
    load_configuration(app)
    
    # --- Configure Logging ---
    configure_logging(app)
    configure_module_loggers(app)  # Configure module-specific loggers
    
    # --- Initialize Extensions ---
    create_extensions(app)
    
    # Initialize SocketIO with the app
    try:
        socketio.init_app(app, cors_allowed_origins="*")
    except TypeError:
        # If the above fails, try without the cors parameter
        socketio.init_app(app)
        app.logger.warning("SocketIO initialized without CORS parameter due to compatibility issues")

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

    # --- Initialize Database ---
    with app.app_context():
        db.init_app(app)
        if not app.config.get("TESTING", False):
            try:
                db.create_all()
                app.logger.info("Database tables created successfully")
            except Exception as e:
                app.logger.error(f"Error creating database tables: {e}")

    return app
