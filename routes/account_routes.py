from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from DatabaseHandling.connection import connect_db, get_db_cursor
import json

# Blueprints
account_bp = Blueprint('account', __name__)
account_routes = Blueprint('account_routes', __name__)

@account_bp.route('/create-account', methods=['POST'])
def create_account():
    try:
        account_name = request.form['account_name']
        # Assuming the user's ID is stored in the session when they log in
        user_id = session.get('user_id')  # Replace with your session key if different
        account_type = request.form.get('account_type', 'checking')
        currency_code = request.form.get('currency_code', 'USD')

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
    try:
        conn, cursor = get_db_cursor()
        cursor.execute("SELECT account_id, account_name FROM accounts")
        accounts = cursor.fetchall()
        cursor.close()
        conn.close()

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
        accounts = []  # Reset accounts to an empty list in case of exception

    selected_account = None
    transactions = []
    balance = 0.00

    if request.method == 'POST':
        selected_account_id = request.form.get('account_choice')

        # Retrieve account details, balance, transactions, etc.
        try:
            conn, cursor = get_db_cursor()
            cursor.execute("SELECT * FROM accounts WHERE account_id = %s", (selected_account_id,))
            selected_account = cursor.fetchone()

            if selected_account:
                balance = selected_account['balance']
                # Retrieve transactions for the selected account
                cursor.execute("SELECT * FROM transactions WHERE account_id = %s", (selected_account_id,))
                transactions = cursor.fetchall()

            cursor.close()
            conn.close()

        except Exception as e:
            current_app.logger.error(f"An error occurred while retrieving account details: {e}")
            flash(f"An error occurred while retrieving account details: {e}", "error")

    return render_template('dashboard.html', country_options=country_options, accounts=accounts, selected_account=selected_account, balance=balance, transactions=transactions)


def configure_account_routes(app):
    app.register_blueprint(account_routes)
    app.register_blueprint(account_bp, url_prefix='/account')
