import io
import base64
from reportlab.pdfgen import canvas
from models import SignedDocument
from extensions import db
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

def save_document_to_db(document_type, base64_data, additional_info):
    """Save the base64-encoded document to the database."""
    user_id = current_user.id  # Assuming you have a user session and using Flask-Login

    new_document = SignedDocument(
        user_id=user_id,
        document_type=document_type,
        image_data=base64_data,  # Assuming 'image_data' is the base64 column
        additional_info=additional_info
    )

    db.session.add(new_document)
    db.session.commit()

    return new_document.id  # Use 'id' instead of 'document_id'
