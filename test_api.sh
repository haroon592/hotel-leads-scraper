#!/bin/bash

# Test script for your Fly.io API
# Usage: ./test_api.sh your-app-name

if [ -z "$1" ]; then
    echo "Usage: ./test_api.sh your-app-name"
    echo "Example: ./test_api.sh hotel-leads-scraper-abc123"
    exit 1
fi

APP_NAME=$1
BASE_URL="https://${APP_NAME}.fly.dev"

echo "Testing API at: $BASE_URL"
echo "================================"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
curl -s "${BASE_URL}/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Status Check
echo "Test 2: Status Check"
echo "--------------------"
curl -s "${BASE_URL}/status" | python3 -m json.tool
echo ""
echo ""

# Test 3: Progress Check
echo "Test 3: Progress Check"
echo "----------------------"
curl -s "${BASE_URL}/progress" | python3 -m json.tool
echo ""
echo ""

echo "================================"
echo "Basic tests complete!"
echo ""
echo "To start a scraping job, run:"
echo "curl -X POST ${BASE_URL}/scrape"
echo ""
echo "To check results, run:"
echo "curl ${BASE_URL}/results"
