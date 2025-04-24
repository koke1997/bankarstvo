# utils/routes.py
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

def register_blueprint(app, blueprint, url_prefix=None):
    """
    Register a blueprint with the application and log registered routes.
    
    Args:
        app: Flask application instance
        blueprint: Blueprint to register
        url_prefix: URL prefix for the blueprint
    """
    if url_prefix:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
    else:
        app.register_blueprint(blueprint)
    
    # Extract and log routes from this blueprint
    routes = [rule.rule for rule in app.url_map.iter_rules() 
              if rule.endpoint.startswith(blueprint.name + '.')]
    
    logger.info(f"Registered {blueprint.name} routes: {routes}")
    return routes