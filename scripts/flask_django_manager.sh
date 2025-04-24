#!/bin/bash
# flask_django_manager.sh - Script for managing the Flask to Django transition

set -e  # Exit on error

# Define colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_header() {
  echo -e "${BLUE}=============================================================${NC}"
  echo -e "${GREEN}$1${NC}"
  echo -e "${BLUE}=============================================================${NC}"
}

function print_section() {
  echo -e "${YELLOW}$1${NC}"
}

function print_error() {
  echo -e "${RED}ERROR: $1${NC}"
}

# Check if required commands are available
command -v docker-compose >/dev/null 2>&1 || { print_error "docker-compose is required but not installed. Aborting."; exit 1; }

function show_help() {
  print_header "Flask to Django Migration Manager"
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  start-flask        Start the Flask application"
  echo "  start-django       Start the Django application"
  echo "  start-hybrid       Start both Flask and Django applications"
  echo "  migrate-data       Migrate data from Flask to Django"
  echo "  make-migrations    Run Django makemigrations"
  echo "  migrate            Run Django migrations"
  echo "  django-shell       Access Django shell"
  echo "  flask-shell        Access Flask shell"
  echo "  clean              Stop all containers and clean volumes"
  echo "  help               Show this help message"
  echo ""
}

function start_flask() {
  print_header "Starting Flask Application"
  docker-compose up -d flask db keycloak
  echo -e "${GREEN}Flask application is running at: http://localhost:5000${NC}"
}

function start_django() {
  print_header "Starting Django Application"
  docker-compose -f docker-compose-hybrid.yml up -d django db keycloak
  echo -e "${GREEN}Django application is running at: http://localhost:8000${NC}"
}

function start_hybrid() {
  print_header "Starting Hybrid Mode (Flask + Django)"
  docker-compose -f docker-compose-hybrid.yml up -d
  echo -e "${GREEN}Flask application is running at: http://localhost:5000${NC}"
  echo -e "${GREEN}Django application is running at: http://localhost:8000${NC}"
}

function migrate_data() {
  print_header "Migrating Data from Flask to Django"
  print_section "This will migrate all data from your Flask database to Django."
  read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Make sure the containers are running
    docker-compose -f docker-compose-hybrid.yml up -d django db
    # Run the migration command
    docker-compose -f docker-compose-hybrid.yml exec django python manage.py migrate_flask_data
    echo -e "${GREEN}Data migration completed.${NC}"
  else
    echo "Data migration cancelled."
  fi
}

function make_migrations() {
  print_header "Running Django makemigrations"
  docker-compose -f docker-compose-hybrid.yml exec django python manage.py makemigrations
}

function migrate() {
  print_header "Running Django migrations"
  docker-compose -f docker-compose-hybrid.yml exec django python manage.py migrate
}

function django_shell() {
  print_header "Accessing Django shell"
  docker-compose -f docker-compose-hybrid.yml exec django python manage.py shell
}

function flask_shell() {
  print_header "Accessing Flask shell"
  docker-compose exec flask python -c "from app_factory import create_app; app = create_app(); from flask.globals import _app_ctx_stack; _app_ctx_stack.push(app.app_context()); print('Flask app context created. You can now work with your Flask application.')"
}

function clean() {
  print_header "Cleaning Environment"
  print_section "This will stop all containers and remove volumes."
  read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose-hybrid.yml down -v
    echo -e "${GREEN}Environment cleaned.${NC}"
  else
    echo "Clean operation cancelled."
  fi
}

# Check command line arguments
if [ $# -lt 1 ]; then
  show_help
  exit 0
fi

# Process commands
case "$1" in
  start-flask)
    start_flask
    ;;
  start-django)
    start_django
    ;;
  start-hybrid)
    start_hybrid
    ;;
  migrate-data)
    migrate_data
    ;;
  make-migrations)
    make_migrations
    ;;
  migrate)
    migrate
    ;;
  django-shell)
    django_shell
    ;;
  flask-shell)
    flask_shell
    ;;
  clean)
    clean
    ;;
  help)
    show_help
    ;;
  *)
    print_error "Unknown command: $1"
    show_help
    exit 1
    ;;
esac