#!/bin/bash

# Development startup script for bankarstvo application

# Colors for console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Starting Bankarstvo Development Environment =====${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Function to check if containers are already running
check_containers() {
    MYSQL_RUNNING=$(docker ps -q -f name=bankarstvo-mysql)
    KEYCLOAK_RUNNING=$(docker ps -q -f name=bankarstvo-keycloak)
    
    if [ ! -z "$MYSQL_RUNNING" ] && [ ! -z "$KEYCLOAK_RUNNING" ]; then
        return 0 # Both running
    else
        return 1 # Not all running
    fi
}

# Start containers if not running
if check_containers; then
    echo -e "${GREEN}✓ MySQL and Keycloak containers are already running${NC}"
else
    echo -e "${YELLOW}➤ Starting MySQL and Keycloak containers...${NC}"
    docker-compose up -d mysql keycloak
    
    echo -e "${YELLOW}➤ Waiting for MySQL to initialize (this may take a moment)...${NC}"
    until docker exec bankarstvo-mysql mysqladmin ping -h localhost -u root -pexample --silent; do
        echo -e "${YELLOW}⟳ Waiting for MySQL...${NC}"
        sleep 3
    done
    
    echo -e "${GREEN}✓ MySQL is ready${NC}"
    echo -e "${GREEN}✓ Keycloak should be starting at http://localhost:3790${NC}"
fi

# Optional: Start PHPMyAdmin if needed
if [[ "$1" == "--with-phpmyadmin" ]]; then
    echo -e "${YELLOW}➤ Starting PHPMyAdmin...${NC}"
    docker-compose up -d phpmyadmin
    echo -e "${GREEN}✓ PHPMyAdmin available at http://localhost:8080${NC}"
fi

# Setup instructions
echo -e "\n${BLUE}===== Development Environment Ready =====${NC}"
echo -e "MySQL Database:"
echo -e "  - Host: ${GREEN}localhost${NC}"
echo -e "  - Port: ${GREEN}3306${NC}"
echo -e "  - User: ${GREEN}root${NC}"
echo -e "  - Password: ${GREEN}example${NC}"
echo -e "  - Database: ${GREEN}bankarstvo${NC}"
echo -e "\nKeycloak:"
echo -e "  - URL: ${GREEN}http://localhost:3790${NC}"
echo -e "  - Admin Console: ${GREEN}http://localhost:3790/admin${NC}"
echo -e "  - Username: ${GREEN}admin${NC}"
echo -e "  - Password: ${GREEN}admin${NC}"

if [[ "$1" == "--with-phpmyadmin" ]]; then
    echo -e "\nPHPMyAdmin:"
    echo -e "  - URL: ${GREEN}http://localhost:8080${NC}"
fi

echo -e "\n${BLUE}===== Start Flask Application =====${NC}"
echo -e "Now you can start your Flask application with:"
echo -e "  ${GREEN}python debug.py${NC}"
echo -e "\nTo stop the Docker containers when done:"
echo -e "  ${GREEN}docker-compose down${NC}"