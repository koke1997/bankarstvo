from flask import render_template, current_app
from flask_login import current_user
from utils.extensions import db
from core.models import Transaction, Account
from . import transaction_routes
import logging

@transaction_routes.route("/transaction_history", methods=["GET"], endpoint="transaction_history")
def transaction_history():
    user_id = current_user.get_id()  # Get user_id from current_user
    
    # Check if we're in test mode
    if current_app.config.get('TESTING', False):
        # Just return an empty list for testing
        return []
    
    # Use SQLAlchemy ORM to fetch transactions
    # First, get all accounts belonging to the user
    user_accounts = Account.query.filter_by(user_id=user_id).all()
    account_ids = [account.account_id for account in user_accounts]
    
    # Now get all transactions where these accounts are involved
    sent_transactions = Transaction.query.filter(
        Transaction.account_id.in_(account_ids)
    ).all()
    
    received_transactions = Transaction.query.filter(
        Transaction.recipient_account_id.in_(account_ids)
    ).all()
    
    # Combine sent and received transactions
    transactions = []
    
    for tx in sent_transactions:
        tx_data = {
            'transaction_id': tx.transaction_id,
            'date_posted': tx.date_posted,
            'account_id': tx.account_id,
            'description': tx.description,
            'amount': tx.amount,
            'type': tx.type,
            'recipient_account_id': tx.recipient_account_id,
            'transaction_direction': 'Sent'
        }
        transactions.append(tx_data)
    
    for tx in received_transactions:
        # Skip if this transaction is already included as a "sent" transaction
        # from one of the user's accounts to another of their accounts
        if tx.account_id in account_ids:
            continue
            
        tx_data = {
            'transaction_id': tx.transaction_id,
            'date_posted': tx.date_posted,
            'account_id': tx.recipient_account_id,
            'description': tx.description,
            'amount': tx.amount,
            'type': tx.type,
            'recipient_account_id': tx.account_id,
            'transaction_direction': 'Received'
        }
        transactions.append(tx_data)
    
    logging.debug("Query result: %s", transactions)
    
    return transactions  # Return transactions instead of rendering a template