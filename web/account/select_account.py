# select_account.py
from flask import session, request, redirect, url_for, flash
from flask_login import current_user
from . import account_routes
from utils.extensions import db
from core.models import Account, User
import logging

logger = logging.getLogger(__name__)


@account_routes.route("/select_account", methods=["POST"])
def select_account():
    account_choice = request.form.get("account_choice")
    session["selected_account_id"] = account_choice
    selected_account_id = session.get("selected_account_id")

    if selected_account_id is not None:
        try:
            selected_account_id = int(selected_account_id)
            try:
                # Use SQLAlchemy to fetch the account information
                account = Account.query.filter_by(
                    account_id=selected_account_id, 
                    user_id=current_user.get_id()
                ).first()
                
                if account:
                    user = User.query.filter_by(user_id=account.user_id).first()
                    selected_account = {
                        'account_id': account.account_id,
                        'user_id': account.user_id,
                        'username': user.username if user else 'Unknown'
                    }
                    logger.info(selected_account)  # Log the selected account
                else:
                    selected_account = None
            except Exception as e:
                logger.error(f"Database error: {e}")  # Log the exception
                flash("Failed to select account due to a database error", "error")
                return redirect(url_for("account_routes.dashboard"))

            if selected_account:
                flash("Account selected successfully", "success")
            else:
                flash("Failed to select account", "error")
        except ValueError:
            flash("Invalid account ID", "error")

    return redirect(url_for("account_routes.dashboard"))
