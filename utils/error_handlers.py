# utils/error_handlers.py
from flask import render_template, request


def register_error_handlers(app):
    """Register custom error handlers."""
    
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 Not Found: {request.url}")
        return render_template(
            "error.html",
            error_title="Page Not Found",
            error_code=404,
            error_message="The requested URL was not found on the server. If you entered the URL manually, please check your spelling and try again."
        ), 404

    @app.errorhandler(401)
    def unauthorized_error(e):
        app.logger.warning(f"Unauthorized access attempt: {request.url}")
        return render_template(
            "error.html", 
            error_title="Unauthorized",
            error_code=401,
            error_message="You need to log in to access this resource."
        ), 401

    @app.errorhandler(403)
    def forbidden_error(e):
        app.logger.warning(f"Forbidden access attempt: {request.url}")
        return render_template(
            "error.html", 
            error_title="Forbidden",
            error_code=403,
            error_message="You do not have permission to access this resource."
        ), 403

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {str(e)}")
        return render_template(
            "error.html",
            error_title="Server Error",
            error_code=500,
            error_message="An internal server error occurred. Please try again later."
        ), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception
        app.logger.exception("Unhandled exception: %s", str(e))
        
        # In development, show more details
        if app.debug:
            error_details = str(e)
        else:
            error_details = "An unexpected error occurred. Our team has been notified."
            
        return render_template(
            "error.html",
            error_title="Application Error",
            error_code=500,
            error_message=error_details
        ), 500