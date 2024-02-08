# routes/account_routes/search.py
# search.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from routes.account_routes import account_routes  # Updated import
from DatabaseHandling.connection import get_db_cursor
import logging


search_routes = Blueprint("search_routes", __name__)

def search_accounts_by_username(username):
    try:
        current_app.logger.debug("Before calling search_accounts in search.py")

        conn, cursor = get_db_cursor()
        sql_query = """
            SELECT account_id, account_name
            FROM accounts
            WHERE user_id IN (SELECT user_id FROM user WHERE username = %s)
        """
        cursor.execute(sql_query, (username,))
        accounts = cursor.fetchall()
        print(accounts)

        # Log the executed SQL query
        current_app.logger.debug("Executed SQL query: %s" % cursor.statement)

        cursor.close()
        conn.close()

        current_app.logger.debug(f"Search results for {username}: {accounts}")

        # Convert each account dictionary to a new dictionary
        accounts_list = [{'account_id': account['account_id'], 'account_name': account['account_name']} for account in accounts]

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