from flask import Flask, Blueprint
from api.rest.routes.currency_routes import currency_api
from api.rest.routes.account_routes import account_api
from api.rest.routes.transaction_routes import transaction_api
from api.rest.routes.auth_routes import auth_api
import logging

logger = logging.getLogger(__name__)

def create_api_blueprint():
    """
    Create and configure the main API blueprint
    that includes all API route blueprints
    """
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    
    # Register all API route blueprints here
    api_blueprint.register_blueprint(currency_api, url_prefix='/currency')
    api_blueprint.register_blueprint(account_api, url_prefix='')
    api_blueprint.register_blueprint(transaction_api, url_prefix='')
    
    # Register auth_api with proper prefix for React frontend compatibility
    logger.info("Registering auth API blueprint with appropriate prefix")
    auth_api.url_prefix = '/auth'  # Set the URL prefix directly on the blueprint
    api_blueprint.register_blueprint(auth_api)
    
    return api_blueprint
