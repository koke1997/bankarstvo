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
from DatabaseHandling.connection import get_db_connection
from FiatHandling.deposit import process_deposit
from FiatHandling.withdraw import process_withdrawal
from FiatHandling.fundtransfer import process_transfer
from FiatHandling.transactionhistory import get_transaction_history
from core.models import TransactionModel, AccountModel


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
            
            # Validate user owns the account
            db_connection = get_db_connection()
            account = AccountModel.find_by_id(db_connection, account_id)
            
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
                db_connection, user_id, account_id, amount, description
            )
            
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(message)
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message=message
                )
            
            # Prepare transaction response
            transaction_proto = transaction_service_pb2.Transaction(
                transaction_id=str(transaction.transaction_id),
                account_id=str(transaction.account_id),
                user_id=transaction.user_id,
                transaction_type=transaction_service_pb2.TransactionType.DEPOSIT,
                amount=float(transaction.amount),
                balance_after=float(account.balance),
                description=transaction.description,
                created_at=str(transaction.date_posted),
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
            
            # Validate user owns the account
            db_connection = get_db_connection()
            account = AccountModel.find_by_id(db_connection, account_id)
            
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
            
            # Process withdrawal
            success, message, transaction = process_withdrawal(
                db_connection, user_id, account_id, amount, description
            )
            
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(message)
                return transaction_service_pb2.TransactionResponse(
                    success=False,
                    message=message
                )
            
            # Prepare transaction response
            transaction_proto = transaction_service_pb2.Transaction(
                transaction_id=str(transaction.transaction_id),
                account_id=str(transaction.account_id),
                user_id=transaction.user_id,
                transaction_type=transaction_service_pb2.TransactionType.WITHDRAWAL,
                amount=float(transaction.amount),
                balance_after=float(account.balance),
                description=transaction.description,
                created_at=str(transaction.date_posted),
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
            
            # Validate user owns the source account
            db_connection = get_db_connection()
            from_account = AccountModel.find_by_id(db_connection, from_account_id)
            
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
            
            # Validate destination account exists
            to_account = AccountModel.find_by_id(db_connection, to_account_id)
            if not to_account:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Destination account not found")
                return transaction_service_pb2.TransferResponse(
                    success=False,
                    message="Destination account not found"
                )
            
            # Process transfer
            success, message, source_tx, destination_tx = process_transfer(
                db_connection, user_id, from_account_id, to_account_id, amount, description
            )
            
            if not success:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(message)
                return transaction_service_pb2.TransferResponse(
                    success=False,
                    message=message
                )
            
            # Prepare transaction responses
            source_tx_proto = transaction_service_pb2.Transaction(
                transaction_id=str(source_tx.transaction_id),
                account_id=str(source_tx.account_id),
                user_id=source_tx.user_id,
                transaction_type=transaction_service_pb2.TransactionType.TRANSFER_OUT,
                amount=float(source_tx.amount),
                balance_after=float(from_account.balance),
                description=source_tx.description,
                created_at=str(source_tx.date_posted),
                status=transaction_service_pb2.TransactionStatus.COMPLETED,
                reference_id=str(destination_tx.transaction_id)
            )
            
            destination_tx_proto = transaction_service_pb2.Transaction(
                transaction_id=str(destination_tx.transaction_id),
                account_id=str(destination_tx.account_id),
                user_id=destination_tx.user_id,
                transaction_type=transaction_service_pb2.TransactionType.TRANSFER_IN,
                amount=float(destination_tx.amount),
                balance_after=float(to_account.balance),
                description=destination_tx.description,
                created_at=str(destination_tx.date_posted),
                status=transaction_service_pb2.TransactionStatus.COMPLETED,
                reference_id=str(source_tx.transaction_id)
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
            
            # Validate user owns the account
            db_connection = get_db_connection()
            account = AccountModel.find_by_id(db_connection, account_id)
            
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
            
            # Get transaction history
            transactions, total_count = get_transaction_history(
                db_connection, account_id, start_date, end_date, 
                transaction_type_filter=transaction_type, limit=limit, offset=offset
            )
            
            # Map transaction types to proto enum
            tx_type_map = {
                'deposit': transaction_service_pb2.TransactionType.DEPOSIT,
                'withdrawal': transaction_service_pb2.TransactionType.WITHDRAWAL,
                'transfer_out': transaction_service_pb2.TransactionType.TRANSFER_OUT,
                'transfer_in': transaction_service_pb2.TransactionType.TRANSFER_IN,
                'payment': transaction_service_pb2.TransactionType.PAYMENT,
                'fee': transaction_service_pb2.TransactionType.FEE,
                'interest': transaction_service_pb2.TransactionType.INTEREST
            }
            
            # Prepare transaction responses
            transaction_protos = []
            for tx in transactions:
                tx_proto = transaction_service_pb2.Transaction(
                    transaction_id=str(tx.transaction_id),
                    account_id=str(tx.account_id),
                    user_id=tx.user_id,
                    transaction_type=tx_type_map.get(
                        tx.transaction_type, 
                        transaction_service_pb2.TransactionType.OTHER
                    ),
                    amount=float(tx.amount),
                    description=tx.description,
                    created_at=str(tx.date_posted),
                    status=transaction_service_pb2.TransactionStatus.COMPLETED,
                    reference_id=str(tx.reference_id) if tx.reference_id else ""
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