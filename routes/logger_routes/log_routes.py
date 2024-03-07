from flask import Blueprint, send_file

log_routes = Blueprint('log_routes', __name__)

@log_routes.route('/logs', methods=['GET'])
def get_logs():
    return send_file('app.log', mimetype='text/plain')