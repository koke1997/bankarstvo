from flask import Blueprint

marketplace_routes = Blueprint("marketplace_routes", __name__)

# Import other route functions
from .items import list_items, sell_item

# Register the routes
marketplace_routes.add_url_rule("/marketplace/list", endpoint="list_items", view_func=list_items)
marketplace_routes.add_url_rule("/marketplace/sell", endpoint="sell_item", view_func=sell_item)
