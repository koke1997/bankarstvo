import logging
import os
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a global flag to track if database is available
db_available = True

# Default demo data for use when database is unavailable
DEMO_USERS = {
    1: {"user_id": 1, "username": "demo_user", "email": "demo@example.com", "password_hash": "demo_hash"},
    2: {"user_id": 2, "username": "admin", "email": "admin@example.com", "password_hash": "admin_hash"},
}

DEMO_ACCOUNTS = {
    1: {"account_id": 1, "user_id": 1, "account_type": "Checking", "balance": 1000.00, "currency_code": "USD"},
    2: {"account_id": 2, "user_id": 1, "account_type": "Savings", "balance": 5000.00, "currency_code": "EUR"},
}

DEMO_TRANSACTIONS = [
    {"transaction_id": 1, "user_id": 1, "from_account_id": 1, "amount": 100.00, "date_posted": "2025-04-21 12:00:00", "description": "Initial deposit", "type": "deposit"},
    {"transaction_id": 2, "user_id": 1, "from_account_id": 1, "amount": -50.00, "date_posted": "2025-04-21 13:00:00", "description": "ATM Withdrawal", "type": "withdraw"},
]

def get_connection_params():
    """Get database connection parameters from environment variables with defaults."""
    return {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', 3306)),
        'user': os.getenv('DATABASE_USER', 'root'),
        'password': os.getenv('DATABASE_PASSWORD', 'example'),
        'database': os.getenv('DATABASE_NAME', 'bankarstvo'),
        'charset': 'utf8mb4',
        'cursorclass': DictCursor
    }

def check_database_availability():
    """Check if database is available by attempting a connection."""
    global db_available
    
    try:
        conn = pymysql.connect(**get_connection_params())
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        if not db_available:
            logger.info("Database connection re-established")
        db_available = True
        return True
    except Exception as e:
        if db_available:
            logger.warning(f"Database unavailable: {e}. Will use demo data.")
        db_available = False
        return False

@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic reconnection attempts."""
    global db_available
    
    # Check if database is available or fall back to demo mode
    if not check_database_availability():
        logger.warning("Using demo mode (no database connection)")
        # Yield None to indicate no actual connection
        try:
            yield None
        finally:
            pass
        return
    
    # Try to establish a connection
    connection = None
    try:
        connection = pymysql.connect(**get_connection_params())
        yield connection
        connection.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        if connection:
            connection.rollback()
        db_available = False
        raise
    finally:
        if connection:
            connection.close()

def get_db_cursor():
    """Get database connection and cursor with retry logic."""
    global db_available
    
    # If database is known to be unavailable, return None for both
    if not db_available:
        logger.warning("Database unavailable, returning None for connection and cursor")
        return None, None
    
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = pymysql.connect(**get_connection_params())
            cursor = conn.cursor()
            return conn, cursor
        except pymysql.err.OperationalError as e:
            attempt += 1
            logger.warning(f"Connection attempt {attempt}/{max_attempts} failed: {e}")
            if attempt >= max_attempts:
                db_available = False
                logger.error(f"Failed to connect to database after {max_attempts} attempts")
                return None, None
            time.sleep(1)  # Wait before retrying
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            db_available = False
            return None, None

# Demo data access functions used when database is unavailable
def get_demo_user(username=None, user_id=None, email=None):
    """Get a user from demo data by username, id or email."""
    if username:
        for user in DEMO_USERS.values():
            if user['username'] == username:
                return user
    elif user_id:
        return DEMO_USERS.get(user_id)
    elif email:
        for user in DEMO_USERS.values():
            if user['email'] == email:
                return user
    return None

def get_demo_accounts(user_id):
    """Get accounts for a user from demo data."""
    return [account for account in DEMO_ACCOUNTS.values() if account['user_id'] == user_id]

def get_demo_transactions(user_id=None, account_id=None):
    """Get transactions from demo data, filtered by user or account."""
    if user_id:
        return [tx for tx in DEMO_TRANSACTIONS if tx['user_id'] == user_id]
    elif account_id:
        return [tx for tx in DEMO_TRANSACTIONS if tx.get('from_account_id') == account_id or tx.get('to_account_id') == account_id]
    return DEMO_TRANSACTIONS

def get_demo_account(account_id):
    """Get a specific account from demo data."""
    return DEMO_ACCOUNTS.get(account_id)
