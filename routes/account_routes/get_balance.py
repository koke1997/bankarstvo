from . import account_routes
from flask import jsonify
from DatabaseHandling.connection import get_db_cursor

@account_routes.route('/get_balance', methods=['GET'])
def get_balance():
    account_id = session.get("selected_account_id")
    if account_id is None:
        return jsonify({'error': 'No account selected'}), 400

    conn, cursor = get_db_cursor()
    cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
    balance = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({'balance': balance})