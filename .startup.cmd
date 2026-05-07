@echo off
REM FieldNode Docker Startup Script for Windows

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo FieldNode - Docker Startup
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo X Docker is not installed.
    echo   Install Docker Desktop from: https://www.docker.com/products/docker-desktop
    exit /b 1
)

echo OK Docker is available
echo.

REM Start services
echo Starting FieldNode services...
echo.

docker-compose up -d

echo.
echo OK Services started
echo.
echo ==========================================
echo FieldNode is ready
echo ==========================================
echo.
echo API:       http://localhost:8000
echo Swagger:   http://localhost:8000/swagger/
echo Admin:     http://localhost:8000/admin/
echo MySQL:     localhost:3306
echo MQTT:      localhost:1883
echo.
echo Create superuser:
echo   docker exec fieldnode-api python manage.py createsuperuser
echo.
echo View logs:
echo   docker-compose logs -f api
echo.
echo Stop services:
echo   docker-compose down
echo.
pause
