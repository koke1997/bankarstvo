from flask import Blueprint

transaction_routes = Blueprint("transaction_routes", __name__)

# Include other shared imports and constants here

# Include other shared functions here

# Include other shared routes here

from .deposit import deposit
from .withdraw import withdraw
from .transfer import transfer
from .history import transaction_history
from .document import generate_and_save_document
