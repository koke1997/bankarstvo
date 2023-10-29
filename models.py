from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    
    # other attributes and methods related to the User class...

class Currency(db.Model):
    __tablename__ = "currencies"
    currency_code = db.Column(db.String(3), primary_key=True)
    currency_name = db.Column(db.String(255), nullable=False)

class Account(db.Model):
    __tablename__ = "accounts"
    
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    balance = db.Column(db.Numeric(20, 2), default=0.00)
    account_type = db.Column(db.String(255))
    account_status = db.Column(db.String(255), default='Active')
