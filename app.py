
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import uuid
import decimal

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/fintech_wallet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(15))
    wallet_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    balance = db.Column(db.Numeric(10, 2), default=0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.String(36), db.ForeignKey('user.wallet_id'))
    transaction_type = db.Column(db.String(50))
    amount = db.Column(db.Numeric(10, 2))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

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
    name = data['name']
    email = data['email']
    phone_number = data['phone_number']
    wallet_id = str(uuid.uuid4())
    new_user = User(name=name, email=email, phone_number=phone_number, wallet_id=wallet_id)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'wallet_id': new_user.wallet_id, 'balance': new_user.balance})

@app.route('/api/wallet/add-money', methods=['POST'])
def add_money():
    data = request.json
    wallet_id = data['wallet_id']
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
def check_balance(wallet_id):
    user = User.query.filter_by(wallet_id=wallet_id).first()
    if user:
        return jsonify({'balance': user.balance})
    return jsonify({'error': 'Wallet not found'}), 404

@app.route('/api/wallet/<wallet_id>/transactions', methods=['GET'])
def transaction_history(wallet_id):
    transactions = Transaction.query.filter_by(wallet_id=wallet_id).all()
    return jsonify([{
        'transaction_type': t.transaction_type,
        'amount': t.amount,
        'timestamp': t.timestamp
    } for t in transactions])

@app.route('/api/admin/wallets', methods=['GET'])
def view_all_wallets():
    users = User.query.all()
    return jsonify([{
        'name': u.name,
        'email': u.email,
        'phone_number': u.phone_number,
        'wallet_id': u.wallet_id,
        'balance': u.balance
    } for u in users])

@app.route('/api/admin/transactions', methods=['GET'])
def view_all_transactions():
    transactions = Transaction.query.all()
    return jsonify([{
        'wallet_id': t.wallet_id,
        'transaction_type': t.transaction_type,
        'amount': t.amount,
        'timestamp': t.timestamp
    } for t in transactions])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)