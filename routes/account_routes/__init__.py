# account_routes/__init__.py
from flask import Blueprint

account_routes = Blueprint("account_routes", __name__, template_folder="templates")  # Assuming templates are in a subfolder

# Import other route functions
from .dashboard import dashboard
from .create_account import create_account
from .select_account import select_account
from .get_balance import get_balance

# Register the routes
account_routes.add_url_rule("/dashboard", endpoint="dashboard", view_func=dashboard)
account_routes.add_url_rule("/create_account", endpoint="create_account", view_func=create_account)
account_routes.add_url_rule("/select_account", endpoint="select_account", view_func=select_account)
account_routes.add_url_rule("/get-balance", endpoint="get_balance", view_func=get_balance)