from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from DatabaseHandling.connection import connect_db, get_db_cursor

transaction_routes = Blueprint('transaction_routes', __name__)

@transaction_routes.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        try:
            deposit_amount = request.form.get('amount', type=float)
            account_id = session.get('selected_account_id')
            
            conn, cursor = get_db_cursor()
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (deposit_amount, account_id))
            cursor.execute("""
                INSERT INTO transactions (from_account_id, amount, transaction_type, description) 
                VALUES (%s, %s, 'deposit', 'Deposit into account')
                """, (account_id, deposit_amount))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Deposit successful!', 'success')
        except Exception as e:
            flash(f"An error occurred during deposit: {e}", "error")

        return redirect(url_for('account_routes.dashboard'))

    return render_template('deposit.html')

@transaction_routes.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        try:
            withdrawal_amount = request.form.get('amount', type=float)
            account_id = session.get('selected_account_id')

            conn, cursor = get_db_cursor()
            # Ensure the account has sufficient balance
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
            balance = cursor.fetchone()[0]
            if balance >= withdrawal_amount:
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (withdrawal_amount, account_id))
                cursor.execute("""
                    INSERT INTO transactions (from_account_id, amount, transaction_type, description) 
                    VALUES (%s, %s, 'withdrawal', 'Withdrawal from account')
                    """, (account_id, withdrawal_amount))
                conn.commit()
            else:
                flash('Insufficient balance!', 'error')
            cursor.close()
            conn.close()

            flash('Withdrawal successful!', 'success')
        except Exception as e:
            flash(f"An error occurred during withdrawal: {e}", "error")

        return redirect(url_for('account_routes.dashboard'))

    return render_template('withdraw.html')

@transaction_routes.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        try:
            transfer_amount = request.form.get('amount', type=float)
            from_account_id = session.get('selected_account_id')
            to_account_id = request.form.get('recipient_account_id', type=int)  # Assuming recipient account ID is provided

            conn, cursor = get_db_cursor()
            # Check balance of sender's account
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (from_account_id,))
            balance = cursor.fetchone()[0]
            if balance >= transfer_amount:
                # Update balances of both accounts
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (transfer_amount, from_account_id))
                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (transfer_amount, to_account_id))
                # Record transactions
                cursor.execute("""
                    INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description) 
                    VALUES (%s, %s, %s, 'transfer', 'Transfer to another account')
                    """, (from_account_id, to_account_id, transfer_amount))
                conn.commit()
            else:
                flash('Insufficient balance for transfer!', 'error')
            cursor.close()
            conn.close()

            flash('Transfer successful!', 'success')
            return redirect(url_for('account_routes.dashboard'))  # Add a return statement here
        except Exception as e:
            flash(f"An error occurred during transfer: {e}", "error")

    return render_template('transfer.html')



@transaction_routes.route('/transaction_history', methods=['GET'])
def transaction_history():
    # Logic to show transaction history
    return render_template('transaction_history.html')

def configure_transaction_routes(app):
    app.register_blueprint(transaction_routes)
