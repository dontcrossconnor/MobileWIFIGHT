#!/bin/bash
# Start Backend Server

set -e

echo "Starting WiFi Pentester Backend..."

cd /workspace/backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running installation..."
    cd /workspace
    sudo ./scripts/install.sh
    cd /workspace/backend
fi

# Activate venv
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
    echo "⚠️  Edit backend/.env to add your cloud GPU API keys if needed"
fi

# Create capture directory
mkdir -p /tmp/wifi-pentester/captures

# Start server
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m app.main
