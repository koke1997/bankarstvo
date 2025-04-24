# utils/config.py
import os
import sys
import logging
from pathlib import Path

def load_configuration(app):
    """Load application configuration from environment and files."""
    # Set basic configuration
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "0") == "1"
    app.config["TESTING"] = os.getenv("FLASK_TESTING", "0") == "1"
    
    # Load database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:example@localhost:3306/bankarstvo"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Load Flask environment variables
    app.config["FLASK_APP"] = os.getenv("FLASK_APP", "app.py")
    app.config["FLASK_DEBUG"] = os.getenv("FLASK_DEBUG", "1")
    app.config["FLASK_ENV"] = os.getenv("FLASK_ENV", "development")
    
    # Set secret key for sessions
    app.secret_key = os.getenv("SECRET_KEY", "dev_key_not_secure")
    
    # Default configuration for uploads
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
    
    # Load additional configuration from environment
    for key, value in os.environ.items():
        if key.startswith('FLASK_') or key.startswith('APP_'):
            app.config[key] = value
    
    # Testing configuration
    configure_test_environment(app)
    
    # Debug log
    if app.debug:
        logging.getLogger("app_factory").debug(f"Application configuration: {app.config}")
        
    return app

def configure_test_environment(app):
    """Configure application for testing if needed."""
    # Check for test mode
    is_testing = (
        app.config.get("TESTING") or 
        "pytest" in sys.modules or
        os.environ.get("FLASK_ENV") == "testing"
    )
    
    if is_testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SKIP_KEYCLOAK"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.logger.info("Running in TEST mode with in-memory SQLite database")