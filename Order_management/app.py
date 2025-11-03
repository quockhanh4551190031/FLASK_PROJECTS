from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, PORT
from models.models import db
from controllers.orders_controller import orders_bp
from controllers.order_items_controller import items_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db.init_app(app)

app.register_blueprint(orders_bp)
app.register_blueprint(items_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=PORT)
