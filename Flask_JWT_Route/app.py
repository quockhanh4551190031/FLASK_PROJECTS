from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = '010904'

jwt = JWTManager(app)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={'username': user.username})
        user.token = access_token
        db.session.commit()
        return jsonify({'token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/auth', methods=['GET'])
@jwt_required()
def auth():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# API này đã được bảo vệ bởi @jwt_required() ở trên
# Nếu bạn muốn tạo một API mới, chỉ cần thêm decorator này
@app.route("/hello", methods=["GET"])
@jwt_required()
def hello_world_protected():
    return "Hello World"

if __name__ == '__main__':
    app.run(debug=True)