@echo off
REM flask_django_manager.bat - Script for managing the Flask to Django transition on Windows

setlocal enabledelayedexpansion

REM Define colors for better readability (Windows command prompt)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m" 
set "BLUE=[94m"
set "NC=[0m"

REM Check if required commands are available
where docker-compose >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_error "docker-compose is required but not installed. Aborting."
    exit /b 1
)

if "%~1"=="" (
    call :show_help
    exit /b 0
)

REM Process commands
if "%~1"=="start-flask" (
    call :start_flask
) else if "%~1"=="start-django" (
    call :start_django
) else if "%~1"=="start-hybrid" (
    call :start_hybrid
) else if "%~1"=="migrate-data" (
    call :migrate_data
) else if "%~1"=="make-migrations" (
    call :make_migrations
) else if "%~1"=="migrate" (
    call :migrate
) else if "%~1"=="django-shell" (
    call :django_shell
) else if "%~1"=="flask-shell" (
    call :flask_shell
) else if "%~1"=="clean" (
    call :clean
) else if "%~1"=="help" (
    call :show_help
) else (
    call :print_error "Unknown command: %~1"
    call :show_help
    exit /b 1
)

exit /b 0

:print_header
    echo %BLUE%=============================================================%NC%
    echo %GREEN%%~1%NC%
    echo %BLUE%=============================================================%NC%
    exit /b 0

:print_section
    echo %YELLOW%%~1%NC%
    exit /b 0

:print_error
    echo %RED%ERROR: %~1%NC%
    exit /b 0

:show_help
    call :print_header "Flask to Django Migration Manager"
    echo Usage: %0 [command]
    echo.
    echo Commands:
    echo   start-flask        Start the Flask application
    echo   start-django       Start the Django application
    echo   start-hybrid       Start both Flask and Django applications
    echo   migrate-data       Migrate data from Flask to Django
    echo   make-migrations    Run Django makemigrations
    echo   migrate            Run Django migrations
    echo   django-shell       Access Django shell
    echo   flask-shell        Access Flask shell
    echo   clean              Stop all containers and clean volumes
    echo   help               Show this help message
    echo.
    exit /b 0

:start_flask
    call :print_header "Starting Flask Application"
    docker-compose up -d flask db keycloak
    echo %GREEN%Flask application is running at: http://localhost:5000%NC%
    exit /b 0

:start_django
    call :print_header "Starting Django Application"
    docker-compose -f docker-compose-hybrid.yml up -d django db keycloak
    echo %GREEN%Django application is running at: http://localhost:8000%NC%
    exit /b 0

:start_hybrid
    call :print_header "Starting Hybrid Mode (Flask + Django)"
    docker-compose -f docker-compose-hybrid.yml up -d
    echo %GREEN%Flask application is running at: http://localhost:5000%NC%
    echo %GREEN%Django application is running at: http://localhost:8000%NC%
    exit /b 0

:migrate_data
    call :print_header "Migrating Data from Flask to Django"
    call :print_section "This will migrate all data from your Flask database to Django."
    
    set /p CONFIRM=Are you sure you want to proceed? (y/n) 
    if /i "!CONFIRM!"=="y" (
        REM Make sure the containers are running
        docker-compose -f docker-compose-hybrid.yml up -d django db
        REM Run the migration command
        docker-compose -f docker-compose-hybrid.yml exec django python manage.py migrate_flask_data
        echo %GREEN%Data migration completed.%NC%
    ) else (
        echo Data migration cancelled.
    )
    exit /b 0

:make_migrations
    call :print_header "Running Django makemigrations"
    docker-compose -f docker-compose-hybrid.yml exec django python manage.py makemigrations
    exit /b 0

:migrate
    call :print_header "Running Django migrations"
    docker-compose -f docker-compose-hybrid.yml exec django python manage.py migrate
    exit /b 0

:django_shell
    call :print_header "Accessing Django shell"
    docker-compose -f docker-compose-hybrid.yml exec django python manage.py shell
    exit /b 0

:flask_shell
    call :print_header "Accessing Flask shell"
    docker-compose exec flask python -c "from app_factory import create_app; app = create_app(); from flask.globals import _app_ctx_stack; _app_ctx_stack.push(app.app_context()); print('Flask app context created. You can now work with your Flask application.')"
    exit /b 0

:clean
    call :print_header "Cleaning Environment"
    call :print_section "This will stop all containers and remove volumes."
    
    set /p CONFIRM=Are you sure you want to proceed? (y/n) 
    if /i "!CONFIRM!"=="y" (
        docker-compose -f docker-compose-hybrid.yml down -v
        echo %GREEN%Environment cleaned.%NC%
    ) else (
        echo Clean operation cancelled.
    )
    exit /b 0