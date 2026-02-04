#!/bin/bash
# Start Frontend Development Server

set -e

echo "Starting WiFi Pentester Frontend..."

cd /workspace/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
fi

echo ""
echo "Starting Vite dev server on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
