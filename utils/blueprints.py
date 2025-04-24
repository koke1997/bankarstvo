# utils/blueprints.py
import importlib


def register_blueprints(app):
    """Register all application blueprints."""
    blueprints = []
    
    # Core blueprints - with proper error handling
    try:
        # Transaction blueprint
        from web.transaction.routes import transaction_bp
        blueprints.append({"bp": transaction_bp, "url_prefix": "/transaction"})
        
        # Account blueprint
        from web.account.routes import account_bp
        blueprints.append({"bp": account_bp, "url_prefix": "/account"})
        
        # User blueprint
        from web.user.routes import user_bp
        blueprints.append({"bp": user_bp, "url_prefix": "/user"})
    except ImportError as e:
        app.logger.error(f"Failed to import core blueprints: {e}")
    
    # Optional blueprints - with graceful fallback
    optional_blueprints = [
        ("web.search.routes", "search_bp", "/search"),
        ("web.logger.routes", "log_bp", "/logs"),
        ("web.crypto.routes", "crypto_bp", "/crypto"),
        ("web.stock.routes", "stock_bp", "/stock"),
        ("web.marketplace.routes", "marketplace_bp", "/marketplace")
    ]
    
    for module_path, bp_name, url_prefix in optional_blueprints:
        try:
            module = importlib.import_module(module_path)
            blueprint = getattr(module, bp_name)
            blueprints.append({"bp": blueprint, "url_prefix": url_prefix})
        except (ImportError, AttributeError) as e:
            app.logger.warning(f"Optional blueprint {bp_name} not available: {e}")
    
    # API blueprint
    try:
        from api.rest import create_api_blueprint
        api_blueprint = create_api_blueprint()
        app.register_blueprint(api_blueprint)
        app.logger.info(f"Registered API blueprint")
    except ImportError as e:
        app.logger.error(f"Failed to register API blueprint: {e}")
    
    # Register all available blueprints
    for blueprint in blueprints:
        bp = blueprint["bp"]
        url_prefix = blueprint.get("url_prefix")
        
        # Use the provided URL prefix if the blueprint doesn't already have one
        if url_prefix and not getattr(bp, "url_prefix", None):
            app.register_blueprint(bp, url_prefix=url_prefix)
        else:
            app.register_blueprint(bp)
    
    # Log registered blueprints
    app.logger.info("Registered Blueprints:")
    for blueprint in blueprints:
        bp = blueprint["bp"]
        prefix = getattr(bp, "url_prefix", None) or blueprint.get("url_prefix", "")
        app.logger.info(f"• {bp.name} -> {prefix}")