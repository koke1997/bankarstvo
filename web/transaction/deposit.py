from flask import request, redirect, url_for, flash, session, render_template
from utils.extensions import db
from core.models import Account, Transaction
from . import transaction_routes
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

            # Use db.session.query instead of Account.query
            account = db.session.query(Account).filter_by(account_id=account_id).first()
            
            if not account:
                flash("Account not found!", "error")
                return redirect(url_for("account_routes.dashboard"))
            
            # Update account balance with proper null handling
            current_balance = float(account.balance or 0)
            account.balance = current_balance + deposit_amount
            
            # Create transaction record with proper field initialization
            new_transaction = Transaction(
                account_id=account_id, 
                amount=deposit_amount, 
                type='deposit', 
                description='Deposit into account'
            )
            
            # Save changes to database
            db.session.add(new_transaction)
            db.session.commit()
            
            logging.info(f"Deposit successful! Amount: {deposit_amount}, Account ID: {account_id}")
            flash("Deposit successful!", "success")
        except Exception as e:
            db.session.rollback()
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
