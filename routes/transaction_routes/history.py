from flask import render_template
from flask_login import current_user
from . import transaction_routes
from DatabaseHandling.connection import get_db_cursor
import logging

@transaction_routes.route("/transaction_history", methods=["GET"], endpoint="transaction_history")
def transaction_history():
    conn, cursor = get_db_cursor()
    query = """
    SELECT t.*, 'Sent' as transaction_direction 
    FROM transactions t
    JOIN accounts a ON t.from_account_id = a.account_id
    WHERE a.user_id = %s
    UNION ALL
    SELECT t.*, 'Received' as transaction_direction 
    FROM transactions t
    JOIN accounts a ON t.to_account_id = a.account_id
    WHERE a.user_id = %s
    """
    user_id = current_user.get_id()  # Get user_id from current_user
    params = (user_id, user_id)
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    logging.debug("SQL query: %s", query)
    logging.debug("Query result: %s", transactions)
    cursor.close()
    conn.close()

    return transactions  # Return transactions instead of rendering a template