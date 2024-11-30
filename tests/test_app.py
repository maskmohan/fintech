import unittest
from app import app, db, User, Transaction
from flask_testing import TestCase
from flask_jwt_extended import create_access_token

class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('test_config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()
        self.user = self.create_user()
        self.token = self.get_token()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_user(self):
        user = User(name='Test User', email='test@example.com', phone_number='1234567890')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

    def get_token(self):
        return create_access_token(identity=self.user.wallet_id)

class UserTests(BaseTestCase):
    def test_register_user(self):
        response = self.client.post('/api/register', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '0987654321',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('wallet_id', response.json)

    def test_login(self):
        response = self.client.post('/api/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

class WalletTests(BaseTestCase):
    def test_add_money(self):
        response = self.client.post('/api/wallet/add-money', json={
            'wallet_id': self.user.wallet_id,
            'amount': '100.00'
        }, headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('balance', response.json)

    def test_check_balance(self):
        response = self.client.get(f'/api/wallet/{self.user.wallet_id}/balance', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('balance', response.json)

    def test_transaction_history(self):
        response = self.client.get(f'/api/wallet/{self.user.wallet_id}/transactions', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

class AdminTests(BaseTestCase):
    def test_view_all_wallets(self):
        response = self.client.get('/api/admin/wallets?page=1&per_page=10', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.json)

    def test_view_all_transactions(self):
        response = self.client.get('/api/admin/transactions?page=1&per_page=10', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('transactions', response.json)

if __name__ == '__main__':
    unittest.main()