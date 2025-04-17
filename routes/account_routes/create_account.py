from flask import request, flash, redirect, url_for, current_app, session
from flask_login import current_user
from . import account_routes
from DatabaseHandling.connection import get_db_cursor
from pymysql import IntegrityError

@account_routes.route("/create_account", methods=["GET", "POST"], endpoint="create_account")
def create_account():
    if request.method == "POST":
        account_name = request.form.get("account_name", "").strip()
        account_type = request.form.get("account_type", "").strip()
        currency_code = request.form.get("currency_code", "").strip()
        user_id = current_user.get_id()
        # Validate required fields
        if not account_name or not account_type or not currency_code:
            return ("Missing required fields", 400)
        # Validate currency code (example: only allow USD, EUR, GBP)
        allowed_currencies = {"USD", "EUR", "GBP"}
        if currency_code not in allowed_currencies:
            return ("Invalid currency code", 400)
        try:
            conn, cursor = get_db_cursor()
            # Check for duplicate account (by user_id and account_type)
            cursor.execute(
                "SELECT COUNT(*) FROM accounts WHERE user_id = %s AND account_type = %s AND currency_code = %s",
                (user_id, account_type, currency_code),
            )
            if cursor.fetchone()[0] > 0:
                cursor.close()
                conn.close()
                return ("Account with this type and currency already exists", 400)
            cursor.execute(
                "INSERT INTO accounts (user_id, balance, account_type, currency_code) VALUES (%s, %s, %s, %s)",
                (user_id, 0.00, account_type, currency_code),
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Account created successfully!", "success")
            return redirect(url_for("account_routes.dashboard"))
        except IntegrityError as e:
            current_app.logger.error(f"IntegrityError: {e}")
            return ("Integrity error while creating the account.", 400)
        except Exception as e:
            current_app.logger.error(f"An unexpected error occurred while creating the account: {e}")
            return (f"An unexpected error occurred while creating the account: {e}", 400)
    return redirect(url_for("account_routes.dashboard"))
