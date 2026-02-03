#!/bin/bash
# Run Playwright E2E Tests

set -e

echo "========================================="
echo "WiFi Pentester - E2E Test Suite"
echo "========================================="
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend server not running!"
    echo ""
    echo "Please start backend in another terminal:"
    echo "  ./scripts/start-backend.sh"
    echo ""
    exit 1
fi

echo "✓ Backend server is running"
echo ""

cd /workspace/frontend

# Install Playwright browsers if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Installing Playwright browsers..."
npx playwright install chromium

echo ""
echo "Running E2E tests..."
echo ""

# Run tests
npm run test:e2e

echo ""
echo "========================================="
echo "E2E Tests Complete"
echo "========================================="
echo ""
echo "View HTML report:"
echo "  npx playwright show-report"
echo ""
