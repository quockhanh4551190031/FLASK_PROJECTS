from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from models import db, Product
from datetime import datetime
import requests

app = Flask(__name__)

# Cấu Hình SQL và Port
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ma = Marshmallow(app)

# ==============
# Khởi tạo DB
# ===============
with app.app_context():
    db.create_all()

# Scheme Json
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

products_schema = ProductSchema()
products_schemas = ProductSchema(many=True)

# ==============
# Xác thực Token
# ===============
def validate_token(token):
    if not token:
        return False
    token = token.replace("Bearer ", "")
    try:
        res = requests.post("http://localhost:5000/auth", json={"token": token})
        if res.status_code == 200:
            data = res.json()
            return data.get("valid", False)
        return False
    except Exception as e:
        print("Auth service error:", e)
        return False

# ==============
# API
# ===============

# Lấy ds sản phẩm
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schemas.jsonify(products)

# Lấy chi tiết 1 sản phẩm
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return products_schema.jsonify(product)

# Thêm sản phẩm
@app.route('/products', methods=['POST'])
def create_product():
    token = request.headers.get("Authorization")
    if not validate_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    new_product = Product(
        name=data.get("name"),
        description=data.get("description"),
        price=data.get("price"),
        quantity=data.get("quantity", 0)
    )
    db.session.add(new_product)
    db.session.commit()
    return products_schema.jsonify(new_product), 201


# Cập nhật sản phẩm
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    token = request.headers.get("Authorization")
    if not validate_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    product = Product.query.get_or_404(id)
    data = request.get_json()

    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.price = data.get("price", product.price)
    product.quantity = data.get("quantity", product.quantity)
    product.updated_at = datetime.utcnow()

    db.session.commit()
    return products_schema.jsonify(product)

# Xóa sản phẩm (cần token)
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    token = request.headers.get("Authorization")
    if not validate_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Product {id} deleted"}), 200

# Chạy service
if __name__ == '__main__':
    app.run(debug=True, port=5001)