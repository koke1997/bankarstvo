from flask import Blueprint, request, jsonify
from core.models import MarketplaceItem, MarketplaceTransaction
from utils.extensions import db
from flask_login import current_user

marketplace_routes = Blueprint("marketplace_routes", __name__)

@marketplace_routes.route("/marketplace/list", methods=["GET"])
def list_items():
    items = MarketplaceItem.query.filter_by(status="available").all()
    items_list = [{"id": item.item_id, "name": item.name, "description": item.description, "price": str(item.price)} for item in items]
    return jsonify(items_list)

@marketplace_routes.route("/marketplace/sell", methods=["POST"])
def sell_item():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")

    new_item = MarketplaceItem(
        name=name,
        description=description,
        price=price,
        seller_id=current_user.id,
        status="available"
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify({"message": "Item listed for sale successfully!"}), 201
