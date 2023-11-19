from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from DatabaseHandling.connection import connect_db, get_db_cursor
import json
import logging

# Blueprints
account_bp = Blueprint('account', __name__)
account_routes = Blueprint('account_routes', __name__)

# Create a logger for the current module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@account_bp.route('/create-account', methods=['POST'])
def create_account():
    try:
        account_name = request.form['account_name']
        user_id = session.get('user_id')  # Assuming the user's ID is stored in the session
        account_type = request.form.get('account_type', 'checking')
        currency_code = request.form.get('currency_code', 'USD')

        # Log the current user's ID
        logger.info(f"Creating account for user ID: {user_id}")

        conn, cursor = get_db_cursor()
        cursor.execute("""
            INSERT INTO accounts 
            (user_id, balance, account_type, account_status, currency_code, account_name) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """, 
            (user_id, 0.00, account_type, 'Active', currency_code, account_name))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Account created successfully!', 'success')
    except Exception as e:
        current_app.logger.error(f"An error occurred while creating the account: {e}")
        flash(f"An error occurred while creating the account: {e}", "error")
    return redirect(url_for('account_routes.dashboard'))




@account_routes.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_id = session.get('user_id')  # Moved this line to the top
    if not user_id:
        flash('User not logged in', 'error')
        return redirect(url_for('user_routes.login'))

    try:
        conn, cursor = get_db_cursor()
        cursor.execute("SELECT account_id, account_name FROM accounts WHERE user_id = %s", (user_id,))
        accounts = cursor.fetchall()  # Fetch all accounts associated with the user
        cursor.close()
        conn.close()
        
        logger.debug(f"User ID from session: {user_id}")
        logger.debug(f"Accounts for user ID {user_id}: {accounts}")

        with open('extresources/countrycodes.json') as f:
            country_data = json.load(f)

        country_options = [
            {
                'code': entry['ISO4217-currency_alphabetic_code'],
                'name': entry['CLDR display name']
            }
            for entry in country_data
            if 'ISO4217-currency_alphabetic_code' in entry and entry['ISO4217-currency_alphabetic_code']
        ]

    except Exception as e:
            current_app.logger.error(f"An error occurred: {e}")
            flash(f"An error occurred: {e}", "error")
            country_options = []
            accounts = []  # Reset accounts to an empty list in case of an exception

    selected_account = None
    transactions = []
    balance = 0.00

    if request.method == 'POST':
        account_choice = request.form.get('account_choice')
        session['selected_account_id'] = account_choice  # Store selected_account_id in the session

        try:
            selected_account_id = session.get('selected_account_id')
            conn, cursor = get_db_cursor()
            cursor.execute("SELECT * FROM accounts WHERE account_id = %s AND user_id = %s", (selected_account_id, user_id))
            selected_account = cursor.fetchone()

            if selected_account:
                balance = selected_account['balance']
                cursor.execute("SELECT * FROM transactions WHERE from_account_id = %s", (selected_account_id,))
                transactions = cursor.fetchall()

            cursor.close()
            conn.close()

        except Exception as e:
            current_app.logger.error(f"An error occurred while retrieving account details: {e}")
            flash(f"An error occurred while retrieving account details: {e}", "error")

    return render_template('dashboard.html', country_options=country_options, accounts=accounts, selected_account=selected_account, selected_account_id=session.get('selected_account_id'), balance=balance, transactions=transactions)

# Implement routes for Deposit Funds, Withdraw Funds, Fund Transfer, and Transaction History here

# Rest of your code
def configure_account_routes(app):
    app.register_blueprint(account_routes)
    app.register_blueprint(account_bp, url_prefix='/account')
