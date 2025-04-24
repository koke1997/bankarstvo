import grpc
from concurrent import futures
import time
import logging
from decimal import Decimal
import datetime

# Import generated protobuf code
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import account_service_pb2, account_service_pb2_grpc

# Import database models and services
from utils.extensions import db
from database.repositories.account_repo import get_account_details, get_account_statement
from database.repositories.balancecheck_repo import get_user_balance
from core.models import Account, User, Transaction

# Update model names to match the actual models
# AccountModel -> Account, UserModel -> User, TransactionModel -> Transaction

# Constants and mapping dictionaries
ACCOUNT_TYPE_MAP = {
    0: 'checking',  # CHECKING
    1: 'savings',   # SAVINGS
    2: 'business',  # BUSINESS
    3: 'investment',# INVESTMENT
    4: 'credit'     # CREDIT
}

ACCOUNT_TYPE_REVERSE_MAP = {v: k for k, v in ACCOUNT_TYPE_MAP.items()}

ACCOUNT_STATUS_MAP = {
    0: True,   # ACTIVE
    1: False,  # INACTIVE
    2: False,  # LOCKED
    3: False   # CLOSED
}


class AccountServicer(account_service_pb2_grpc.AccountServiceServicer):
    """Implementation of AccountService service."""

    def CreateAccount(self, request, context):
        """Creates a new bank account."""
        try:
            # Extract fields from request
            user_id = request.user_id
            account_type = request.account_type
            currency = request.currency
            name = request.name
            initial_deposit = request.initial_deposit
            
            # Create account in database - update to use Account model name
            account = Account(
                user_id=user_id,
                account_type=ACCOUNT_TYPE_MAP[account_type],
                currency_code=currency,
                name=name,
                balance=initial_deposit,
                available_balance=initial_deposit,
                status="active"  # Set status as a string instead of boolean
            )
            db.session.add(account)
            db.session.commit()
            
            # Prepare response
            account_proto = self._account_to_proto(account)
            
            return account_service_pb2.AccountResponse(
                success=True,
                message="Account created successfully",
                account=account_proto
            )
            
        except Exception as e:
            logging.error(f"Error creating account: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating account: {str(e)}")
            return account_service_pb2.AccountResponse(
                success=False,
                message=f"Failed to create account: {str(e)}"
            )

    def GetAccount(self, request, context):
        """Get details of a specific account."""
        try:
            account_id = request.account_id
            user_id = request.user_id
            
            # Use db.session.query instead of Account.query
            account = db.session.query(Account).get(account_id)
            
            # Check if account exists and belongs to the user
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return account_service_pb2.AccountResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return account_service_pb2.AccountResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Prepare response
            account_proto = self._account_to_proto(account)
            
            return account_service_pb2.AccountResponse(
                success=True,
                message="Account retrieved successfully",
                account=account_proto
            )
            
        except Exception as e:
            logging.error(f"Error retrieving account: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving account: {str(e)}")
            return account_service_pb2.AccountResponse(
                success=False,
                message=f"Failed to retrieve account: {str(e)}"
            )
    
    def GetAccounts(self, request, context):
        """Get all accounts for a user."""
        try:
            user_id = request.user_id
            account_type = request.account_type
            status = request.status
            
            # Build query conditions
            conditions = {"user_id": user_id}
            
            if account_type != 0:  # If not default (unspecified)
                conditions["account_type"] = ACCOUNT_TYPE_MAP.get(account_type)
                
            if status != 0:  # If not default (unspecified)
                # Map numerical status to string status - updated from is_active to status
                if status == 1:  # INACTIVE
                    conditions["status"] = "inactive"
                elif status == 2:  # LOCKED
                    conditions["status"] = "locked"
                elif status == 3:  # CLOSED
                    conditions["status"] = "closed"
                else:
                    conditions["status"] = "active"
            
            # Use db.session.query instead of Account.query
            accounts = db.session.query(Account).filter_by(**conditions).all()
            
            # Convert accounts to proto format
            account_protos = [self._account_to_proto(account) for account in accounts]
            
            return account_service_pb2.GetAccountsResponse(
                success=True,
                message=f"Retrieved {len(accounts)} accounts",
                accounts=account_protos,
                total_count=len(accounts)
            )
            
        except Exception as e:
            logging.error(f"Error retrieving accounts: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving accounts: {str(e)}")
            return account_service_pb2.GetAccountsResponse(
                success=False,
                message=f"Failed to retrieve accounts: {str(e)}",
                total_count=0
            )

    def UpdateAccount(self, request, context):
        """Updates an existing account."""
        try:
            account_id = request.account_id
            user_id = request.user_id
            name = request.name
            
            # Use db.session.query instead of Account.query
            account = db.session.query(Account).get(account_id)
            
            # Verify account exists and belongs to user
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return account_service_pb2.AccountResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return account_service_pb2.AccountResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Update account details
            account.name = name
            # Handle the case where last_updated might not exist in the model
            if hasattr(account, 'last_updated'):
                account.last_updated = datetime.datetime.now()
            db.session.commit()
            
            # Prepare response
            account_proto = self._account_to_proto(account)
            
            return account_service_pb2.AccountResponse(
                success=True,
                message="Account updated successfully",
                account=account_proto
            )
            
        except Exception as e:
            logging.error(f"Error updating account: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating account: {str(e)}")
            return account_service_pb2.AccountResponse(
                success=False,
                message=f"Failed to update account: {str(e)}"
            )

    def CloseAccount(self, request, context):
        """Closes an account."""
        try:
            account_id = request.account_id
            user_id = request.user_id
            transfer_to_account_id = request.transfer_remaining_to_account_id
            
            # Use db.session.query instead of Account.query
            account = db.session.query(Account).get(account_id)
            
            # Verify account exists and belongs to user
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return account_service_pb2.CloseAccountResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return account_service_pb2.CloseAccountResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Transfer remaining balance if needed
            if transfer_to_account_id and account.balance > 0:
                # Use db.session.query instead of Account.query
                transfer_account = db.session.query(Account).get(transfer_to_account_id)
                
                if not transfer_account:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Transfer destination account not found")
                    return account_service_pb2.CloseAccountResponse(
                        success=False,
                        message="Transfer destination account not found"
                    )
                    
                if transfer_account.user_id != user_id:
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("User does not have permission to access transfer destination account")
                    return account_service_pb2.CloseAccountResponse(
                        success=False,
                        message="Permission denied for transfer destination account"
                    )
                
                # Perform transfer - null handling
                transfer_account.balance = (transfer_account.balance or 0) + (account.balance or 0)
                # Check if available_balance exists
                if hasattr(transfer_account, 'available_balance') and hasattr(account, 'available_balance'):
                    transfer_account.available_balance = (transfer_account.available_balance or 0) + (account.available_balance or 0)
                db.session.commit()
                
                # Create transaction record for the transfer
                # Note: This would normally use a transaction service
                
            # Close the account - update status field
            account.status = "closed"  # Use status string instead of is_active boolean
            account.balance = 0
            # Check if available_balance exists
            if hasattr(account, 'available_balance'):
                account.available_balance = 0
            # Check if last_updated exists
            if hasattr(account, 'last_updated'):
                account.last_updated = datetime.datetime.now()
            db.session.commit()
            
            return account_service_pb2.CloseAccountResponse(
                success=True,
                message="Account closed successfully"
            )
            
        except Exception as e:
            logging.error(f"Error closing account: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error closing account: {str(e)}")
            return account_service_pb2.CloseAccountResponse(
                success=False,
                message=f"Failed to close account: {str(e)}"
            )

    def GetBalance(self, request, context):
        """Gets the current balance of an account."""
        try:
            account_id = request.account_id
            user_id = request.user_id
            
            # Use db.session.query instead of Account.query
            account = db.session.query(Account).get(account_id)
            
            # Verify account exists and belongs to user
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return account_service_pb2.BalanceResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return account_service_pb2.BalanceResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Get current date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare response - added null handling
            return account_service_pb2.BalanceResponse(
                success=True,
                message="Balance retrieved successfully",
                account_id=str(account.account_id),
                balance=float(account.balance or 0),
                available_balance=float(getattr(account, 'available_balance', account.balance) or 0),
                currency=account.currency_code or '',
                as_of_date=current_date
            )
            
        except Exception as e:
            logging.error(f"Error retrieving balance: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving balance: {str(e)}")
            return account_service_pb2.BalanceResponse(
                success=False,
                message=f"Failed to retrieve balance: {str(e)}"
            )

    def GetBalanceHistory(self, request, context):
        """Gets the balance history of an account over time."""
        # This is a placeholder implementation
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not yet implemented")
        return account_service_pb2.BalanceHistoryResponse(
            success=False,
            message="Method not yet implemented"
        )

    def GetAccountStatement(self, request, context):
        """Gets a statement for an account over a specific time period."""
        # This is a placeholder implementation
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not yet implemented")
        return account_service_pb2.AccountStatementResponse(
            success=False,
            message="Method not yet implemented"
        )

    def GetAccountDetails(self, request, context):
        """Gets detailed information about an account."""
        try:
            account_id = request.account_id
            user_id = request.user_id
            
            # Use db.session.query instead of Account.query
            account = db.session.query(Account).get(account_id)
            
            # Verify account exists and belongs to user
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return account_service_pb2.AccountDetailsResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return account_service_pb2.AccountDetailsResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Get account details - updated to use get_account_details from repository
            try:
                account_details = get_account_details(account_id)
                account_holder_name = account_details.get('account_holder_name', "John Doe")
                bank_name = account_details.get('bank_name', "Bankarstvo Bank")
                bank_address = account_details.get('bank_address', "123 Banking St, Finance City")
            except:
                # Fallback to placeholder values
                account_holder_name = "John Doe"  # Placeholder
                bank_name = "Bankarstvo Bank"     # Placeholder
                bank_address = "123 Banking St, Finance City"  # Placeholder
            
            # Prepare response
            account_proto = self._account_to_proto(account)
            
            return account_service_pb2.AccountDetailsResponse(
                success=True,
                message="Account details retrieved successfully",
                account=account_proto,
                account_holder_name=account_holder_name,
                bank_name=bank_name,
                bank_address=bank_address
            )
            
        except Exception as e:
            logging.error(f"Error retrieving account details: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving account details: {str(e)}")
            return account_service_pb2.AccountDetailsResponse(
                success=False,
                message=f"Failed to retrieve account details: {str(e)}"
            )

    def LockAccount(self, request, context):
        """Locks an account (admin operation)."""
        # This is a placeholder implementation
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not yet implemented")
        return account_service_pb2.LockAccountResponse(
            success=False,
            message="Method not yet implemented"
        )

    def UnlockAccount(self, request, context):
        """Unlocks an account (admin operation)."""
        # This is a placeholder implementation
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not yet implemented")
        return account_service_pb2.UnlockAccountResponse(
            success=False,
            message="Method not yet implemented"
        )

    def ListAllAccounts(self, request, context):
        """Lists all accounts (admin operation)."""
        # This is a placeholder implementation
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not yet implemented")
        return account_service_pb2.ListAllAccountsResponse(
            success=False,
            message="Method not yet implemented"
        )

    def _account_to_proto(self, account):
        """Helper method to convert an account model to a proto message."""
        # Map database status to proto enum - updated to check status string
        # status = 0 if account.is_active else 1  # ACTIVE or INACTIVE
        status_map = {
            'active': 0,    # ACTIVE
            'inactive': 1,  # INACTIVE
            'locked': 2,    # LOCKED
            'closed': 3     # CLOSED
        }
        status = status_map.get(getattr(account, 'status', 'active'), 0)
        
        # Map account type to proto enum - add null handling
        account_type = ACCOUNT_TYPE_REVERSE_MAP.get(account.account_type or 'checking', 0)
        
        # Create and return the proto message - added null handling throughout
        return account_service_pb2.Account(
            account_id=str(account.account_id),
            user_id=account.user_id,
            account_type=account_type,
            status=status,
            currency=account.currency_code or '',
            balance=float(account.balance or 0),
            available_balance=float(getattr(account, 'available_balance', account.balance) or 0),
            name=getattr(account, 'name', ''),
            created_at=str(getattr(account, 'date_created', '')),
            updated_at=str(getattr(account, 'last_updated', '')),
            iban=getattr(account, 'iban', ''),
            swift_bic=getattr(account, 'swift_bic', '')
        )


def serve():
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    account_service_pb2_grpc.add_AccountServiceServicer_to_server(
        AccountServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Account gRPC server started on port 50051")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)
        print("Server stopped")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()