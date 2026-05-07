#!/bin/bash
# FieldNode Docker Startup Script
# Requires Docker and Docker Compose to be installed

set -e

echo "=========================================="
echo "FieldNode - Docker Startup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "   Install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker daemon is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker daemon is not running."
    echo "   Start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is available"
echo ""

# Build and start services
echo "Starting FieldNode services..."
echo ""

docker-compose up -d

echo ""
echo "✓ Services started"
echo ""
echo "=========================================="
echo "FieldNode is ready"
echo "=========================================="
echo ""
echo "API:       http://localhost:8000"
echo "Swagger:   http://localhost:8000/swagger/"
echo "Admin:     http://localhost:8000/admin/"
echo "MySQL:     localhost:3306"
echo "MQTT:      localhost:1883"
echo ""
echo "Log in to API:"
echo "  docker exec fieldnode-api python manage.py createsuperuser"
echo ""
echo "View logs:"
echo "  docker-compose logs -f api"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
