# dashboard.py
from flask import render_template, session, request, flash, redirect, url_for, current_app
from . import account_routes
from DatabaseHandling.connection import get_db_cursor
from .forms import TransferForm
from routes.search_routes.search import search_accounts_by_username  # Updated import
from routes.transaction_routes.history import transaction_history
import requests
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@account_routes.route("/dashboard", methods=["GET", "POST"], endpoint="dashboard")
def dashboard():
    user_id = session.get("user_id")

    if not user_id:
        flash("User not logged in", "error")
        return redirect(url_for("user_routes.login"))

    country_options = []
    accounts = []
    selected_account = None
    transactions = []
    balance = 0.00
    transfer_form = TransferForm()
    search_results = []  # Initialize search results

    try:
        conn, cursor = get_db_cursor()
        cursor.execute(
            "SELECT account_id, account_name FROM accounts WHERE user_id = %s",
            (user_id,),
        )
        accounts = cursor.fetchall()
        cursor.close()
        conn.close()

        logger.debug(f"User ID from session: {user_id}")
        logger.debug(f"Accounts for user ID {user_id}: {accounts}")

        with open("extresources/countrycodes.json") as f:
            country_data = json.load(f)

        country_options = [
            {
                "code": entry["ISO4217-currency_alphabetic_code"],
                "name": entry["CLDR display name"],
            }
            for entry in country_data
            if "ISO4217-currency_alphabetic_code" in entry
            and entry["ISO4217-currency_alphabetic_code"]
        ]

    except Exception as e:
        current_app.logger.error(f"An error occurred: {e}")
        flash(f"An error occurred: {e}", "error")

    if request.method == "POST":
        account_choice = request.form.get("account_choice")
        session["selected_account_id"] = account_choice

    selected_account_id = session.get("selected_account_id")

    if selected_account_id is not None:
        selected_account_id = int(selected_account_id)
        conn, cursor = get_db_cursor()
        cursor.execute(
            "SELECT a.*, u.username FROM accounts a JOIN user u ON a.user_id = u.user_id WHERE a.account_id = %s AND a.user_id = %s",
            (selected_account_id, user_id),
        )
        selected_account = cursor.fetchone()

        if selected_account:
            balance = selected_account["balance"]
        cursor.close()
        conn.close()

    if request.method == "POST":
        if "search_button" in request.form:
            current_app.logger.debug("Before calling search_accounts in dashboard.py")
            search_username = transfer_form.recipient.data
            if search_username:
                try:
                    # Utilize search_accounts from search.py
                    search_results = search_accounts_by_username(search_username)

                    return render_template(
                        "dashboard.html",
                        country_options=country_options,
                        accounts=accounts,
                        selected_account=selected_account,
                        selected_account_id=session.get("selected_account_id"),
                        balance=balance,
                        transactions=transaction_history(),
                        transfer_form=transfer_form,
                        search_results=search_results,
                        recipient_username=transfer_form.recipient.data
                    )
                except Exception as e:
                    current_app.logger.error(
                        f"An error occurred while searching for accounts: {e}"
                    )
                    flash(f"An error occurred while searching for accounts: {e}", "error")

        elif "transfer_button" in request.form:
            transactions=transaction_history()

    # Search for accounts based on recipient username
    return render_template(
        "dashboard.html",
        country_options=country_options,
        accounts=accounts,
        selected_account=selected_account,
        selected_account_id=session.get("selected_account_id"),
        balance=balance,
        transactions=transaction_history(),
        transfer_form=transfer_form,
        search_results=search_results,
        recipient_username=transfer_form.recipient.data  # Add this line to pass the recipient username
    )