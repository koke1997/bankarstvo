from flask import Blueprint, jsonify
import pycountry

# Create a blueprint for currency API endpoints
currency_api = Blueprint('currency_api', __name__)

@currency_api.route('/currencies', methods=['GET'])
def get_currencies():
    """
    Fetch all available currencies
    Returns a list of objects with 'code' and 'name' properties
    """
    try:
        # Use pycountry to get all currencies
        currencies = []
        for currency in pycountry.currencies:
            if hasattr(currency, 'alpha_3') and hasattr(currency, 'name'):
                currencies.append({
                    "code": currency.alpha_3,
                    "name": currency.name
                })
        
        # If for some reason pycountry doesn't provide any currencies
        if not currencies:
            currencies = [
                {"code": "USD", "name": "US Dollar"},
                {"code": "EUR", "name": "Euro"},
                {"code": "GBP", "name": "British Pound"},
            ]
        
        return jsonify(currencies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500