import os
import subprocess
from app_factory import create_app
import argparse
from core.plot_diagram import plot_routes_diagram, extract_all_routes

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
            return app.send_static_file('index.html')

        # Run the Flask application with the debugger enabled
        subprocess.run(["flask", "run", "--debugger"])
