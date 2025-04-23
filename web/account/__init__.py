# account_routes/__init__.py
from flask import Blueprint

account_routes = Blueprint("account_routes", __name__, 
                           template_folder="templates",
                           url_prefix="/account")  # Added URL prefix for better route organization

# Import route functions
from .dashboard import dashboard
from .create_account import create_account
from .select_account import select_account
from .get_balance import get_balance

# Register the routes with more descriptive endpoints
account_routes.add_url_rule("/dashboard", 
                           endpoint="dashboard", 
                           view_func=dashboard, 
                           methods=["GET", "POST"])

account_routes.add_url_rule("/create", 
                           endpoint="create_account", 
                           view_func=create_account, 
                           methods=["GET", "POST"])

account_routes.add_url_rule("/select", 
                           endpoint="select_account", 
                           view_func=select_account, 
                           methods=["GET", "POST"])

account_routes.add_url_rule("/balance", 
                           endpoint="get_balance", 
                           view_func=get_balance, 
                           methods=["GET"])

# Log registration of account routes
print(f"Registered account routes: {[rule.rule for rule in account_routes.iter_rules()]}")