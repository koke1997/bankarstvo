from flask import request, redirect, url_for, flash, session
from DatabaseHandling.connection import get_db_cursor
from . import transaction_routes
from MediaHandling.pdf_handling import generate_pdf, save_document_to_db
import logging
import io
import base64
import os
from datetime import datetime

@transaction_routes.route("/deposit", methods=["GET", "POST"], endpoint="deposit")
def deposit():
    if request.method == "POST":
        try:
            deposit_amount = request.form.get("amount", type=float)
            account_id = session.get("selected_account_id")

            conn, cursor = get_db_cursor()

            update_query = "UPDATE accounts SET balance = balance + %s WHERE account_id = %s"
            cursor.execute(update_query, (deposit_amount, account_id))
            logging.info(f"Executed SQL query: {update_query} with parameters: ({deposit_amount}, {account_id})")

            insert_query = """
                INSERT INTO transactions (from_account_id, amount, transaction_type, description) 
                VALUES (%s, %s, 'deposit', 'Deposit into account')
                """
            cursor.execute(insert_query, (account_id, deposit_amount))
            logging.info(f"Executed SQL query: {insert_query} with parameters: ({account_id}, {deposit_amount})")

            conn.commit()
            cursor.close()
            conn.close()

            logging.info(f"Deposit successful! Amount: {deposit_amount}, Account ID: {account_id}")
            flash("Deposit successful!", "success")
        except Exception as e:
            logging.error(f"An error occurred during deposit: {e}")
            flash(f"An error occurred during deposit: {e}", "error")
            collect_failed_automation_results(e)

        return redirect(url_for("account_routes.dashboard"))

    return render_template("dashboard.html")

def collect_failed_automation_results(error):
    folder_name = "failed_automations"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    unique_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    file_name = f"{folder_name}/failed_automation_{unique_id}.log"
    
    with open(file_name, "w") as file:
        file.write(str(error))
