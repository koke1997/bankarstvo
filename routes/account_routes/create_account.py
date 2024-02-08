from flask import request, flash, redirect, url_for, current_app, session
from . import account_routes
from DatabaseHandling.connection import get_db_cursor
from pymysql import IntegrityError

@account_routes.route("/create-account", methods=["GET", "POST"], endpoint="create_account")
def create_account():
    if request.method == "POST":
        try:
            account_name = request.form["account_name"]
            user_id = session.get("user_id")
            account_type = request.form.get("account_type", "checking")
            currency_code = request.form.get("currency_code", "USD")

            current_app.logger.info(f"Creating account for user ID: {user_id}")

            conn, cursor = get_db_cursor()
            cursor.execute(
                "INSERT INTO accounts (user_id, balance, account_type, account_status, currency_code, account_name) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, 0.00, account_type, "Active", currency_code, account_name),
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash("Account created successfully!", "success")
        except IntegrityError as e:
            current_app.logger.error(f"IntegrityError: {e}")
            flash("An error occurred while creating the account. Duplicate entry or integrity constraint violation.", "error")
        except Exception as e:
            current_app.logger.error(f"An unexpected error occurred while creating the account: {e}")
            flash(f"An unexpected error occurred while creating the account: {e}", "error")

        return redirect(url_for("account_routes.dashboard"))

    # If it's a GET request, you might want to render a form or redirect somewhere else.
    current_app.logger.error("Unexpected request to create-account endpoint with GET method.")
    return redirect(url_for("account_routes.dashboard"))  # Adjust this based on your requirements
