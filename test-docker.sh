#!/bin/bash

# Test script for Docker setup
# This runs a quick test to verify the Docker image works

echo "======================================"
echo "Testing Docker Image for Hotel Scraper"
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your credentials"
    exit 1
fi

echo "✓ .env file found"

# Build the Docker image
echo ""
echo "Building Docker image..."
docker build -t hotel-scraper-test . || {
    echo "❌ Docker build failed!"
    exit 1
}

echo "✓ Docker image built successfully"

# Test the image by running Python
echo ""
echo "Testing Python in container..."
docker run --rm hotel-scraper-test python --version || {
    echo "❌ Python test failed!"
    exit 1
}

echo "✓ Python is working"

# Test Chrome installation
echo ""
echo "Testing Chrome installation..."
docker run --rm hotel-scraper-test google-chrome --version || {
    echo "❌ Chrome test failed!"
    exit 1
}

echo "✓ Chrome is installed"

# Test ChromeDriver
echo ""
echo "Testing ChromeDriver..."
docker run --rm hotel-scraper-test chromedriver --version || {
    echo "❌ ChromeDriver test failed!"
    exit 1
}

echo "✓ ChromeDriver is installed"

# Test Python dependencies
echo ""
echo "Testing Python dependencies..."
docker run --rm hotel-scraper-test python -c "import selenium; print('Selenium:', selenium.__version__)" || {
    echo "❌ Selenium import failed!"
    exit 1
}

echo "✓ All dependencies are installed"

echo ""
echo "======================================"
echo "✅ All tests passed!"
echo "======================================"
echo ""
echo "To run the scraper:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop:"
echo "  docker-compose down"
echo "======================================"
