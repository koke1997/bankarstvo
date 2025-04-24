from decimal import Decimal
import logging
from datetime import datetime
from utils.extensions import db
from core.models import Account, Transaction, User
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

def process_deposit(account_id, amount, description="Deposit"):
    """
    Process a deposit transaction for an account
    
    Args:
        account_id: The ID of the account to deposit to
        amount: The amount to deposit
        description: Description of the transaction
        
    Returns:
        Tuple of (success status, message, transaction or None)
    """
    try:
        # Validate inputs
        if not account_id or not amount:
            return False, "Invalid account ID or amount", None
            
        if amount <= 0:
            return False, "Amount must be greater than zero", None
            
        # Find the account - use db.session.query instead of Account.query
        account = db.session.query(Account).filter_by(account_id=account_id).first()
        if not account:
            return False, f"Account {account_id} not found", None
            
        # Update account balance
        if account.balance is None:
            account.balance = Decimal('0')
        account.balance += Decimal(str(amount))
        
        # Create transaction record with proper initialization
        transaction = Transaction(
            account_id=account_id,
            description=description,
            amount=float(amount),
            type='deposit'
        )
        
        # Save changes
        db.session.add(transaction)
        db.session.commit()
        
        return True, "Deposit successful", transaction
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during deposit: {str(e)}")
        return False, f"Database error: {str(e)}", None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing deposit: {str(e)}")
        return False, f"Error: {str(e)}", None

def process_withdrawal(account_id, amount, description="Withdrawal"):
    """
    Process a withdrawal transaction from an account
    
    Args:
        account_id: The ID of the account to withdraw from
        amount: The amount to withdraw
        description: Description of the transaction
        
    Returns:
        Tuple of (success status, message, transaction or None)
    """
    try:
        # Validate inputs
        if not account_id or not amount:
            return False, "Invalid account ID or amount", None
            
        if amount <= 0:
            return False, "Amount must be greater than zero", None
            
        # Find the account - use db.session.query instead of Account.query
        account = db.session.query(Account).filter_by(account_id=account_id).first()
        if not account:
            return False, f"Account {account_id} not found", None
            
        # Check if sufficient funds
        if account.balance is None or account.balance < Decimal(str(amount)):
            return False, "Insufficient funds", None
            
        # Update account balance
        account.balance -= Decimal(str(amount))
        
        # Create transaction record with proper initialization 
        transaction = Transaction(
            account_id=account_id,
            description=description,
            amount=float(amount) * -1,  # Negative amount for withdrawal
            type='withdraw'
        )
        
        # Save changes
        db.session.add(transaction)
        db.session.commit()
        
        return True, "Withdrawal successful", transaction
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during withdrawal: {str(e)}")
        return False, f"Database error: {str(e)}", None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing withdrawal: {str(e)}")
        return False, f"Error: {str(e)}", None

def process_transfer(from_account_id, to_account_id, amount, description="Transfer"):
    """
    Process a transfer transaction between accounts
    
    Args:
        from_account_id: The ID of the source account
        to_account_id: The ID of the destination account
        amount: The amount to transfer
        description: Description of the transaction
        
    Returns:
        Tuple of (success status, message, transaction or None)
    """
    try:
        # Validate inputs
        if not from_account_id or not to_account_id or not amount:
            return False, "Invalid account IDs or amount", None
            
        if amount <= 0:
            return False, "Amount must be greater than zero", None
            
        if from_account_id == to_account_id:
            return False, "Cannot transfer to the same account", None
            
        # Find accounts - use db.session.query instead of Account.query
        from_account = db.session.query(Account).filter_by(account_id=from_account_id).first()
        if not from_account:
            return False, f"Source account {from_account_id} not found", None
            
        to_account = db.session.query(Account).filter_by(account_id=to_account_id).first()
        if not to_account:
            return False, f"Destination account {to_account_id} not found", None
            
        # Check if sufficient funds
        if from_account.balance is None or from_account.balance < Decimal(str(amount)):
            return False, "Insufficient funds", None
        
        # Check currency compatibility - only allow transfers between same currency
        if from_account.currency_code != to_account.currency_code:
            return False, "Currency mismatch between accounts", None
            
        # Update account balances
        from_account.balance -= Decimal(str(amount))
        
        if to_account.balance is None:
            to_account.balance = Decimal('0')
        to_account.balance += Decimal(str(amount))
        
        # Create transaction records with proper initialization
        source_transaction = Transaction(
            account_id=from_account_id,
            description=f"{description} to {to_account_id}",
            amount=float(amount) * -1,  # Negative amount for sender
            type='transfer',
            recipient_account_id=to_account_id
        )
        
        destination_transaction = Transaction(
            account_id=to_account_id,
            description=f"{description} from {from_account_id}",
            amount=float(amount),  # Positive amount for receiver
            type='transfer'
        )
        
        # Save changes
        db.session.add(source_transaction)
        db.session.add(destination_transaction)
        db.session.commit()
        
        return True, "Transfer successful", source_transaction
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during transfer: {str(e)}")
        return False, f"Database error: {str(e)}", None
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing transfer: {str(e)}")
        return False, f"Error: {str(e)}", None

def get_transaction_history(user_id, account_id=None, start_date=None, end_date=None, transaction_type=None, limit=100, offset=0):
    """
    Get transaction history for a user or specific account
    
    Args:
        user_id: The ID of the user
        account_id: Optional account ID to filter by
        start_date: Optional start date to filter by
        end_date: Optional end date to filter by
        transaction_type: Optional transaction type to filter by
        limit: Maximum number of transactions to return
        offset: Offset for pagination
        
    Returns:
        List of transactions
    """
    try:
        # Find all accounts for this user
        user_accounts = db.session.query(Account).filter_by(user_id=user_id).all()
        if not user_accounts:
            return []
            
        # Get all account IDs for this user
        account_ids = [account.account_id for account in user_accounts]
        
        # Start with basic query using SQLAlchemy's session query
        query = db.session.query(Transaction).filter(Transaction.account_id.in_(account_ids))
        
        # Apply filters if provided
        if account_id:
            # Verify the account belongs to the user
            if account_id in account_ids:
                query = query.filter_by(account_id=account_id)
            else:
                return []
                
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Transaction.date_posted >= start_date)
            
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Transaction.date_posted <= end_date)
            
        if transaction_type:
            query = query.filter_by(type=transaction_type)
            
        # Order by date (newest first) and limit results
        transactions = query.order_by(Transaction.date_posted.desc()).offset(offset).limit(limit).all()
        
        return transactions
    except SQLAlchemyError as e:
        logger.error(f"Database error getting transaction history: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error getting transaction history: {str(e)}")
        return []

