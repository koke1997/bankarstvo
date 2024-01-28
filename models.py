from datetime import datetime
from extensions import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Numeric

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    two_factor_auth = db.Column(db.String(255), nullable=True)
    account_created = db.Column(db.DateTime, default=func.now())
    last_login = db.Column(db.DateTime, nullable=True)

    # If you have a balance column, add it here, otherwise remove it from __repr__
    # balance = db.Column(db.Float, nullable=False, default=0.0)
    @property
    def id(self):
        return self.user_id

    def __repr__(self):
        # Make sure all referenced fields exist in this class.
        return f"User('{self.username}', '{self.email}')"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'deposit', 'withdraw', or 'transfer'

    def __repr__(self):
        return f"Transaction('{self.date_posted}', '{self.description}', '{self.amount}', Type: '{self.type}')"

class Account(db.Model):
    __tablename__ = 'accounts'
    account_id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(20, 2), nullable=True)
    currency_code = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"<Account {self.account_name}, Country Code: {self.country_code}, User ID: {self.user_id}>"
    
class SignedDocument(db.Model):
    __tablename__ = 'signed_documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Include user_id
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    document_type = db.Column(db.String(255), nullable=True)
    additional_info = db.Column(db.Text, nullable=True)
    sender = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.Text, nullable=False)  # Stores the base64 image

    def __repr__(self):
        return f"Document(User ID: '{self.user_id}', Transaction ID: '{self.transaction_id}', Timestamp: '{self.timestamp}', Sender: '{self.sender}', Receiver: '{self.receiver}')"


