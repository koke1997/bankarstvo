from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from core.models import Account, User
from utils.extensions import db
import logging

# Create a blueprint for account API endpoints
account_api = Blueprint('account_api', __name__)
logger = logging.getLogger(__name__)

@account_api.route('/accounts', methods=['GET'])
@login_required
def get_user_accounts():
    """
    Get all accounts for the current authenticated user
    Returns a list of account objects
    """
    try:
        user_id = current_user.get_id()
        accounts = Account.query.filter_by(user_id=user_id).all()
        
        # Convert accounts to JSON serializable format
        accounts_data = []
        for account in accounts:
            accounts_data.append({
                'account_id': account.account_id,
                'account_type': account.account_type,
                'balance': float(account.balance),
                'currency_code': account.currency_code,
                'user_id': account.user_id
            })
        
        return jsonify(accounts_data)
    except Exception as e:
        logger.error(f"Error retrieving user accounts: {e}")
        return jsonify({"error": str(e)}), 500

@account_api.route('/accounts/<int:account_id>', methods=['GET'])
@login_required
def get_account_details(account_id):
    """
    Get details for a specific account
    Returns a single account object
    """
    try:
        user_id = current_user.get_id()
        account = Account.query.filter_by(account_id=account_id, user_id=user_id).first()
        
        if not account:
            return jsonify({"error": "Account not found or not authorized"}), 404
        
        # Convert account to JSON serializable format
        account_data = {
            'account_id': account.account_id,
            'account_type': account.account_type,
            'balance': float(account.balance),
            'currency_code': account.currency_code,
            'user_id': account.user_id
        }
        
        return jsonify(account_data)
    except Exception as e:
        logger.error(f"Error retrieving account details: {e}")
        return jsonify({"error": str(e)}), 500

@account_api.route('/accounts', methods=['POST'])
@login_required
def create_account():
    """
    Create a new account for the current user
    Expects JSON with account_type, currency_code, and optional initial_balance
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['account_type', 'currency_code']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        user_id = current_user.get_id()
        
        # Check if account with same type and currency already exists
        existing_account = Account.query.filter_by(
            user_id=user_id,
            account_type=data['account_type'],
            currency_code=data['currency_code']
        ).first()
        
        if existing_account:
            return jsonify({"error": "Account with this type and currency already exists"}), 400
        
        initial_balance = data.get('initial_balance', 0.0)
        
        # Create new account
        new_account = Account(
            user_id=user_id,
            account_type=data['account_type'],
            balance=initial_balance,
            currency_code=data['currency_code']
        )
        
        db.session.add(new_account)
        db.session.commit()
        
        # Return the created account
        return jsonify({
            'account_id': new_account.account_id,
            'account_type': new_account.account_type,
            'balance': float(new_account.balance),
            'currency_code': new_account.currency_code,
            'user_id': new_account.user_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating account: {e}")
        return jsonify({"error": str(e)}), 500

@account_api.route('/accounts/<int:account_id>/transfer', methods=['POST'])
@login_required
def transfer_money(account_id):
    """
    Transfer money from one account to another
    Expects JSON with amount, recipient_account_id, and optional description
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['amount', 'recipient_account_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        user_id = current_user.get_id()
        source_account = Account.query.filter_by(account_id=account_id, user_id=user_id).first()
        
        if not source_account:
            return jsonify({"error": "Source account not found or not authorized"}), 404
        
        recipient_account_id = data['recipient_account_id']
        recipient_account = Account.query.filter_by(account_id=recipient_account_id).first()
        
        if not recipient_account:
            return jsonify({"error": "Recipient account not found"}), 404
        
        amount = float(data['amount'])
        
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
        
        if source_account.balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400
        
        description = data.get('description', f'Transfer to account {recipient_account_id}')
        
        # Perform the transfer
        source_account.balance -= amount
        recipient_account.balance += amount
        
        # Create transaction records (you would implement this based on your transaction model)
        # This is just a placeholder for the actual transaction creation logic
        
        db.session.commit()
        
        return jsonify({
            "message": "Transfer successful",
            "new_balance": float(source_account.balance)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error transferring money: {e}")
        return jsonify({"error": str(e)}), 500

@account_api.route('/search/accounts', methods=['GET'])
@login_required
def search_accounts():
    """
    Search for accounts by username
    Expects query parameter 'username'
    """
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({"error": "Username parameter is required"}), 400
        
        # Find user by username
        user = User.query.filter(User.username.like(f"%{username}%")).first()
        
        if not user:
            return jsonify([])
        
        # Get accounts for the found user
        accounts = Account.query.filter_by(user_id=user.user_id).all()
        
        # Don't return the current user's accounts
        current_user_id = current_user.get_id()
        accounts = [account for account in accounts if account.user_id != int(current_user_id)]
        
        # Convert accounts to JSON serializable format
        accounts_data = []
        for account in accounts:
            accounts_data.append({
                'account_id': account.account_id,
                'account_type': account.account_type,
                'currency_code': account.currency_code,
                'user_id': account.user_id,
                'username': user.username
            })
        
        return jsonify(accounts_data)
    except Exception as e:
        logger.error(f"Error searching accounts: {e}")
        return jsonify({"error": str(e)}), 500