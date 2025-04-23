#!/bin/bash

# Initialize the banking application

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Starting MySQL database and initializing with setup.sql..."
docker-compose up -d mysql

# Wait for MySQL to be ready
echo "Waiting for MySQL to initialize (this may take a minute)..."
sleep 20

echo "Starting Keycloak authentication server..."
docker-compose up -d keycloak

# Note: For development, we'll directly run the Flask app outside Docker for easier debugging
echo "All services started. You can now run the Flask app with:"
echo "python debug.py"
echo ""
echo "Or start everything in Docker with:"
echo "docker-compose up"
echo ""
echo "Database credentials:"
echo "Host: localhost"
echo "Port: 3306"
echo "User: root"
echo "Password: example"
echo "Database: bankarstvo"