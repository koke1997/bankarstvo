# transaction blueprint routes definition
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

# Import services from core directory
from core.services.transaction_service import get_transaction_details, create_transaction, update_transaction

# Create blueprint with new naming convention
transaction_bp = Blueprint('transaction', __name__, template_folder='templates')

@transaction_bp.route('/')
@login_required
def index():
    """
    Transaction dashboard or listing page.
    """
    return render_template('transaction/index.html')

@transaction_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new transaction.
    """
    if request.method == 'POST':
        # Extract form data
        # TODO: Implement form data extraction
        
        # Call service layer to create transaction
        # TODO: Implement transaction creation
        
        flash('Transaction created successfully', 'success')
        return redirect(url_for('transaction.index'))
        
    return render_template('transaction/create.html')

@transaction_bp.route('/<int:id>')
@login_required
def details(id):
    """
    Get details of a specific transaction.
    """
    # Call service layer to get transaction details
    # TODO: Implement transaction details retrieval
    
    return render_template('transaction/details.html')

@transaction_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit a transaction.
    """
    # Get transaction details
    # TODO: Implement transaction retrieval
    
    if request.method == 'POST':
        # Extract form data
        # TODO: Implement form data extraction
        
        # Update transaction
        # TODO: Implement transaction update
        
        flash('Transaction updated successfully', 'success')
        return redirect(url_for('transaction.details', id=id))
        
    return render_template('transaction/edit.html')
