# withdraw.py

from flask import request, redirect, url_for, flash, session
from . import transaction_routes
from DatabaseHandling.connection import get_db_cursor
import logging
import traceback
import os
from datetime import datetime
logger = logging.getLogger(__name__)

@transaction_routes.route("/withdraw", methods=["GET", "POST"], endpoint="withdraw")
def withdraw():
    if request.method == "POST":
        try:
            withdrawal_amount = request.form.get("amount", type=float)
            account_id = session.get("selected_account_id")

            conn, cursor = get_db_cursor()

            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
            result = cursor.fetchone()

            logging.info(f"Result of query: {result}")

            if result is not None and "balance" in result:
                balance = result["balance"]
                if balance >= withdrawal_amount:
                    # Update account balance
                    update_query = "UPDATE accounts SET balance = balance - %s WHERE account_id = %s"
                    cursor.execute(update_query, (withdrawal_amount, account_id))
                    logging.info(f"Executed SQL query: {update_query} with parameters: ({withdrawal_amount}, {account_id})")

                    # Log the withdrawal transaction
                    insert_query = """
                        INSERT INTO transactions (from_account_id, amount, transaction_type, description) 
                        VALUES (%s, %s, 'withdrawal', 'Withdrawal from account')
                    """
                    cursor.execute(insert_query, (account_id, withdrawal_amount))
                    logging.info(f"Executed SQL query: {insert_query} with parameters: ({account_id}, {withdrawal_amount})")

                    conn.commit()
                    conn.close()

                    logging.info(f"Withdrawal successful! Amount: {withdrawal_amount}, Account ID: {account_id}")
                    flash("Withdrawal successful!", "success")
                else:
                    logging.warning(f"Insufficient balance for withdrawal! Amount: {withdrawal_amount}, Account ID: {account_id}")
                    flash("Insufficient balance for withdrawal!", "error")
            else:
                logging.warning(f"Account not found or balance key missing! Account ID: {account_id}")
                flash("Account not found or balance key missing!", "error")
        except Exception as e:
            logging.error(f"An error occurred during withdrawal: {str(e)}")
            flash(f"An error occurred during withdrawal: {str(e)}", "error")
            logger.info(f"Error details: {e}")
            traceback.print_exc()
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
