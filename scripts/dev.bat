@echo off
SETLOCAL

echo ===== Starting Bankarstvo Development Environment =====

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if containers are already running
docker ps -q -f name=bankarstvo-mysql >nul 2>&1
set MYSQL_RUNNING=%ERRORLEVEL%
docker ps -q -f name=bankarstvo-keycloak >nul 2>&1
set KEYCLOAK_RUNNING=%ERRORLEVEL%

REM Start containers if not running
if %MYSQL_RUNNING% EQU 0 (
    if %KEYCLOAK_RUNNING% EQU 0 (
        echo [INFO] MySQL and Keycloak containers are already running
    ) else (
        echo [INFO] Starting containers...
        docker-compose up -d
    )
) else (
    echo [INFO] Starting containers...
    docker-compose up -d
)

echo [INFO] Waiting for MySQL to initialize (this may take a moment)...
timeout /t 20 /nobreak >nul

echo [INFO] MySQL should be ready
echo [INFO] Keycloak should be starting at http://localhost:3790

REM Initialize database
echo [INFO] Initializing database...
mysql -h localhost -u root -pexample bankarstvo < setup.sql
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to initialize database. Please check if MySQL is running.
) else (
    echo [INFO] Database initialized successfully
)

REM Setup instructions
echo.
echo ===== Development Environment Ready =====
echo MySQL Database:
echo   - Host: localhost
echo   - Port: 3306
echo   - User: root
echo   - Password: example
echo   - Database: bankarstvo
echo.
echo Keycloak:
echo   - URL: http://localhost:3790
echo   - Admin Console: http://localhost:3790/admin
echo   - Username: admin
echo   - Password: admin

echo.
echo ===== Start Flask Application =====
echo Now you can start your Flask application with:
echo   python debug.py
echo.
echo To stop the Docker containers when done:
echo   docker-compose down

ENDLOCAL