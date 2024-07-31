from flask import Blueprint, request, jsonify
from utils.extensions import db
from core.models import StockAsset
import requests

stock_routes = Blueprint("stock_routes", __name__)


@stock_routes.route("/stock/buy", methods=["POST"])
def buy_stock():
    data = request.get_json()
    user_id = data.get("user_id")
    symbol = data.get("symbol")
    shares = data.get("shares")

    # Call a popular free API to get the current price of the stock
    response = requests.get(f"https://api.example.com/stock/{symbol}/price")
    price_data = response.json()
    price = price_data["price"]

    # Calculate the total cost
    total_cost = price * shares

    # Check if the user has enough balance
    user_balance = get_user_balance(user_id)
    if user_balance < total_cost:
        return jsonify({"error": "Insufficient balance"}), 400

    # Deduct the total cost from the user's balance
    update_user_balance(user_id, user_balance - total_cost)

    # Add the purchased stock to the user's assets
    stock_asset = StockAsset.query.filter_by(user_id=user_id, symbol=symbol).first()
    if stock_asset:
        stock_asset.shares += shares
    else:
        new_stock_asset = StockAsset(user_id=user_id, symbol=symbol, shares=shares)
        db.session.add(new_stock_asset)
    db.session.commit()

    return jsonify({"message": "Stock purchased successfully"}), 200


@stock_routes.route("/stock/sell", methods=["POST"])
def sell_stock():
    data = request.get_json()
    user_id = data.get("user_id")
    symbol = data.get("symbol")
    shares = data.get("shares")

    # Call a popular free API to get the current price of the stock
    response = requests.get(f"https://api.example.com/stock/{symbol}/price")
    price_data = response.json()
    price = price_data["price"]

    # Calculate the total value
    total_value = price * shares

    # Check if the user has enough stock balance
    stock_asset = StockAsset.query.filter_by(user_id=user_id, symbol=symbol).first()
    if not stock_asset or stock_asset.shares < shares:
        return jsonify({"error": "Insufficient stock balance"}), 400

    # Deduct the sold stock from the user's assets
    stock_asset.shares -= shares
    if stock_asset.shares == 0:
        db.session.delete(stock_asset)

    # Add the total value to the user's balance
    user_balance = get_user_balance(user_id)
    update_user_balance(user_id, user_balance + total_value)

    db.session.commit()

    return jsonify({"message": "Stock sold successfully"}), 200


def get_user_balance(user_id):
    # Implement this function to get the user's balance from the database
    pass


def update_user_balance(user_id, new_balance):
    # Implement this function to update the user's balance in the database
    pass
