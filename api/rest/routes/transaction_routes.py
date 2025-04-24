from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from core.models import Account, Transaction
from utils.extensions import db
import logging
from datetime import datetime, timedelta

# Create a blueprint for transaction API endpoints
transaction_api = Blueprint('transaction_api', __name__)
logger = logging.getLogger(__name__)

@transaction_api.route('/accounts/<int:account_id>/transactions', methods=['GET'])
@login_required
def get_account_transactions(account_id):
    """
    Get all transactions for a specific account
    Optional query parameters:
    - startDate (YYYY-MM-DD)
    - endDate (YYYY-MM-DD)
    - type (deposit, withdraw, transfer)
    - minAmount
    - maxAmount
    """
    try:
        user_id = current_user.get_id()
        
        # First check if the account belongs to the current user
        account = Account.query.filter_by(account_id=account_id, user_id=user_id).first()
        if not account:
            return jsonify({"error": "Account not found or not authorized"}), 404
        
        # Start with base query
        query = Transaction.query.filter_by(account_id=account_id)
        
        # Apply filters based on query parameters
        if request.args.get('startDate'):
            try:
                start_date = datetime.strptime(request.args.get('startDate'), '%Y-%m-%d')
                query = query.filter(Transaction.date_posted >= start_date)
            except ValueError:
                return jsonify({"error": "Invalid startDate format. Use YYYY-MM-DD"}), 400
                
        if request.args.get('endDate'):
            try:
                end_date = datetime.strptime(request.args.get('endDate'), '%Y-%m-%d')
                # Include the whole day by adding one day and subtracting one second
                end_date = end_date + timedelta(days=1) - timedelta(seconds=1)
                query = query.filter(Transaction.date_posted <= end_date)
            except ValueError:
                return jsonify({"error": "Invalid endDate format. Use YYYY-MM-DD"}), 400
        
        if request.args.get('type'):
            transaction_type = request.args.get('type')
            query = query.filter(Transaction.type == transaction_type)
            
        if request.args.get('minAmount'):
            try:
                min_amount = float(request.args.get('minAmount'))
                query = query.filter(Transaction.amount >= min_amount)
            except ValueError:
                return jsonify({"error": "Invalid minAmount format. Must be a number"}), 400
                
        if request.args.get('maxAmount'):
            try:
                max_amount = float(request.args.get('maxAmount'))
                query = query.filter(Transaction.amount <= max_amount)
            except ValueError:
                return jsonify({"error": "Invalid maxAmount format. Must be a number"}), 400
        
        # Order by date, most recent first
        transactions = query.order_by(Transaction.date_posted.desc()).all()
        
        # Convert transactions to JSON serializable format
        transactions_data = []
        for transaction in transactions:
            transactions_data.append({
                'transaction_id': transaction.transaction_id,
                'account_id': transaction.account_id,
                'amount': float(transaction.amount),
                'type': transaction.type,
                'description': transaction.description,
                'date_posted': transaction.date_posted.isoformat(),
                'recipient_account_id': transaction.recipient_account_id
            })
        
        return jsonify(transactions_data)
    except Exception as e:
        logger.error(f"Error retrieving account transactions: {e}")
        return jsonify({"error": str(e)}), 500

@transaction_api.route('/transactions/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction_details(transaction_id):
    """
    Get details for a specific transaction
    Returns a single transaction object
    """
    try:
        user_id = current_user.get_id()
        
        # Find the transaction
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404
        
        # Check if the transaction belongs to an account owned by the current user
        account = Account.query.filter_by(account_id=transaction.account_id, user_id=user_id).first()
        if not account:
            return jsonify({"error": "Not authorized to view this transaction"}), 403
        
        # Convert transaction to JSON serializable format
        transaction_data = {
            'transaction_id': transaction.transaction_id,
            'account_id': transaction.account_id,
            'amount': float(transaction.amount),
            'type': transaction.type,
            'description': transaction.description,
            'date_posted': transaction.date_posted.isoformat(),
            'recipient_account_id': transaction.recipient_account_id
        }
        
        return jsonify(transaction_data)
    except Exception as e:
        logger.error(f"Error retrieving transaction details: {e}")
        return jsonify({"error": str(e)}), 500

@transaction_api.route('/transactions/<int:transaction_id>/receipt', methods=['GET'])
@login_required
def get_transaction_receipt(transaction_id):
    """
    Generate and return a receipt/PDF for a specific transaction
    Returns a PDF file
    """
    try:
        user_id = current_user.get_id()
        
        # Find the transaction
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404
        
        # Check if the transaction belongs to an account owned by the current user
        account = Account.query.filter_by(account_id=transaction.account_id, user_id=user_id).first()
        if not account:
            return jsonify({"error": "Not authorized to view this transaction"}), 403
        
        # In a real implementation, you would generate a PDF here
        # For now, we'll just return a placeholder JSON response
        return jsonify({
            "message": "Receipt generation not yet implemented",
            "transaction_id": transaction_id
        })
    except Exception as e:
        logger.error(f"Error generating transaction receipt: {e}")
        return jsonify({"error": str(e)}), 500