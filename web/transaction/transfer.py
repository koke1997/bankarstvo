# transfer.py

from flask import request, redirect, url_for, flash, session, render_template
from utils.extensions import db
from core.models import Account, Transaction
from . import transaction_routes
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
            logging.info(f"Fetching account details for Account ID: {from_account_id}")

            # Use SQLAlchemy ORM instead of direct database connections
            from_account = Account.query.filter_by(account_id=from_account_id).first()
            to_account = Account.query.filter_by(account_id=to_account_id).first()
            
            if not from_account:
                logging.error(f"No account found with ID: {from_account_id}")
                flash(f"No account found with ID: {from_account_id}", "error")
                return redirect(url_for("account_routes.dashboard"))
                
            if not to_account:
                logging.error(f"No recipient account found with ID: {to_account_id}")
                flash(f"No recipient account found with ID: {to_account_id}", "error")
                return redirect(url_for("account_routes.dashboard"))

            balance = float(from_account.balance)
            logging.info(f"Account ID: {from_account_id}, Balance: {balance}")

            if balance >= transfer_amount:
                # Update balance for the source account
                from_account.balance = balance - transfer_amount

                # Update balance for the destination account
                to_account.balance = float(to_account.balance) + transfer_amount

                # Create transaction records
                from_transaction = Transaction(
                    account_id=from_account_id,
                    amount=transfer_amount,
                    type='transfer',
                    description=f'Transfer from account {from_account_id} to account {to_account_id}',
                    recipient_account_id=to_account_id
                )
                
                to_transaction = Transaction(
                    account_id=to_account_id,
                    amount=transfer_amount,
                    type='transfer_received',
                    description=f'Transfer received from account {from_account_id}',
                    recipient_account_id=from_account_id
                )

                # Save changes to database
                db.session.add(from_transaction)
                db.session.add(to_transaction)
                db.session.commit()

                # Update the balance in the session
                session["balance"] = from_account.balance

                logging.info(f"Transfer successful! Amount: {transfer_amount}, From Account ID: {from_account_id}, To Account ID: {to_account_id}")
                flash("Transfer successful!", "success")

                # Note: Real-time notification removed as socketio is not available
                # This can be implemented later once you set up Socket.IO in your new architecture
            else:
                logging.warning(f"Insufficient balance for transfer! Amount: {transfer_amount}, Account ID: {from_account_id}")
                flash("Insufficient balance for transfer!", "error")
        except Exception as e:
            db.session.rollback()
            logging.error(f"An error occurred during transfer: {str(e)}")
            logging.error(traceback.format_exc())
            flash(f"An error occurred during transfer: {str(e)}", "error")

        return redirect(url_for("account_routes.dashboard"))

    return render_template("dashboard.html")
