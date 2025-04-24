# utils/logging_setup.py
import os
import logging
import logging.config
from pathlib import Path

def configure_logging(app):
    """Configure application logging from configuration file."""
    # Try to load logging configuration
    log_config_paths = [
        Path("config/logging.conf"),
        Path("configuration/logging.conf"),
        Path(app.root_path) / "config" / "logging.conf",
    ]
    
    # Find first available logging configuration
    for log_path in log_config_paths:
        if log_path.exists():
            logging.config.fileConfig(log_path)
            app.logger.info(f"Loaded logging configuration from {log_path}")
            break
    else:
        # Basic configuration if no config file found
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        app.logger.warning("No logging configuration found, using basic setup")
    
    # Ensure app logger is properly configured
    app.logger.setLevel(logging.INFO if not app.debug else logging.DEBUG)
    
    # Configure SQLAlchemy logging level based on debug status
    if not app.debug:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return app

def configure_module_loggers(app):
    """Configure loggers for specific modules."""
    logger = app.logger
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    # Core application modules
    modules = [
        'web',
        'api',
        'core',
        'database',
        'infrastructure',
        'werkzeug',
    ]
    
    for module in modules:
        module_logger = logging.getLogger(module)
        module_logger.setLevel(log_level)
        # Ensure handler doesn't already exist to prevent duplicate logs
        if not module_logger.handlers:
            for handler in logger.handlers:
                module_logger.addHandler(handler)