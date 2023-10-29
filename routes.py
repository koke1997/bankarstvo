from FiatHandling.deposit import deposit as deposit_func
from flask import render_template, request, redirect, url_for, flash, session
from models import User, db
from flask_bcrypt import Bcrypt
import os
from FiatHandling.transactionhistory import get_transaction_history
from FiatHandling.withdraw import withdraw as withdraw_func
from FiatHandling.fundtransfer import transfer_funds


bcrypt = Bcrypt()

def configure_routes(app):

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            # Generate a salt
            salt = os.urandom(16).hex()

            # Combine password and salt, then hash
            hashed_pw = bcrypt.generate_password_hash(password + salt).decode('utf-8')

            # Store the user in the database
            new_user = User(username=username, email=email, password_hash=hashed_pw, salt=salt)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please login.')
            return redirect(url_for('index'))

        return render_template('register.html')

    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password + user.salt):
            session['user_id'] = user.user_id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('index'))
        

    @app.route('/create_account', methods=['POST'])
    def create_account():
        user_id = session.get('user_id')
        currency_code = request.form.get('currency_code')

        # Validation
        if not validate_currency(currency_code):
            flash('Invalid currency code. Please choose a valid currency.')
            return redirect(url_for('dashboard'))

        # Create an account
        new_account = Account(user_id=user_id, currency_code=currency_code)
        db.session.add(new_account)
        db.session.commit()
        
        flash('Account created successfully!')
        return redirect(url_for('dashboard'))


    @app.route('/transaction_history')
    def transaction_history():
        # user_id = # TODO: Fetch current user's ID
        # For now, I'll fetch a dummy user ID
        user_id = session.get('user_id')
        transactions = get_transaction_history(user_id)
        return render_template('transaction_history.html', transactions=transactions)

    @app.route('/withdraw', methods=['POST'])
    def withdraw():
        # user_id = # TODO: Fetch current user's ID
        # For now, I'll fetch a dummy user ID
        user_id = session.get('user_id')
        amount = request.form.get('amount')
        message = withdraw_func(user_id, amount)
        flash(message)
        return redirect(url_for('dashboard'))

    @app.route('/deposit', methods=['POST'])
    def deposit():
        # user_id = # TODO: Fetch current user's ID
        # For now, I'll fetch a dummy user ID
        user_id = session.get('user_id')
        amount = request.form.get('amount')
        message = deposit_func(user_id, amount)
        flash(message)
        return redirect(url_for('dashboard'))

    @app.route('/transfer', methods=['POST'])
    def transfer():
        # user_id = # TODO: Fetch current user's ID
        # For now, I'll fetch a dummy user ID
        user_id = session.get('user_id')
        recipient_id = request.form.get('recipient')
        amount = request.form.get('amount')
        message = transfer_funds(user_id, recipient_id, amount)
        flash(message)
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
