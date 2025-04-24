from flask import Blueprint, jsonify, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from core.models import User
from utils.extensions import db, bcrypt
import logging
import jwt
import datetime

# Create a blueprint for authentication API endpoints
auth_api = Blueprint('auth_api', __name__)
logger = logging.getLogger(__name__)

@auth_api.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    Expects JSON with username, password, email, and optional fullName
    """
    try:
        data = request.get_json(force=True)
        logger.debug(f"Register request received: {data}")
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided",
                "message": "Please provide registration information"
            }), 400
        
        required_fields = ['username', 'password', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}",
                    "message": f"Please provide {field}"
                }), 400
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({
                "success": False,
                "error": "Username exists",
                "message": "Username already exists"
            }), 400
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({
                "success": False,
                "error": "Email exists",
                "message": "Email already in use"
            }), 400
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password,
            full_name=data.get('fullName', '')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the new user
        login_user(new_user)
        
        # Generate a JWT token
        token = generate_token(new_user)
        
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "token": token,
            "data": {
                "id": str(new_user.user_id),
                "username": new_user.username,
                "email": new_user.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering user: {e}")
        return jsonify({
            "success": False,
            "error": "Registration failed",
            "message": str(e)
        }), 500

@auth_api.route('/login', methods=['POST'])
def login():
    """
    Log in an existing user
    Expects JSON with username and password
    """
    try:
        # Enhanced and detailed logging
        logger.info(f"API login request received - Method: {request.method}, Path: {request.path}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Form data: {dict(request.form)}")
        
        # Try multiple ways to get the data
        data = None
        
        # Method 1: Try to get JSON directly
        try:
            data = request.get_json(silent=True)
            if data:
                logger.info(f"Successfully parsed JSON data: {data}")
        except Exception as e:
            logger.error(f"Error parsing JSON: {str(e)}")
        
        # Method 2: Try to get JSON with force option
        if not data:
            try:
                data = request.get_json(force=True)
                if data:
                    logger.info(f"Successfully parsed forced JSON data: {data}")
            except Exception as e:
                logger.error(f"Error parsing forced JSON: {str(e)}")
        
        # Method 3: Try to use form data
        if not data and request.form:
            data = dict(request.form)
            logger.info(f"Using form data: {data}")
        
        # Method 4: Try to get raw data and parse it
        if not data and request.data:
            try:
                import json
                data = json.loads(request.data.decode('utf-8'))
                logger.info(f"Parsed raw request data: {data}")
            except Exception as e:
                logger.error(f"Error parsing raw data: {str(e)}")
                logger.info(f"Raw data content: {request.data}")
        
        # Log what we found
        if data:
            logger.info(f"Final data used for login: {data}")
        else:
            logger.error("Could not extract any data from request")
            return jsonify({
                "success": False,
                "error": "No data provided", 
                "message": "Could not extract login data from request"
            }), 400
        
        # Check required fields
        required_fields = ['username', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(f"Missing fields in login request: {missing_fields}")
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "message": f"Please provide all required fields: {', '.join(missing_fields)}"
            }), 400
        
        username = data['username']
        password = data['password']
        
        logger.info(f"Looking up user: {username}")
        
        # Try to find user by username or email
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if not user:
            logger.warning(f"User not found: {username}")
            return jsonify({
                "success": False,
                "error": "Invalid credentials",
                "message": "Invalid username or password"
            }), 401
        
        logger.info(f"User found: {user.username}, ID: {user.user_id}")
        
        # Check password
        if not hasattr(user, 'password_hash'):
            logger.error(f"User {username} has no password_hash attribute")
            return jsonify({
                "success": False,
                "error": "Account error",
                "message": "Authentication failed - account issue"
            }), 500
        
        if not user.password_hash:
            logger.error(f"User {username} has empty password hash")
            return jsonify({
                "success": False,
                "error": "Account error",
                "message": "Authentication failed - password not set"
            }), 500
        
        # Verify password
        password_valid = bcrypt.check_password_hash(user.password_hash, password)
        logger.info(f"Password validation result for {username}: {password_valid}")
        
        if not password_valid:
            logger.warning(f"Invalid password for user: {username}")
            return jsonify({
                "success": False,
                "error": "Invalid credentials",
                "message": "Invalid username or password"
            }), 401
        
        # Login successful
        login_user(user)
        logger.info(f"User {username} logged in successfully via API")
        
        # Generate a JWT token
        token = generate_token(user)
        logger.info(f"Generated token for user {username}")
        
        # Build response
        response_data = {
            "success": True,
            "message": "Login successful",
            "token": token,
            "data": {
                "id": str(user.user_id),
                "username": user.username,
                "email": getattr(user, 'email', '')
            }
        }
        
        logger.info(f"Sending successful login response for {username}")
        logger.debug(f"Response data: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error in login process: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Server error",
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500

@auth_api.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Log out the current user
    """
    try:
        logout_user()
        return jsonify({"message": "Logout successful"})
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        return jsonify({"error": str(e)}), 500

@auth_api.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get the current authenticated user
    """
    try:
        return jsonify({
            "id": current_user.user_id,
            "username": current_user.username,
            "email": current_user.email,
            "fullName": current_user.full_name
        })
    except Exception as e:
        logger.error(f"Error retrieving current user: {e}")
        return jsonify({"error": str(e)}), 500

def generate_token(user):
    """
    Generate a JWT token for the given user
    """
    try:
        secret_key = current_app.config['SECRET_KEY']
        
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user.user_id
        }
        
        token = jwt.encode(
            payload,
            secret_key,
            algorithm='HS256'
        )
        
        # Convert bytes to string if needed (depending on jwt version)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        logger.debug(f"Generated token for user ID {user.user_id}")
        return token
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        # Return a placeholder token for emergencies
        return "emergency_token_" + str(user.user_id)