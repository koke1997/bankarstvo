import os
import logging
import importlib
from app_factory import create_app, socketio
import argparse
from core.plot_diagram import plot_routes_diagram, extract_all_routes
from flask import render_template, send_from_directory, jsonify, request
from flask_login import login_user
from core.models import User
from utils.extensions import db, bcrypt
import traceback
import json

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

# Set specific loggers to DEBUG level
for module in ['web.user.login', 'web.account.dashboard', 'core.models', 'utils.extensions', 'api.rest.routes.auth_routes']:
    logging.getLogger(module).setLevel(logging.DEBUG)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-diagram", action="store_true", help="Display routes diagram")
    args = parser.parse_args()

    if args.diagram:
        extracted_routes = extract_all_routes()
        plot_routes_diagram(extracted_routes)
    else:
        app = create_app()
        
        # Log all registered routes at startup
        logger.info("===== REGISTERED ROUTES =====")
        for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
            logger.info(f"Route: {rule.rule} - Methods: {', '.join(rule.methods - {'HEAD', 'OPTIONS'})}")
        logger.info("============================")
        
        # Special route to test API auth directly
        @app.route('/api-login-test', methods=['GET', 'POST'])
        def api_login_test():
            """Special diagnostic route to test login directly"""
            if request.method == 'GET':
                return '''
                <html>
                <head><title>API Login Test</title></head>
                <body>
                    <h1>API Login Test</h1>
                    <form method="post">
                        <label>Username: <input type="text" name="username"></label><br>
                        <label>Password: <input type="password" name="password"></label><br>
                        <button type="submit">Login</button>
                    </form>
                </body>
                </html>
                '''
            else:
                # Log all information about the request
                logger.info("===== API LOGIN TEST =====")
                logger.info(f"Method: {request.method}")
                logger.info(f"Headers: {dict(request.headers)}")
                logger.info(f"Form data: {dict(request.form)}")
                logger.info(f"JSON data: {request.get_json(silent=True)}")
                logger.info(f"Raw data: {request.data}")
                
                # Extract credentials
                if request.form:
                    username = request.form.get('username')
                    password = request.form.get('password')
                    logger.info(f"Form credentials - Username: {username}, Password: {'*' * len(password) if password else None}")
                else:
                    try:
                        data = request.get_json(force=True) if request.data else None
                        username = data.get('username') if data else None
                        password = data.get('password') if data else None
                        logger.info(f"JSON credentials - Username: {username}, Password: {'*' * len(password) if password else None}")
                    except Exception as e:
                        logger.error(f"Error parsing request data: {e}")
                        return jsonify({
                            "success": False,
                            "error": "Invalid request",
                            "message": f"Error parsing request data: {str(e)}"
                        }), 400
                
                if not username or not password:
                    return jsonify({
                        "success": False,
                        "error": "Missing credentials",
                        "message": "Username and password are required"
                    }), 400
                
                # Try to find user and validate credentials
                try:
                    user = User.query.filter((User.username == username) | (User.email == username)).first()
                    
                    if not user:
                        logger.warning(f"User not found: {username}")
                        return jsonify({
                            "success": False,
                            "error": "Invalid credentials",
                            "message": "User not found"
                        }), 401
                    
                    # Check password
                    if not hasattr(user, 'password_hash') or not user.password_hash:
                        logger.error(f"User {username} has no valid password hash")
                        return jsonify({
                            "success": False,
                            "error": "Account error",
                            "message": "Account has authentication issues"
                        }), 500
                    
                    # Verify password
                    password_valid = bcrypt.check_password_hash(user.password_hash, password)
                    logger.info(f"Password validation result: {password_valid}")
                    
                    if not password_valid:
                        return jsonify({
                            "success": False,
                            "error": "Invalid credentials",
                            "message": "Invalid password"
                        }), 401
                    
                    # Login successful
                    login_user(user)
                    
                    # Return success response
                    response_data = {
                        "success": True,
                        "message": "Login successful",
                        "data": {
                            "id": str(user.user_id),
                            "username": user.username,
                            "email": getattr(user, 'email', '')
                        }
                    }
                    
                    # Log the response
                    logger.info(f"Successful login for user: {username}")
                    logger.info(f"Response data: {response_data}")
                    
                    return jsonify(response_data)
                    
                except Exception as e:
                    logger.error(f"Error in login test: {e}")
                    logger.error(traceback.format_exc())
                    return jsonify({
                        "success": False,
                        "error": "Server error",
                        "message": str(e)
                    }), 500
                    
        # Create a special diagnostic page to test everything
        @app.route('/diagnostic', methods=['GET'])
        def diagnostic_page():
            """Page with various diagnostic tools"""
            return '''
            <html>
            <head>
                <title>Banking App Diagnostics</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    .section { margin-bottom: 30px; }
                    form { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                    button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
                    input, textarea { margin: 5px 0; padding: 8px; width: 300px; }
                    .code { font-family: monospace; background: #f0f0f0; padding: 10px; white-space: pre-wrap; }
                </style>
            </head>
            <body>
                <h1>Banking App Diagnostics</h1>
                
                <div class="section">
                    <h2>API Login Test</h2>
                    <form id="api-login-form" method="post" action="/api-login-test">
                        <div>
                            <label>Username: <input type="text" name="username" required></label>
                        </div>
                        <div>
                            <label>Password: <input type="password" name="password" required></label>
                        </div>
                        <button type="submit">Test Login</button>
                    </form>
                </div>
                
                <div class="section">
                    <h2>Direct API JSON Login Test</h2>
                    <form id="json-login-form">
                        <div>
                            <label>Username: <input type="text" id="json-username" required></label>
                        </div>
                        <div>
                            <label>Password: <input type="password" id="json-password" required></label>
                        </div>
                        <div>
                            <label>Target URL: <input type="text" id="target-url" value="/api/auth/login"></label>
                        </div>
                        <button type="button" id="json-login-btn">Send JSON Login</button>
                    </form>
                    <div>
                        <h3>Request:</h3>
                        <pre id="request-json" class="code"></pre>
                        <h3>Response:</h3>
                        <pre id="response-json" class="code"></pre>
                    </div>
                </div>
                
                <script>
                    document.getElementById('json-login-btn').addEventListener('click', async function() {
                        const username = document.getElementById('json-username').value;
                        const password = document.getElementById('json-password').value;
                        const url = document.getElementById('target-url').value;
                        
                        const requestData = {
                            username: username,
                            password: password
                        };
                        
                        document.getElementById('request-json').textContent = JSON.stringify(requestData, null, 2);
                        
                        try {
                            const response = await fetch(url, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(requestData)
                            });
                            
                            const responseData = await response.json();
                            document.getElementById('response-json').textContent = 
                                `Status: ${response.status} ${response.statusText}\n\n` +
                                JSON.stringify(responseData, null, 2);
                        } catch (error) {
                            document.getElementById('response-json').textContent = 
                                `Error: ${error.message}`;
                        }
                    });
                </script>
            </body>
            </html>
            '''
        
        # Direct API login endpoint to handle React frontend requests
        @app.route('/api/auth/login', methods=['POST'])
        def direct_api_login():
            logger.debug(f"Direct API login endpoint called with method: {request.method}")
            logger.debug(f"Request headers: {dict(request.headers)}")
            try:
                data = request.get_json(force=True)
                logger.debug(f"Received login data: {data}")
                
                if not data or 'username' not in data or 'password' not in data:
                    logger.warning("Missing username or password in request")
                    return jsonify({
                        "success": False,
                        "error": "Missing username or password",
                        "message": "Please provide both username and password"
                    }), 400
                
                username = data['username']
                password = data['password']
                
                # Look up user
                user = User.query.filter((User.username == username) | (User.email == username)).first()
                
                if not user:
                    logger.warning(f"User not found: {username}")
                    return jsonify({
                        "success": False, 
                        "error": "Invalid credentials", 
                        "message": "Invalid username or password"
                    }), 401
                
                # Verify password
                if not bcrypt.check_password_hash(user.password_hash, password):
                    logger.warning(f"Invalid password for user: {username}")
                    return jsonify({
                        "success": False, 
                        "error": "Invalid credentials", 
                        "message": "Invalid username or password"
                    }), 401
                
                # Login successful
                login_user(user)
                logger.info(f"User {username} logged in successfully via direct API")
                
                # Create token
                token = "temporary_token_" + str(user.user_id)  # Replace with proper JWT token generation
                
                # Return success response matching frontend expectations
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "id": str(user.user_id),  # Convert to string as frontend uses this as token
                        "username": user.username,
                        "email": getattr(user, 'email', '')
                    }
                })
                
            except Exception as e:
                logger.error(f"Error in direct API login: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    "success": False,
                    "error": "Server error", 
                    "message": "An error occurred during login"
                }), 500

        # Set the FLASK_APP environment variable
        os.environ["FLASK_APP"] = "app.py"

        # Test route to confirm basic server functionality
        @app.route('/api/test')
        def test_route():
            return jsonify({"status": "success", "message": "Server is working correctly!"})

        # Add explicit route for the JavaScript bundle
        @app.route('/bundle.<path:filename>')
        def serve_bundle(filename):
            logger.info(f"Serving bundle file: {filename}")
            return send_from_directory('static/js/react-app', f'bundle.{filename}')

        # Add route to serve the React application
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_react_app(path):
            logger.info(f"Request for path: {path}")
            # First, try to serve static files
            if path and os.path.exists(os.path.join(app.static_folder, path)):
                logger.info(f"Serving static file: {path}")
                return send_from_directory(app.static_folder, path)
            
            # For the React app, serve the index.html for any other routes
            # This allows client-side routing to work
            logger.info(f"Serving React index.html for path: {path}")
            return send_from_directory('static/js/react-app', 'index.html')
            
        # Add route to serve the documentation page
        @app.route('/docs')
        def docs():
            return render_template('docs.html')

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
