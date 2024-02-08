from flask import render_template, session
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
    params = (session.get("user_id"), session.get("user_id"))
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    logging.debug("SQL query: %s", query)
    logging.debug("Query result: %s", transactions)
    cursor.close()
    conn.close()

    return transactions  # Return transactions instead of rendering a template
