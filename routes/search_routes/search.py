# routes/account_routes/search.py
# search.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from routes.account_routes import account_routes  # Updated import
from DatabaseHandling.connection import get_db_cursor
from utils.extensions import db
from core.models import Account, User
import logging
import traceback

logger = logging.getLogger(__name__)

search_routes = Blueprint("search_routes", __name__)

def search_accounts_by_username(username):
    try:
        current_app.logger.debug("Before calling search_accounts in search.py")

        # Check if we're in test mode
        if current_app.config.get('TESTING', False):
            # Use SQLAlchemy for tests
            user = User.query.filter_by(username=username).first()
            if not user:
                return []
                
            accounts_query = Account.query.filter_by(user_id=user.user_id).all()
            accounts_list = []
            for account in accounts_query:
                accounts_list.append({
                    'account_id': account.account_id, 
                    'account_name': f"{account.account_type} - {account.currency_code}"
                })
            return accounts_list
        
        # Use raw database connection for production
        conn, cursor = get_db_cursor()
        sql_query = """
            SELECT a.account_id, a.account_type, a.currency_code
            FROM accounts a
            JOIN user u ON a.user_id = u.user_id
            WHERE u.username = %s
        """
        cursor.execute(sql_query, (username,))
        accounts = cursor.fetchall()
        logger.info(accounts)

        # Log the executed SQL query
        current_app.logger.debug("Executed SQL query: %s" % cursor.statement)

        cursor.close()
        conn.close()

        current_app.logger.debug(f"Search results for {username}: {accounts}")

        # Convert each account dictionary to a new dictionary
        accounts_list = [{
            'account_id': account['account_id'], 
            'account_name': f"{account['account_type']} - {account['currency_code']}"
        } for account in accounts]

        # Return the accounts
        return accounts_list

    except Exception as e:
        error_message = f"An error occurred while searching accounts: {e}"
        current_app.logger.error(error_message)
        current_app.logger.error(traceback.format_exc())  # Print the traceback
        return []

@search_routes.route('/search_accounts', methods=['POST'])
def search_accounts():
    recipient_username = request.form.get('recipient')
    if recipient_username is None:
        return jsonify(error="Recipient username not provided in the request."), 400

    accounts = search_accounts_by_username(recipient_username)
    return jsonify(accounts=accounts)