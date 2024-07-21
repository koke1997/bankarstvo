from flask import Blueprint, request, jsonify
from utils.extensions import db
from core.models import CryptoAsset
import requests

crypto_routes = Blueprint('crypto_routes', __name__)

@crypto_routes.route('/crypto/buy', methods=['POST'])
def buy_crypto():
    data = request.get_json()
    user_id = data.get('user_id')
    symbol = data.get('symbol')
    amount = data.get('amount')

    # Call a popular free API to get the current price of the crypto
    response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd')
    price_data = response.json()
    price = price_data[symbol]['usd']

    # Calculate the total cost
    total_cost = price * amount

    # Check if the user has enough balance
    user_balance = get_user_balance(user_id)
    if user_balance < total_cost:
        return jsonify({'error': 'Insufficient balance'}), 400

    # Deduct the total cost from the user's balance
    update_user_balance(user_id, user_balance - total_cost)

    # Add the purchased crypto to the user's assets
    crypto_asset = CryptoAsset.query.filter_by(user_id=user_id, symbol=symbol).first()
    if crypto_asset:
        crypto_asset.balance += amount
    else:
        new_crypto_asset = CryptoAsset(user_id=user_id, symbol=symbol, balance=amount)
        db.session.add(new_crypto_asset)
    db.session.commit()

    return jsonify({'message': 'Crypto purchased successfully'}), 200

@crypto_routes.route('/crypto/sell', methods=['POST'])
def sell_crypto():
    data = request.get_json()
    user_id = data.get('user_id')
    symbol = data.get('symbol')
    amount = data.get('amount')

    # Call a popular free API to get the current price of the crypto
    response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd')
    price_data = response.json()
    price = price_data[symbol]['usd']

    # Calculate the total value
    total_value = price * amount

    # Check if the user has enough crypto balance
    crypto_asset = CryptoAsset.query.filter_by(user_id=user_id, symbol=symbol).first()
    if not crypto_asset or crypto_asset.balance < amount:
        return jsonify({'error': 'Insufficient crypto balance'}), 400

    # Deduct the sold crypto from the user's assets
    crypto_asset.balance -= amount
    if crypto_asset.balance == 0:
        db.session.delete(crypto_asset)

    # Add the total value to the user's balance
    user_balance = get_user_balance(user_id)
    update_user_balance(user_id, user_balance + total_value)

    db.session.commit()

    return jsonify({'message': 'Crypto sold successfully'}), 200

def get_user_balance(user_id):
    # Implement this function to get the user's balance from the database
    pass

def update_user_balance(user_id, new_balance):
    # Implement this function to update the user's balance in the database
    pass
