import os
import subprocess
from app_factory import create_app, socketio
import argparse
from core.plot_diagram import plot_routes_diagram, extract_all_routes
from flask import render_template

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-diagram", action="store_true", help="Display routes diagram")
    args = parser.parse_args()

    if args.diagram:
        extracted_routes = extract_all_routes()
        plot_routes_diagram(extracted_routes)
    else:
        app = create_app()

        # Set the FLASK_APP environment variable
        os.environ["FLASK_APP"] = "app.py"

        # Add route to serve the Vue.js application
        @app.route('/')
        def index():
            return render_template('index.html')

        # Add route to serve the documentation page
        @app.route('/docs')
        def docs():
            return render_template('index.html')

        # Run the Flask application with the debugger enabled
        # Add host='0.0.0.0' to make it accessible from outside the container
        # Add allow_unsafe_werkzeug=True to avoid the Werkzeug warning in Docker
        socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
