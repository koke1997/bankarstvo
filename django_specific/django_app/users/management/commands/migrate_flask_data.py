import os
import sys
import logging
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.conf import settings
from users.models import User
from accounts.models import Account, Loan, Payment
from transactions.models import Transaction, SignedDocument, CryptoAsset, StockAsset
from marketplace.models import MarketplaceItem, MarketplaceTransaction
from django.contrib.auth.hashers import make_password

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class Command(BaseCommand):
    help = 'Migrates data from Flask SQLAlchemy database to Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flask-db-uri',
            type=str,
            help='URI of the Flask database to migrate from. If not provided, will use the DATABASE_URI env variable.',
        )

    def handle(self, *args, **options):
        try:
            flask_db_uri = options['flask_db_uri'] or os.environ.get('SQLALCHEMY_DATABASE_URI')
            
            if not flask_db_uri:
                self.stderr.write(self.style.ERROR('No Flask database URI provided. Set --flask-db-uri or DATABASE_URI env variable.'))
                return
                
            self.stdout.write(self.style.SUCCESS(f'Starting migration from {flask_db_uri}'))
            
            # Import SQLAlchemy and setup Flask database connection
            try:
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                
                engine = create_engine(flask_db_uri)
                Session = sessionmaker(bind=engine)
                flask_session = Session()
                
                self.stdout.write(self.style.SUCCESS('Successfully connected to Flask database'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to connect to Flask database: {e}'))
                return
            
            # Start a transaction for all Django operations
            with transaction.atomic():
                # 1. Migrate users
                self.migrate_users(flask_session)
                
                # 2. Migrate accounts
                self.migrate_accounts(flask_session)
                
                # 3. Migrate transactions
                self.migrate_transactions(flask_session)
                
                # 4. Migrate crypto and stock assets
                self.migrate_assets(flask_session)
                
                # 5. Migrate marketplace items and transactions
                self.migrate_marketplace(flask_session)
                
                # 6. Migrate loans and payments
                self.migrate_loans(flask_session)
            
            self.stdout.write(self.style.SUCCESS('Data migration completed successfully'))
            
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            self.stderr.write(self.style.ERROR(f'Migration failed: {e}'))
    
    def migrate_users(self, flask_session):
        """Migrate users from Flask to Django"""
        from sqlalchemy import text
        
        self.stdout.write('Migrating users...')
        # Get all users from Flask database
        flask_users = flask_session.execute(text('SELECT * FROM user')).fetchall()
        
        count = 0
        for flask_user in flask_users:
            # Check if user already exists
            if not User.objects.filter(username=flask_user.username).exists():
                # Create new Django user from Flask user
                user = User(
                    username=flask_user.username,
                    email=flask_user.email,
                    password=flask_user.password_hash,  # Django will expect a hashed password
                    two_factor_auth=flask_user.two_factor_auth if hasattr(flask_user, 'two_factor_auth') else False,
                    two_factor_auth_code=flask_user.two_factor_auth_code if hasattr(flask_user, 'two_factor_auth_code') else None,
                    two_factor_auth_expiry=flask_user.two_factor_auth_expiry if hasattr(flask_user, 'two_factor_auth_expiry') else None,
                    two_factor_auth_secret=flask_user.two_factor_auth_secret if hasattr(flask_user, 'two_factor_auth_secret') else None,
                    account_created=flask_user.account_created if hasattr(flask_user, 'account_created') else None,
                    last_login=flask_user.last_login if hasattr(flask_user, 'last_login') else None,
                )
                user.save()
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} users'))
    
    def migrate_accounts(self, flask_session):
        """Migrate accounts from Flask to Django"""
        from sqlalchemy import text
        
        self.stdout.write('Migrating accounts...')
        # Get all accounts from Flask database
        flask_accounts = flask_session.execute(text('SELECT * FROM accounts')).fetchall()
        
        count = 0
        for flask_account in flask_accounts:
            # Get the Django user for this account
            try:
                user = User.objects.get(id=flask_account.user_id)
                
                # Check if account already exists
                if not Account.objects.filter(account_id=flask_account.account_id).exists():
                    # Create new Django account from Flask account
                    account = Account(
                        account_id=flask_account.account_id,
                        account_type=flask_account.account_type,
                        balance=flask_account.balance,
                        currency_code=flask_account.currency_code,
                        user=user
                    )
                    account.save()
                    count += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {flask_account.user_id} not found, skipping account'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} accounts'))
    
    def migrate_transactions(self, flask_session):
        """Migrate transactions from Flask to Django"""
        from sqlalchemy import text
        
        self.stdout.write('Migrating transactions...')
        # Get all transactions from Flask database
        flask_transactions = flask_session.execute(text('SELECT * FROM transactions')).fetchall()
        
        count = 0
        for flask_tx in flask_transactions:
            # Get the Django user for this transaction
            try:
                user = User.objects.get(id=flask_tx.user_id)
                
                # Check if transaction already exists
                if not Transaction.objects.filter(transaction_id=flask_tx.transaction_id).exists():
                    # Create new Django transaction from Flask transaction
                    tx = Transaction(
                        transaction_id=flask_tx.transaction_id,
                        date_posted=flask_tx.date_posted,
                        user=user,
                        description=flask_tx.description,
                        amount=flask_tx.amount,
                        type=flask_tx.type
                    )
                    tx.save()
                    count += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {flask_tx.user_id} not found, skipping transaction'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} transactions'))
        
        # Migrate signed documents
        self.stdout.write('Migrating signed documents...')
        flask_documents = flask_session.execute(text('SELECT * FROM signed_documents')).fetchall()
        
        count = 0
        for flask_doc in flask_documents:
            try:
                user = User.objects.get(id=flask_doc.user_id)
                transaction = None
                
                if flask_doc.transaction_id:
                    try:
                        transaction = Transaction.objects.get(transaction_id=flask_doc.transaction_id)
                    except Transaction.DoesNotExist:
                        pass
                
                if not SignedDocument.objects.filter(document_id=flask_doc.document_id).exists():
                    doc = SignedDocument(
                        document_id=flask_doc.document_id,
                        user=user,
                        transaction=transaction,
                        timestamp=flask_doc.timestamp,
                        document_type=flask_doc.document_type,
                        additional_info=flask_doc.additional_info,
                        sender=flask_doc.sender,
                        receiver=flask_doc.receiver,
                        image_data=flask_doc.image_data
                    )
                    doc.save()
                    count += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {flask_doc.user_id} not found, skipping document'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {count} signed documents'))
    
    def migrate_assets(self, flask_session):
        """Migrate crypto and stock assets from Flask to Django"""
        from sqlalchemy import text
        
        # Migrate crypto assets
        self.stdout.write('Migrating crypto assets...')
        flask_crypto = flask_session.execute(text('SELECT * FROM crypto_assets')).fetchall()
        
        crypto_count = 0
        for flask_asset in flask_crypto:
            try:
                user = User.objects.get(id=flask_asset.user_id)
                
                if not CryptoAsset.objects.filter(asset_id=flask_asset.asset_id).exists():
                    asset = CryptoAsset(
                        asset_id=flask_asset.asset_id,
                        name=flask_asset.name,
                        symbol=flask_asset.symbol,
                        user=user,
                        balance=flask_asset.balance
                    )
                    asset.save()
                    crypto_count += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {flask_asset.user_id} not found, skipping crypto asset'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {crypto_count} crypto assets'))
        
        # Migrate stock assets
        self.stdout.write('Migrating stock assets...')
        flask_stocks = flask_session.execute(text('SELECT * FROM stock_assets')).fetchall()
        
        stock_count = 0
        for flask_asset in flask_stocks:
            try:
                user = User.objects.get(id=flask_asset.user_id)
                
                if not StockAsset.objects.filter(asset_id=flask_asset.asset_id).exists():
                    asset = StockAsset(
                        asset_id=flask_asset.asset_id,
                        name=flask_asset.name,
                        symbol=flask_asset.symbol,
                        user=user,
                        shares=flask_asset.shares
                    )
                    asset.save()
                    stock_count += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {flask_asset.user_id} not found, skipping stock asset'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {stock_count} stock assets'))
    
    def migrate_marketplace(self, flask_session):
        """Migrate marketplace items and transactions from Flask to Django"""
        from sqlalchemy import text
        
        # Migrate marketplace items
        self.stdout.write('Migrating marketplace items...')
        flask_items = flask_session.execute(text('SELECT * FROM marketplace_items')).fetchall()
        
        item_count = 0
        for flask_item in flask_items:
            try:
                seller = User.objects.get(id=flask_item.seller_id)
                buyer = None
                
                if flask_item.buyer_id:
                    try:
                        buyer = User.objects.get(id=flask_item.buyer_id)
                    except User.DoesNotExist:
                        pass
                
                if not MarketplaceItem.objects.filter(item_id=flask_item.item_id).exists():
                    item = MarketplaceItem(
                        item_id=flask_item.item_id,
                        name=flask_item.name,
                        description=flask_item.description,
                        price=flask_item.price,
                        seller=seller,
                        buyer=buyer,
                        status=flask_item.status
                    )
                    item.save()
                    item_count += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {flask_item.seller_id} not found, skipping marketplace item'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {item_count} marketplace items'))
        
        # Migrate marketplace transactions
        self.stdout.write('Migrating marketplace transactions...')
        flask_transactions = flask_session.execute(text('SELECT * FROM marketplace_transactions')).fetchall()
        
        transaction_count = 0
        for flask_tx in flask_transactions:
            try:
                buyer = User.objects.get(id=flask_tx.buyer_id)
                seller = User.objects.get(id=flask_tx.seller_id)
                
                try:
                    item = MarketplaceItem.objects.get(item_id=flask_tx.item_id)
                    
                    if not MarketplaceTransaction.objects.filter(transaction_id=flask_tx.transaction_id).exists():
                        tx = MarketplaceTransaction(
                            transaction_id=flask_tx.transaction_id,
                            item=item,
                            buyer=buyer,
                            seller=seller,
                            timestamp=flask_tx.timestamp,
                            amount=flask_tx.amount
                        )
                        tx.save()
                        transaction_count += 1
                except MarketplaceItem.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Item with ID {flask_tx.item_id} not found, skipping marketplace transaction'))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User not found, skipping marketplace transaction'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {transaction_count} marketplace transactions'))
    
    def migrate_loans(self, flask_session):
        """Migrate loans and payments from Flask to Django"""
        from sqlalchemy import text
        
        # Migrate loans
        self.stdout.write('Migrating loans...')
        flask_loans = flask_session.execute(text('SELECT * FROM loans')).fetchall()
        
        loan_count = 0
        for flask_loan in flask_loans:
            try:
                user = User.objects.get(id=flask_loan.user_id)
                
                if not Loan.objects.filter(loan_id=flask_loan.loan_id).exists():
                    loan = Loan(
                        loan_id=flask_loan.loan_id,
                        user=user,
                        amount=flask_loan.amount,
                        interest_rate=flask_loan.interest_rate,
                        term=flask_loan.term,
                        start_date=flask_loan.start_date,
                        end_date=flask_loan.end_date,
                        status=flask_loan.status
                    )
                    loan.save()
                    loan_count += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User with ID {flask_loan.user_id} not found, skipping loan'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {loan_count} loans'))
        
        # Migrate payments
        self.stdout.write('Migrating payments...')
        flask_payments = flask_session.execute(text('SELECT * FROM payments')).fetchall()
        
        payment_count = 0
        for flask_payment in flask_payments:
            try:
                loan = Loan.objects.get(loan_id=flask_payment.loan_id)
                
                if not Payment.objects.filter(payment_id=flask_payment.payment_id).exists():
                    payment = Payment(
                        payment_id=flask_payment.payment_id,
                        loan=loan,
                        amount=flask_payment.amount,
                        payment_date=flask_payment.payment_date,
                        status=flask_payment.status
                    )
                    payment.save()
                    payment_count += 1
            except Loan.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Loan with ID {flask_payment.loan_id} not found, skipping payment'))
        
        self.stdout.write(self.style.SUCCESS(f'Migrated {payment_count} payments'))