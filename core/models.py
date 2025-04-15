from datetime import datetime
from utils.extensions import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Numeric
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import logging

logging.basicConfig(level=logging.ERROR)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Multi-factor authentication fields
    two_factor_auth = db.Column(db.Boolean, default=False)
    two_factor_auth_code = db.Column(db.String(255), nullable=True)
    two_factor_auth_expiry = db.Column(db.DateTime, nullable=True)
    two_factor_auth_secret = db.Column(db.String(255), nullable=True)

    account_created = db.Column(db.DateTime, default=func.now())
    last_login = db.Column(db.DateTime, nullable=True)

    @property
    def id(self):
        return self.user_id

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Transaction(db.Model):
    __tablename__ = "transactions"
    transaction_id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(
        db.String(10), nullable=False
    )  # 'deposit', 'withdraw', or 'transfer'

    def __repr__(self):
        return f"Transaction('{self.date_posted}', '{self.description}', '{self.amount}', Type: '{self.type}')"


class Account(db.Model):
    __tablename__ = "accounts"
    account_id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(20, 2), nullable=True)
    currency_code = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

    def __repr__(self):
        return f"<Account {self.account_name}, Country Code: {self.country_code}, User ID: {self.user_id}>"


class SignedDocument(db.Model):
    __tablename__ = "signed_documents"
    document_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.transaction_id"))
    transaction = relationship("Transaction", backref="signed_documents")
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    document_type = db.Column(db.String(255), nullable=True)
    additional_info = db.Column(db.Text, nullable=True)
    sender = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.Text, nullable=False)  # Stores the base64 image

    def __repr__(self):
        return f"Document(User ID: '{self.user_id}', Transaction ID: '{self.transaction_id}', Timestamp: '{self.timestamp}', Sender: '{self.sender}', Receiver: '{self.receiver}')"


class CryptoAsset(db.Model):
    __tablename__ = "crypto_assets"
    asset_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    balance = db.Column(db.Numeric(20, 8), nullable=False)

    def __repr__(self):
        return f"CryptoAsset('{self.name}', '{self.symbol}', Balance: '{self.balance}')"


class StockAsset(db.Model):
    __tablename__ = "stock_assets"
    asset_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    shares = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"StockAsset('{self.name}', '{self.symbol}', Shares: '{self.shares}')"


class MarketplaceItem(db.Model):
    __tablename__ = "marketplace_items"
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(20, 2), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="available")

    def __repr__(self):
        return f"MarketplaceItem('{self.name}', Price: '{self.price}', Status: '{self.status}')"


class MarketplaceTransaction(db.Model):
    __tablename__ = "marketplace_transactions"
    transaction_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("marketplace_items.item_id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Numeric(20, 2), nullable=False)

    def __repr__(self):
        return f"MarketplaceTransaction(Item ID: '{self.item_id}', Buyer ID: '{self.buyer_id}', Seller ID: '{self.seller_id}', Amount: '{self.amount}')"


class Loan(db.Model):
    __tablename__ = "loans"
    loan_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term = db.Column(db.Integer, nullable=False)  # Term in months
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="active")

    def __repr__(self):
        return f"Loan(User ID: '{self.user_id}', Amount: '{self.amount}', Interest Rate: '{self.interest_rate}', Term: '{self.term}', Status: '{self.status}')"


class Payment(db.Model):
    __tablename__ = "payments"
    payment_id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey("loans.loan_id"), nullable=False)
    amount = db.Column(db.Numeric(20, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default="completed")

    def __repr__(self):
        return f"Payment(Loan ID: '{self.loan_id}', Amount: '{self.amount}', Payment Date: '{self.payment_date}', Status: '{self.status}')"
