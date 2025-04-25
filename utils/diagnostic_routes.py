from flask import jsonify, render_template

def register_diagnostic_routes(app):
    """Register diagnostic API and HTML routes for testing purposes."""

    @app.route('/api/diagnostic', methods=['GET'])
    def diagnostic_api():
        """A simple diagnostic API endpoint."""
        return jsonify({"status": "ok", "message": "Diagnostic API is working!"})

    @app.route('/diagnostic', methods=['GET'])
    def diagnostic_html():
        """A simple diagnostic HTML page."""
        return render_template('diagnostic.html', message="Diagnostic HTML is working!")