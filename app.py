import os
import logging
import argparse
from app_factory import create_app, socketio
from utils.diagnostic_routes import register_diagnostic_routes

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Set root logger to DEBUG level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('app.log')  # Also log to file
    ]
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-diagram", action="store_true", help="Display routes diagram")
    args = parser.parse_args()

    if args.diagram:
        from core.plot_diagram import plot_routes_diagram, extract_all_routes
        extracted_routes = extract_all_routes()
        plot_routes_diagram(extracted_routes)
    else:
        app = create_app()

        # Register diagnostic routes
        register_diagnostic_routes(app)

        # Log all registered routes at startup
        logger.info("===== REGISTERED ROUTES =====")
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
            logger.info(f"Route: {rule.rule} - Methods: {', '.join(rule.methods - {'HEAD', 'OPTIONS'})}")
        logger.info("============================")

        # Run the Flask application with the debugger enabled
        logger.info("Starting the server...")

        try:
            # Run with Flask-SocketIO using threading mode
            logger.info("Running Flask app with SocketIO (threading mode)")
            socketio.run(
                app, 
                debug=True, 
                host='0.0.0.0', 
                use_reloader=True,
                log_output=True  # Show SocketIO logs
            )
        except Exception as e:
            logger.error(f"Failed to start with SocketIO: {e}")
            logger.info("Falling back to Flask's standard server")
            app.run(debug=True, host='0.0.0.0')
