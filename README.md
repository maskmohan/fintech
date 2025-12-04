# Fintech Wallet System

Welcome to the Fintech Wallet System! This project is a simple and secure wallet management system built with Flask. It includes features for user registration, wallet operations, and an admin dashboard.

## Features

- **User Registration**: Register new users with name, email, phone number, and password.
- **User Login**: Authenticate users and provide JWT tokens for secure access.
- **Wallet Operations**: Add money, check balance, and view transaction history.
- **Admin Dashboard**: View all wallets and transactions with pagination support.
- **API Documentation**: Interactive API documentation using Swagger..

## Getting Started

### Prerequisites

- Python 3.7+
- PostgreSQL
- Virtualenv (optional but recommended)

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/fintech-wallet.git
    cd fintech-wallet
    ```

2. **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database**:
    - Ensure PostgreSQL is running and create a database named `fintech_wallet`.
    - Update the `DATABASE_URL` in the `.env` file with your PostgreSQL connection string.

5. **Run database migrations**:
    ```bash
    flask db upgrade
    ```

6. **Run the application**:
    ```bash
    flask run
    ```

### Running Tests

To run the unit tests, use the following command:

```bash
python -m unittest discover -s tests

PI Documentation
The API documentation is available at /api/docs when the application is running. It provides interactive documentation for all available endpoints.

Deployment
Using Gunicorn and Nginx
Install Gunicorn:

pip install gunicorn
Run Gunicorn:

gunicorn -c gunicorn_config.py app:app
Set up Nginx:

Install Nginx: sudo apt install nginx
Configure Nginx to proxy requests to Gunicorn.
Environment Variables
Ensure the following environment variables are set in your production environment:

FLASK_APP: Set to app.py
FLASK_ENV: Set to production
DATABASE_URL: Your PostgreSQL connection string
JWT_SECRET_KEY: A secure secret key for JWT

Acknowledgements
Flask
SQLAlchemy
Flask-Migrate
Flask-JWT-Extended
Flask-Swagger-UI
Feel free to customize this README.md file to better suit your project's needs. Let me know if you need any further assistance!
