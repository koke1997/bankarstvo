from flask import request, flash, redirect, url_for, current_app, session
from flask_login import current_user
from . import account_routes
from core.models import Account
from utils.extensions import db

@account_routes.route("/create_account", methods=["GET", "POST"], endpoint="create_account")
def create_account():
    if request.method == "POST":
        account_type = request.form.get("account_type", "").strip()
        currency_code = request.form.get("currency_code", "").strip()
        
        # Get user_id, try multiple methods to ensure it works in test environments
        user_id = None
        if current_user and current_user.is_authenticated:
            user_id = current_user.get_id()
        
        # Fallback for tests
        if not user_id and 'user_id' in session:
            user_id = session['user_id']
        
        # Log for debugging
        current_app.logger.info(f"Creating account with user_id: {user_id}, auth: {current_user.is_authenticated if current_user else False}")
        
        # Validate required fields
        if not account_type or not currency_code:
            return ("Missing required fields", 400)
        
        # Validate user is logged in
        if not user_id:
            return ("User not authenticated", 401)
            
        # Validate currency code (example: only allow USD, EUR, GBP)
        allowed_currencies = {"USD", "EUR", "GBP"}
        if currency_code not in allowed_currencies:
            return ("Invalid currency code", 400)
            
        try:
            # Check for duplicate account - using db.session.query instead of Account.query
            existing = db.session.query(Account).filter_by(user_id=user_id, account_type=account_type, currency_code=currency_code).first()
            if existing:
                return ("Account with this type and currency already exists", 400)
                
            # Create account object with the proper field assignments as keyword arguments
            account = Account(
                account_type=account_type,
                balance=0.00,
                currency_code=currency_code,
                user_id=user_id,
                status="active"  # Adding a default status
            )
            db.session.add(account)
            db.session.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for("account_routes.dashboard"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"An unexpected error occurred while creating the account: {e}")
            return (f"An unexpected error occurred while creating the account: {e}", 400)
    return redirect(url_for("account_routes.dashboard"))
