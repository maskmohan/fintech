
class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@localhost/fintech_wallet'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = '74ed47754a2508bb7ef630353cd2af93b1b6241b1c50ca5d3990dece16e2347b'  # In my local system directly give , it's actual move on env