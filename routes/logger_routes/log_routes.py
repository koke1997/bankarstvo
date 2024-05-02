from flask import Blueprint, send_file, current_app
import logging

log_routes = Blueprint('log_routes', __name__)

# Enhanced logging configuration
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@log_routes.route('/logs', methods=['GET'])
def get_logs():
    current_app.logger.info("Serving log file to user")
    return send_file('app.log', mimetype='text/plain')
