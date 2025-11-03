from flask import Blueprint, request, jsonify
from models.models import db, OrderItem
from services.product_service import check_inventory
from services.auth_service import is_authenticated

items_bp = Blueprint('order_items', __name__)

@items_bp.route('/order_items', methods=['GET'])
def get_items():
    return jsonify([i.serialize() for i in OrderItem.query.all()])

@items_bp.route('/order_items/<int:id>', methods=['GET'])
def get_item(id):
    item = OrderItem.query.get_or_404(id)
    return jsonify(item.serialize())

@items_bp.route('/order_items', methods=['POST'])
def create_item():
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not check_inventory(data['product_id'], data['quantity']):
        return jsonify({'error': 'Insufficient stock'}), 400

    data['total_price'] = data['quantity'] * data['unit_price']
    item = OrderItem(**data)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.serialize()), 201

@items_bp.route('/order_items/<int:id>', methods=['PUT'])
def update_item(id):
    item = OrderItem.query.get_or_404(id)
    item.quantity = request.json.get('quantity', item.quantity)
    db.session.commit()
    return jsonify(item.serialize())

@items_bp.route('/order_items/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = OrderItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return '', 204
