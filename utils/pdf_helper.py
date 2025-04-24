import io
import base64
from reportlab.pdfgen import canvas
from core.models import SignedDocument
from utils.extensions import db
from flask_login import current_user  # Assuming you have Flask-Login for user management

def generate_pdf(document_content):
    """Generate a PDF and return it as a base64 string."""
    buffer = io.BytesIO()

    # Create a PDF object and add content
    p = canvas.Canvas(buffer)
    p.drawString(100, 100, document_content)  # Simple text content for demonstration
    p.showPage()
    p.save()

    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()

    return base64.b64encode(pdf).decode('utf-8')

def save_document_to_db(document_type, base64_data, additional_info=None, user_id=None):
    """Save the base64-encoded document to the database."""
    # Use the provided user_id or get from current_user if available
    if user_id is None and current_user and hasattr(current_user, 'user_id'):
        user_id = current_user.user_id
    elif user_id is None:
        # Default fallback if no user_id is provided and no current user exists
        user_id = 1
    
    # Set sender and receiver to dummy values if not provided
    # These are required fields in the SignedDocument model
    sender = "System"
    receiver = "User"

    # Create a new document with proper initialization
    new_document = SignedDocument(
        user_id=user_id,
        document_type=document_type,
        image_data=base64_data,
        additional_info=additional_info,
        sender=sender,
        receiver=receiver
    )

    db.session.add(new_document)
    db.session.commit()

    return new_document.document_id  # Use 'document_id' which is the attribute name defined in the model
