# withdraw.py

from flask import request, redirect, url_for, flash, session, render_template
from utils.extensions import db
from core.models import Account, Transaction
from . import transaction_routes
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

            # Use db.session.query instead of Account.query
            account = db.session.query(Account).filter_by(account_id=account_id).first()
            
            if account:
                # Add proper null handling for account.balance
                current_balance = float(account.balance or 0)
                if current_balance >= withdrawal_amount:
                    # Update account balance
                    account.balance = current_balance - withdrawal_amount
                    
                    # Create transaction record with proper initialization
                    new_transaction = Transaction(
                        account_id=account_id, 
                        amount=-withdrawal_amount,  # Use negative for withdrawals 
                        type='withdraw',  # Use 'withdraw' to match model expectations
                        description='Withdrawal from account'
                    )
                    
                    # Save changes to database
                    db.session.add(new_transaction)
                    db.session.commit()
                    
                    logging.info(f"Withdrawal successful! Amount: {withdrawal_amount}, Account ID: {account_id}")
                    flash("Withdrawal successful!", "success")
                else:
                    logging.warning(f"Insufficient balance for withdrawal! Amount: {withdrawal_amount}, Account ID: {account_id}")
                    flash("Insufficient balance for withdrawal!", "error")
            else:
                logging.warning(f"Account not found! Account ID: {account_id}")
                flash("Account not found!", "error")
        except Exception as e:
            db.session.rollback()
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
