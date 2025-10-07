from flask import Flask, request, jsonify, g, render_template, session, redirect, url_for
import jwt
import datetime
from functools import wraps
import hashlib
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = '010904'
app.config['SESSION_TYPE'] = 'filesystem'  # Để session hoạt động tốt hơn

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
    # Luôn mã hóa MD5 cho chuỗi password gốc
    return hashlib.md5(password.encode()).hexdigest()

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
        # Lấy token từ session trước (cho UI)
        if 'token' in session:
            token = session['token']
        # Nếu không, lấy từ header Authorization (cho API)
        elif 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[-1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.current_user = data
        except jwt.ExpiredSignatureError:
            # Xóa session nếu hết hạn
            session.pop('token', None)
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
def index():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.content_type == 'application/json':  # Giữ nguyên API JSON
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

    # Xử lý form HTML (POST từ UI)
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return render_template('login.html', error='Vui lòng nhập tên đăng nhập và mật khẩu!')

    encoded_password = hashlib.md5(password.encode()).hexdigest()   # Mã hóa MD5
    user = next((u for u in users_db if u['UserName'] == username and u['Password'] == encoded_password), None)
    if not user:
        return render_template('login.html', error='Tên đăng nhập hoặc mật khẩu không đúng!')
    token = generate_token(user['IdUser'], user['UserName'])
    user['Token'] = token
    session['token'] = token  # Lưu token vào session
    print("DEBUG:", username, password, encoded_password)
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard():
    return render_template('dashboard.html', user=g.current_user)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('token', None)
    return redirect(url_for('index'))

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