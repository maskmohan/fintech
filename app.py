from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields, validate, ValidationError
import uuid
import decimal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/fintech_wallet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '74ed47754a2508bb7ef630353cd2af93b1b6241b1c50ca5d3990dece16e2347b'  # In my local system directly give , it's actual move on env
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(15))
    wallet_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    balance = db.Column(db.Numeric(10, 2), default=0)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.String(36), db.ForeignKey('user.wallet_id'))
    transaction_type = db.Column(db.String(50))
    amount = db.Column(db.Numeric(10, 2))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class UserSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    phone_number = fields.String(required=True, validate=validate.Length(min=10, max=15))
    password = fields.String(required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=100))
    password = fields.String(required=True, validate=validate.Length(min=6))

class AddMoneySchema(Schema):
    wallet_id = fields.String(required=True, validate=validate.Length(equal=36))
    amount = fields.Decimal(required=True, as_string=True)

user_schema = UserSchema()
login_schema = LoginSchema()
add_money_schema = AddMoneySchema()

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify(error.messages), 400

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/wallet')
def wallet_page():
    return render_template('wallet.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    name = data['name']
    email = data['email']
    phone_number = data['phone_number']
    password = data['password']
    wallet_id = str(uuid.uuid4())
    new_user = User(name=name, email=email, phone_number=phone_number, wallet_id=wallet_id)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'wallet_id': new_user.wallet_id, 'balance': new_user.balance})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.wallet_id)
        return jsonify(access_token=access_token)
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/wallet/add-money', methods=['POST'])
@jwt_required()
def add_money():
    data = request.json
    errors = add_money_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    wallet_id = get_jwt_identity()
    amount = decimal.Decimal(data['amount'])
    user = User.query.filter_by(wallet_id=wallet_id).first()
    if user:
        user.balance += amount
        new_transaction = Transaction(wallet_id=wallet_id, transaction_type='Add Money', amount=amount)
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'balance': user.balance})
    return jsonify({'error': 'Wallet not found'}), 404

@app.route('/api/wallet/<wallet_id>/balance', methods=['GET'])
@jwt_required()
def check_balance(wallet_id):
    user = User.query.filter_by(wallet_id=wallet_id).first()
    if user:
        return jsonify({'balance': user.balance})
    return jsonify({'error': 'Wallet not found'}), 404

@app.route('/api/wallet/<wallet_id>/transactions', methods=['GET'])
@jwt_required()
def transaction_history(wallet_id):
    transactions = Transaction.query.filter_by(wallet_id=wallet_id).all()
    return jsonify([{
        'transaction_type': t.transaction_type,
        'amount': t.amount,
        'timestamp': t.timestamp
    } for t in transactions])

@app.route('/api/admin/wallets', methods=['GET'])
@jwt_required()
def view_all_wallets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page,
        'users': [{
            'name': u.name,
            'email': u.email,
            'phone_number': u.phone_number,
            'wallet_id': u.wallet_id,
            'balance': u.balance
        } for u in users.items]
    })

@app.route('/api/admin/transactions', methods=['GET'])
@jwt_required()
def view_all_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    transactions = Transaction.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'total': transactions.total,
        'pages': transactions.pages,
        'current_page': transactions.page,
        'transactions': [{
            'wallet_id': t.wallet_id,
            'transaction_type': t.transaction_type,
            'amount': t.amount,
            'timestamp': t.timestamp
        } for t in transactions.items]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)