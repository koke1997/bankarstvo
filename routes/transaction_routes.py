from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session
from DatabaseHandling.connection import connect_db, get_db_cursor
import logging
import psycopg2.errors
import traceback  # Import the traceback module

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Initialize logging with a custom log format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define a Blueprint for transaction routes
transaction_routes = Blueprint('transaction_routes', __name__)

# Define your other routes and configurations here (snippets you have)

# ...

# Define the deposit route
@transaction_routes.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        try:
            deposit_amount = request.form.get('amount', type=float)
            account_id = session.get('selected_account_id')
            
            conn, cursor = get_db_cursor()
            
            # Log the SQL query
            update_query = "UPDATE accounts SET balance = balance + %s WHERE account_id = %s"
            cursor.execute(update_query, (deposit_amount, account_id))
            logger.info(f'Executed SQL query: {update_query} with parameters: ({deposit_amount}, {account_id})')
            
            # Log the SQL query
            insert_query = """
                INSERT INTO transactions (from_account_id, amount, transaction_type, description) 
                VALUES (%s, %s, 'deposit', 'Deposit into account')
                """
            cursor.execute(insert_query, (account_id, deposit_amount))
            logger.info(f'Executed SQL query: {insert_query} with parameters: ({account_id}, {deposit_amount})')
            
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f'Deposit successful! Amount: {deposit_amount}, Account ID: {account_id}')
            flash('Deposit successful!', 'success')
        except Exception as e:
            logger.error(f"An error occurred during deposit: {e}")
            flash(f"An error occurred during deposit: {e}", "error")

        return redirect(url_for('account_routes.dashboard'))

    return render_template('deposit.html')

# Define the withdraw route
@transaction_routes.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        try:
            withdrawal_amount = request.form.get('amount', type=float)
            account_id = session.get('selected_account_id')

            conn, cursor = get_db_cursor()

            # Ensure the account has sufficient balance
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
            result = cursor.fetchone()  # Get the result

            logger.info(f"Result of query: {result}")  # Add this line for debugging

            if result is not None and 'balance' in result:  # Check if 'balance' key is in the result
                balance = result['balance']  # Access the balance from the result dictionary
                if balance >= withdrawal_amount:
                    # Log the SQL query for updating balance
                    update_query = "UPDATE accounts SET balance = balance - %s WHERE account_id = %s"
                    cursor.execute(update_query, (withdrawal_amount, account_id))
                    logger.info(f'Executed SQL query: {update_query} with parameters: ({withdrawal_amount}, {account_id})')

                    # Log the SQL query for inserting transaction
                    insert_query = """
                        INSERT INTO transactions (from_account_id, amount, transaction_type, description) 
                        VALUES (%s, %s, 'withdrawal', 'Withdrawal from account')
                        """
                    cursor.execute(insert_query, (account_id, withdrawal_amount))
                    logger.info(f'Executed SQL query: {insert_query} with parameters: ({account_id}, {withdrawal_amount})')

                    conn.commit()
                    cursor.close()
                    conn.close()

                    logger.info(f'Withdrawal successful! Amount: {withdrawal_amount}, Account ID: {account_id}')
                    flash('Withdrawal successful!', 'success')
                else:
                    logger.warning(f'Insufficient balance for withdrawal! Amount: {withdrawal_amount}, Account ID: {account_id}')
                    flash('Insufficient balance for withdrawal!', 'error')
            else:
                logger.warning(f'Account not found or balance key missing! Account ID: {account_id}')
                flash('Account not found or balance key missing!', 'error')
        except psycopg2.errors.DatabaseError as db_error:
            # Log the specific database error
            logger.error(f"Database error during withdrawal: {db_error}")
            flash(f"Database error during withdrawal: {db_error}", "error")
        except Exception as e:
            # Log any other exceptions
            logger.error(f"An error occurred during withdrawal: {str(e)}")
            flash(f"An error occurred during withdrawal: {str(e)}", "error")
            print(f"Error details: {e}")  # Add this line for debugging
            traceback.print_exc()  # Print the full traceback

        return redirect(url_for('account_routes.dashboard'))

    return render_template('withdraw.html')






# Define the transfer route
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
                logger.warning(f'Insufficient balance for transfer! Amount: {transfer_amount}, Account ID: {from_account_id}')
                flash('Insufficient balance for transfer!', 'error')
            cursor.close()
            conn.close()

            logger.info(f'Transfer successful! Amount: {transfer_amount}, From Account ID: {from_account_id}, To Account ID: {to_account_id}')
            flash('Transfer successful!', 'success')
            return redirect(url_for('account_routes.dashboard'))  # Add a return statement here
        except Exception as e:
            logger.error(f"An error occurred during transfer: {e}")
            flash(f"An error occurred during transfer: {e}", "error")

    return render_template('transfer.html')

# Define the transaction history route
@transaction_routes.route('/transaction_history', methods=['GET'])
def transaction_history():
    # Logic to show transaction history
    return render_template('transaction_history.html')

# Add other routes and configurations here (snippets you have)

# ...

# Configure the transaction routes in your app
def configure_transaction_routes(app):
    app.register_blueprint(transaction_routes)

if __name__ == '__main__':
    configure_transaction_routes(app)
    app.run(debug=True)
