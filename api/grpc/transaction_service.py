import grpc
from concurrent import futures
import time
import logging
from decimal import Decimal

# Import generated protobuf code
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import transaction_service_pb2, transaction_service_pb2_grpc

# Import database models and handlers
from utils.extensions import db
from database.repositories.transaction_repo import (
    process_deposit,
    process_withdrawal,
    process_transfer,
    get_transaction_history
)
from core.models import Account, User, Transaction

# Update model names to match the actual models
# AccountModel -> Account, UserModel -> User, TransactionModel -> Transaction

class TransactionServicer(transaction_service_pb2_grpc.TransactionServiceServicer):
    """Implementation of TransactionService service."""

    def CreateDeposit(self, request, context):
        """Process a deposit transaction."""
        try:
            # Extract fields from request
            account_id = request.account_id
            user_id = request.user_id
            amount = request.amount
            description = request.description or "Deposit"
            
            # Use db.session.query instead of AccountModel.query
            account = db.session.query(Account).get(account_id)
            
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Process deposit
            success, message, transaction = process_deposit(
                account_id, amount, description
            )
            
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(message)
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message=message
                )
            
            # Prepare transaction response - handle potential None values safely
            transaction_proto = transaction_service_pb2.Transaction(
                transaction_id=str(transaction.transaction_id),
                account_id=str(transaction.account_id),
                user_id=user_id,  # Use the provided user_id since this might not be in the transaction
                transaction_type=transaction_service_pb2.TransactionType.DEPOSIT,
                amount=float(transaction.amount or 0),
                balance_after=float(account.balance or 0),
                description=transaction.description or "",
                created_at=str(transaction.date_posted or ""),
                status=transaction_service_pb2.TransactionStatus.COMPLETED
            )
            
            return transaction_service_pb2.TransactionResponse(
                success=True,
                message="Deposit processed successfully",
                transaction=transaction_proto
            )
            
        except Exception as e:
            logging.error(f"Error processing deposit: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error processing deposit: {str(e)}")
            return transaction_service_pb2.TransactionResponse(
                success=False,
                message=f"Failed to process deposit: {str(e)}"
            )

    def CreateWithdrawal(self, request, context):
        """Process a withdrawal transaction."""
        try:
            # Extract fields from request
            account_id = request.account_id
            user_id = request.user_id
            amount = request.amount
            description = request.description or "Withdrawal"
            
            # Use db.session.query instead of AccountModel.query
            account = db.session.query(Account).get(account_id)
            
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Process withdrawal with correct parameter order matching the function
            success, message, transaction = process_withdrawal(
                account_id, amount, description
            )
            
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(message)
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message=message
                )
            
            # Prepare transaction response - handle potential None values safely
            transaction_proto = transaction_service_pb2.Transaction(
                transaction_id=str(transaction.transaction_id),
                account_id=str(transaction.account_id),
                user_id=user_id,  # Use the provided user_id since this might not be in the transaction
                transaction_type=transaction_service_pb2.TransactionType.WITHDRAWAL,
                amount=float(transaction.amount or 0),
                balance_after=float(account.balance or 0),
                description=transaction.description or "",
                created_at=str(transaction.date_posted or ""),
                status=transaction_service_pb2.TransactionStatus.COMPLETED
            )
            
            return transaction_service_pb2.TransactionResponse(
                success=True,
                message="Withdrawal processed successfully",
                transaction=transaction_proto
            )
            
        except Exception as e:
            logging.error(f"Error processing withdrawal: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error processing withdrawal: {str(e)}")
            return transaction_service_pb2.TransactionResponse(
                success=False,
                message=f"Failed to process withdrawal: {str(e)}"
            )

    def CreateTransfer(self, request, context):
        """Process a transfer transaction."""
        try:
            # Extract fields from request
            from_account_id = request.from_account_id
            to_account_id = request.to_account_id
            user_id = request.user_id
            amount = request.amount
            description = request.description or "Transfer"
            
            # Use db.session.query instead of AccountModel.query
            from_account = db.session.query(Account).get(from_account_id)
            
            if not from_account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Source account not found")
                return transaction_service_pb2.TransferResponse(
                    success=False,
                    message="Source account not found"
                )
                
            if from_account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access the source account")
                return transaction_service_pb2.TransferResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Validate destination account exists - use db.session.query
            to_account = db.session.query(Account).get(to_account_id)
            if not to_account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Destination account not found")
                return transaction_service_pb2.TransferResponse(
                    success=False,
                    message="Destination account not found"
                )
            
            # Process transfer with correct parameter order matching the function
            success, message, transaction = process_transfer(
                from_account_id, to_account_id, amount, description
            )
            
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(message)
                return transaction_service_pb2.TransferResponse(
                    success=False,
                    message=message
                )
            
            # In the updated repository, process_transfer only returns one transaction
            # We need to adjust our expectations accordingly
            source_tx = transaction
            
            # Create a simplified response - handle the case where destination_tx doesn't exist
            source_tx_proto = transaction_service_pb2.Transaction(
                transaction_id=str(source_tx.transaction_id),
                account_id=str(source_tx.account_id),
                user_id=user_id,  # Use the provided user_id
                transaction_type=transaction_service_pb2.TransactionType.TRANSFER_OUT,
                amount=float(source_tx.amount or 0),
                balance_after=float(from_account.balance or 0),
                description=source_tx.description or "",
                created_at=str(source_tx.date_posted or ""),
                status=transaction_service_pb2.TransactionStatus.COMPLETED
            )
            
            # Create a placeholder for destination transaction since our implementation changed
            destination_tx_proto = transaction_service_pb2.Transaction(
                transaction_id="0",  # Placeholder ID
                account_id=str(to_account_id),
                user_id=to_account.user_id,
                transaction_type=transaction_service_pb2.TransactionType.TRANSFER_IN,
                amount=float(amount),  # Use the original amount
                balance_after=float(to_account.balance or 0),
                description=description,
                created_at=str(source_tx.date_posted or ""),
                status=transaction_service_pb2.TransactionStatus.COMPLETED
            )
            
            return transaction_service_pb2.TransferResponse(
                success=True,
                message="Transfer processed successfully",
                source_transaction=source_tx_proto,
                destination_transaction=destination_tx_proto
            )
            
        except Exception as e:
            logging.error(f"Error processing transfer: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error processing transfer: {str(e)}")
            return transaction_service_pb2.TransferResponse(
                success=False,
                message=f"Failed to process transfer: {str(e)}"
            )

    def GetTransactionHistory(self, request, context):
        """Get transaction history for an account."""
        try:
            # Extract fields from request
            account_id = request.account_id
            user_id = request.user_id
            start_date = request.start_date
            end_date = request.end_date
            transaction_type = request.transaction_type
            limit = request.limit or 50
            offset = request.offset or 0
            
            # Use db.session.query instead of AccountModel.query
            account = db.session.query(Account).get(account_id)
            
            if not account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found")
                return transaction_service_pb2.TransactionHistoryResponse(
                    success=False,
                    message="Account not found"
                )
                
            if account.user_id != user_id:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("User does not have permission to access this account")
                return transaction_service_pb2.TransactionHistoryResponse(
                    success=False,
                    message="Permission denied"
                )
            
            # Get transaction history - adjusted to match the updated function signature
            transactions = get_transaction_history(
                user_id, account_id, start_date, end_date, 
                transaction_type=transaction_type, limit=limit, offset=offset
            )
            
            # Assuming get_transaction_history returns a list but not a count now
            total_count = len(transactions)
            
            # Map transaction types to proto enum
            tx_type_map = {
                'deposit': transaction_service_pb2.TransactionType.DEPOSIT,
                'withdraw': transaction_service_pb2.TransactionType.WITHDRAWAL,  # Updated to 'withdraw'
                'transfer': transaction_service_pb2.TransactionType.TRANSFER_OUT,
                'payment': transaction_service_pb2.TransactionType.PAYMENT,
                'fee': transaction_service_pb2.TransactionType.FEE,
                'interest': transaction_service_pb2.TransactionType.INTEREST
            }
            
            # Prepare transaction responses - handle potential None values
            transaction_protos = []
            for tx in transactions:
                tx_proto = transaction_service_pb2.Transaction(
                    transaction_id=str(tx.transaction_id),
                    account_id=str(tx.account_id),
                    user_id=user_id,  # Use the provided user_id
                    transaction_type=tx_type_map.get(
                        tx.type,  # Updated from tx.transaction_type to tx.type
                        transaction_service_pb2.TransactionType.OTHER
                    ),
                    amount=float(tx.amount or 0),
                    description=tx.description or "",
                    created_at=str(tx.date_posted or ""),
                    status=transaction_service_pb2.TransactionStatus.COMPLETED,
                    # Handle the case where tx might not have a recipient_account_id attribute
                    reference_id=str(getattr(tx, 'recipient_account_id', '')) if hasattr(tx, 'recipient_account_id') else ""
                )
                transaction_protos.append(tx_proto)
            
            return transaction_service_pb2.TransactionHistoryResponse(
                success=True,
                message=f"Retrieved {len(transactions)} transactions",
                transactions=transaction_protos,
                total_count=total_count,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logging.error(f"Error retrieving transaction history: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error retrieving transaction history: {str(e)}")
            return transaction_service_pb2.TransactionHistoryResponse(
                success=False,
                message=f"Failed to retrieve transaction history: {str(e)}"
            )

def serve():
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    transaction_service_pb2_grpc.add_TransactionServiceServicer_to_server(
        TransactionServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Transaction gRPC server started on port 50052")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)
        print("Server stopped")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()