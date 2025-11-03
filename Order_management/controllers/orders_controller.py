import json
from flask import Blueprint, request, jsonify
from models.models import db, Order
from services.auth_service import is_authenticated

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([o.serialize() for o in orders])

@orders_bp.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.get_or_404(id)
    return jsonify(order.serialize())

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    token = request.headers.get('Authorization')
    if not is_authenticated(token):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    try:
        order = Order(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            total_amount=data['total_amount'],
            status=data.get('status', 'pending')
        )
        db.session.add(order)
        db.session.commit()
        return jsonify({
            'id': order.id,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'total_amount': float(order.total_amount),
            'status': order.status
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = Order.query.get_or_404(id)
    order.status = request.json.get('status', order.status)
    db.session.commit()
    return jsonify(order.serialize())

@orders_bp.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return '', 204