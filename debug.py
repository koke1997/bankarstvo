#!/usr/bin/env python
"""
Development server script for running the banking application locally
while using containerized services (MySQL, Keycloak).
"""
import os
from dotenv import load_dotenv
from app_factory import create_app, socketio

# Load environment variables from .env file
load_dotenv()

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    print("Starting development server...")
    print(f"DATABASE_HOST: {os.getenv('DATABASE_HOST')}")
    print(f"KEYCLOAK_AUTH_SERVER_URL: {os.getenv('KEYCLOAK_AUTH_SERVER_URL')}")
    print("Debug mode: ON")
    print("Open http://localhost:5000 in your browser")
    # Run the application with socketio and debug enabled
    # Removed the allow_unsafe_werkzeug parameter as it's not supported by eventlet
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)