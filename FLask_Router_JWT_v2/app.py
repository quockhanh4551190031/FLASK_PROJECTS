from flask import Flask, request, jsonify, g
import jwt
import datetime
from functools import wraps
import hashlib
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = '010904'

# Giả lập bảng người dùng
users_db = [
    {
        'IdUser': 1,
        'UserName': 'testuser',
        'Password': hashlib.md5('password123'.encode()).hexdigest(),  # Mã hóa MD5
        'Token': ''
    }
]

def encode_password(password):
    # Giả sử client gửi base64 hoặc md5, ở đây kiểm tra md5
    try:
        # Nếu là base64
        decoded = base64.b64decode(password).decode()
        return hashlib.md5(decoded.encode()).hexdigest()
    except Exception:
        # Nếu là md5
        return password

def generate_token(user_id, username):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Lấy token từ header Authorization
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[-1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('userName')
    password = data.get('password')
    encoded_password = encode_password(password)
    user = next((u for u in users_db if u['UserName'] == username and u['Password'] == encoded_password), None)
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    token = generate_token(user['IdUser'], user['UserName'])
    user['Token'] = token
    return jsonify({'token': token})

@app.route('/auth', methods=['POST'])
def auth():
    token = request.get_json().get('token')
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'valid': True, 'user': data})
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'message': 'Invalid token'}), 401

@app.route('/hello', methods=['GET'])
@token_required
def hello():
    return jsonify({'message': 'Hello World', 'user': g.current_user})

if __name__ == '__main__':
    app.run(debug=True)