# select_account.py
from flask import session, request, redirect, url_for, flash
from flask_login import current_user
from . import account_routes
from DatabaseHandling.connection import get_db_cursor

@account_routes.route("/select_account", methods=["POST"])
def select_account():
    account_choice = request.form.get("account_choice")
    session["selected_account_id"] = account_choice
    selected_account_id = session.get("selected_account_id")

    if selected_account_id is not None:
        selected_account_id = int(selected_account_id)
        try:
            conn, cursor = get_db_cursor()
            cursor.execute("SELECT 1")  # Test the database connection
            cursor.fetchone()  # Fetch the result of the "SELECT 1" query
            cursor.execute(
                "SELECT a.*, u.username FROM accounts a JOIN user u ON a.user_id = u.user_id WHERE a.account_id = %s AND a.user_id = %s",
                (selected_account_id, current_user.get_id()),  # Get user_id from current_user
            )
            selected_account = cursor.fetchone()
            print(selected_account) # Log the selected account
        except Exception as e:
            print(f"Database error: {e}")  # Log the exception
            flash("Failed to select account due to a database error", "error")
            return redirect(url_for("account_routes.dashboard"))
        finally:
            cursor.close()
            conn.close()

        if selected_account:
            flash("Account selected successfully", "success")
        else:
            flash("Failed to select account", "error")

    return redirect(url_for("account_routes.dashboard"))