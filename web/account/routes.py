# account blueprint routes definition
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

# Import services from core directory
from core.services import get_account_details, create_account, update_account

# Create blueprint with new naming convention
account_bp = Blueprint('account', __name__, template_folder='templates')

@account_bp.route('/')
@login_required
def index():
    """
    Account dashboard or listing page.
    """
    return render_template('account/index.html')

@account_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new account.
    """
    if request.method == 'POST':
        # Extract form data
        # TODO: Implement form data extraction
        
        # Call service layer to create account
        # TODO: Implement account creation
        
        flash('Account created successfully', 'success')
        return redirect(url_for('account.index'))
        
    return render_template('account/create.html')

@account_bp.route('/<int:id>')
@login_required
def details(id):
    """
    Get details of a specific account.
    """
    # Call service layer to get account details
    # TODO: Implement account details retrieval
    
    return render_template('account/details.html')

@account_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a account.
    """
    # Get account details
    # TODO: Implement account retrieval
    
    if request.method == 'POST':
        # Extract form data
        # TODO: Implement form data extraction
        
        # Update account
        # TODO: Implement account update
        
        flash('Account updated successfully', 'success')
        return redirect(url_for('account.details', id=id))
        
    return render_template('account/edit.html')
