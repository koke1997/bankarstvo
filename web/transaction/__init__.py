from flask import Blueprint

transaction_routes = Blueprint("transaction_routes", __name__, 
                              template_folder="templates",
                              url_prefix="/transaction")  # Added URL prefix for better route organization

# Import route functions
from .deposit import deposit
from .withdraw import withdraw
from .transfer import transfer
from .history import transaction_history
from .document import generate_and_save_document

# Register the routes with descriptive endpoints and HTTP methods
transaction_routes.add_url_rule("/deposit", 
                               endpoint="deposit", 
                               view_func=deposit, 
                               methods=["GET", "POST"])

transaction_routes.add_url_rule("/withdraw", 
                               endpoint="withdraw", 
                               view_func=withdraw, 
                               methods=["GET", "POST"])

transaction_routes.add_url_rule("/transfer", 
                               endpoint="transfer", 
                               view_func=transfer, 
                               methods=["GET", "POST"])

transaction_routes.add_url_rule("/history", 
                               endpoint="transaction_history", 
                               view_func=transaction_history, 
                               methods=["GET"])

transaction_routes.add_url_rule("/document", 
                               endpoint="generate_document", 
                               view_func=generate_and_save_document, 
                               methods=["GET", "POST"])

# Log registration of transaction routes
print(f"Registered transaction routes: {[rule.rule for rule in transaction_routes.iter_rules()]}")
