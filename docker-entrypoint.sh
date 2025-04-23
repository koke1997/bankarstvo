#!/bin/bash
# Django application entrypoint script for Docker
set -e

# Function to check if MySQL is ready
function wait_for_mysql() {
    echo "Waiting for MySQL to be ready..."
    while ! nc -z ${DATABASE_HOST:-db} ${DATABASE_PORT:-3306}; do
        sleep 1
    done
    echo "MySQL is ready!"
}

# Function to run migrations
function run_migrations() {
    echo "Running Django migrations..."
    python manage.py migrate --noinput
}

# Function to collect static files
function collect_static() {
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
}

# Function to start the Django server
function start_server() {
    echo "Starting Django server..."
    if [ "${DJANGO_USE_ASGI:-False}" = "True" ]; then
        # Use Daphne for ASGI/WebSocket support
        daphne -b 0.0.0.0 -p 8000 bankarstvo_django.asgi:application
    else
        # Use regular Django runserver
        python manage.py runserver 0.0.0.0:8000
    fi
}

# Main execution flow
echo "Starting Django application..."

# Check if we're running in Docker
if [ -n "$DATABASE_HOST" ]; then
    wait_for_mysql
fi

# Run migrations if needed
if [ "${DJANGO_RUN_MIGRATIONS:-True}" = "True" ]; then
    run_migrations
fi

# Collect static files if needed
if [ "${DJANGO_COLLECT_STATIC:-True}" = "True" ]; then
    collect_static
fi

# Run the Django health check
echo "Running Django health check..."
python manage.py check_django_setup

# Start the server
start_server