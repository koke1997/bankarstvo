from utils.extensions import db
from core.models import User, Account
from datetime import datetime


def get_account_details(user_id):
    """Get user account details using SQLAlchemy instead of raw SQL."""
    try:
        # Use SQLAlchemy to query the database instead of raw SQL
        user = db.session.query(User).filter_by(user_id=user_id).first()
        
        if user:
            return {
                'username': user.username,
                'email': user.email,
                'account_created': getattr(user, 'date_created', None),
                'last_login': getattr(user, 'last_login', None)
            }
        return None
    except Exception as e:
        print(f"Error getting account details: {e}")
        return None


def create_account(user_id, account_type, currency_code, name=None, initial_balance=0.0):
    """Create a new account for a user."""
    try:
        # Check if user exists
        user = db.session.query(User).filter_by(user_id=user_id).first()
        if not user:
            return False, "User not found"
        
        # Create new account
        account = Account(
            user_id=user_id,
            account_type=account_type,
            currency_code=currency_code,
            name=name or f"{account_type.capitalize()} Account",
            balance=initial_balance,
            status="active",
            date_created=datetime.now()
        )
        
        db.session.add(account)
        db.session.commit()
        
        return True, account
    except Exception as e:
        db.session.rollback()
        print(f"Error creating account: {e}")
        return False, f"Failed to create account: {str(e)}"


def update_account(account_id, user_id, **updates):
    """Update an existing account."""
    try:
        # Find the account
        account = db.session.query(Account).filter_by(account_id=account_id, user_id=user_id).first()
        
        if not account:
            return False, "Account not found or does not belong to user"
        
        # Apply updates to allowed fields only
        allowed_fields = ['name', 'status']
        for field, value in updates.items():
            if field in allowed_fields and hasattr(account, field):
                setattr(account, field, value)
        
        # Update last_updated timestamp if the model has it
        if hasattr(account, 'last_updated'):
            account.last_updated = datetime.now()
        
        db.session.commit()
        return True, account
    except Exception as e:
        db.session.rollback()
        print(f"Error updating account: {e}")
        return False, f"Failed to update account: {str(e)}"


def get_user_accounts(user_id, account_type=None, status=None):
    """Get all accounts for a user with optional filtering."""
    try:
        # Start with basic query
        query = db.session.query(Account).filter_by(user_id=user_id)
        
        # Apply filters if provided
        if account_type:
            query = query.filter_by(account_type=account_type)
        
        if status:
            query = query.filter_by(status=status)
        
        # Execute query
        accounts = query.all()
        return accounts
    except Exception as e:
        print(f"Error getting user accounts: {e}")
        return []


def close_account(account_id, user_id, transfer_to_account_id=None):
    """Close an account, optionally transferring remaining balance."""
    try:
        # Find the account
        account = db.session.query(Account).filter_by(account_id=account_id, user_id=user_id).first()
        
        if not account:
            return False, "Account not found or does not belong to user"
        
        # Check if account has balance
        if account.balance > 0:
            if transfer_to_account_id:
                # Find the destination account
                transfer_account = db.session.query(Account).filter_by(
                    account_id=transfer_to_account_id, user_id=user_id
                ).first()
                
                if not transfer_account:
                    return False, "Transfer destination account not found"
                
                # Transfer the balance
                transfer_account.balance = (transfer_account.balance or 0) + account.balance
                
                # Create a transfer transaction (would need a transaction service)
                # This would be handled by the transaction service in a real implementation
            else:
                return False, "Account has balance but no transfer destination provided"
        
        # Close the account
        account.status = "closed"
        account.balance = 0
        
        # Update last_updated timestamp if the model has it
        if hasattr(account, 'last_updated'):
            account.last_updated = datetime.now()
        
        db.session.commit()
        return True, "Account closed successfully"
    except Exception as e:
        db.session.rollback()
        print(f"Error closing account: {e}")
        return False, f"Failed to close account: {str(e)}"
