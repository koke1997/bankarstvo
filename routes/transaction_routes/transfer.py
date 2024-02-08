# transfer.py

from flask import request, redirect, url_for, flash, session, render_template
from . import transaction_routes
from DatabaseHandling.connection import get_db_cursor
import logging
import traceback

@transaction_routes.route("/transfer", methods=["GET", "POST"], endpoint="transfer")
def transfer():
    if request.method == "POST":
        try:
            transfer_amount = request.form.get("amount")
            to_account_id = request.form.get("recipient_account_id")

            # Convert amount to a number
            try:
                transfer_amount = float(transfer_amount)
            except ValueError:
                flash("Invalid transfer amount", "error")
                return redirect(url_for("account_routes.dashboard"))

            # Convert recipient_account_id to an integer
            try:
                to_account_id = int(to_account_id)
            except ValueError:
                flash("Invalid recipient account ID", "error")
                return redirect(url_for("account_routes.dashboard"))

            from_account_id = session.get("selected_account_id")
            logging.info(f"Fetching account details for Account ID: {from_account_id}")  # Log the account id

            conn, cursor = get_db_cursor()

            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (from_account_id,))
            result = cursor.fetchone()
            if result is None:
                logging.error(f"No account found with ID: {from_account_id}")
                flash(f"No account found with ID: {from_account_id}", "error")
                return redirect(url_for("account_routes.dashboard"))

            balance = result['balance']  # Corrected line
            logging.info(f"Account ID: {from_account_id}, Balance: {balance}")  # Log the account id and balance

            if balance >= transfer_amount:
                # Update balance for the source account
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (transfer_amount, from_account_id))
                logging.info("Updated balance for the source account")

                # Update balance for the destination account
                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (transfer_amount, to_account_id))
                logging.info("Updated balance for the destination account")

                # Log the transfer transactions
                insert_query_from = """
                    INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description) 
                    VALUES (%s, %s, %s, 'transfer', CONCAT('Transfer from account ', %s, ' to account ', %s))
                """
                cursor.execute(insert_query_from, (from_account_id, to_account_id, transfer_amount, from_account_id, to_account_id))
                logging.info("Logged the transfer transaction for the source account")

                insert_query_to = """
                    INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, description) 
                    VALUES (%s, %s, %s, 'transfer', CONCAT('Transfer from account ', %s, ' to account ', %s))
                """
                cursor.execute(insert_query_to, (to_account_id, from_account_id, transfer_amount, to_account_id, from_account_id))
                logging.info("Logged the transfer transaction for the destination account")

                conn.commit()

                conn.close()

                logging.info(f"Transfer successful! Amount: {transfer_amount}, From Account ID: {from_account_id}, To Account ID: {to_account_id}")
                flash("Transfer successful!", "success")
            else:
                logging.warning(f"Insufficient balance for transfer! Amount: {transfer_amount}, Account ID: {from_account_id}")
                flash("Insufficient balance for transfer!", "error")
        except Exception as e:
            logging.error(f"An error occurred during transfer: {str(e)}")
            logging.error(traceback.format_exc())
            flash(f"An error occurred during transfer: {str(e)}", "error")

        return redirect(url_for("account_routes.dashboard"))

    return render_template("dashboard.html")