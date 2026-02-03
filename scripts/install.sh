#!/bin/bash
# WiFi Pentester - Installation Script
# This script installs all dependencies and sets up the environment

set -e

echo "========================================="
echo "WiFi Pentester - Installation Script"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run as root"
    echo "Please run: sudo ./install.sh"
    exit 1
fi

echo "[1/7] Updating package lists..."
apt-get update

echo "[2/7] Installing system dependencies..."
apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    aircrack-ng \
    hcxtools \
    hashcat \
    wireless-tools \
    net-tools \
    iw \
    ethtool \
    lsb-release \
    wget \
    curl \
    git

echo "[3/7] Installing Node.js (if not installed)..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

echo "[4/7] Setting up Python virtual environment..."
cd /workspace/backend
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[5/7] Creating necessary directories..."
mkdir -p /tmp/wifi-pentester/captures
mkdir -p /var/log/wifi-pentester
chmod 755 /tmp/wifi-pentester
chmod 755 /var/log/wifi-pentester

echo "[6/7] Installing wordlists..."
if [ ! -d "/usr/share/wordlists" ]; then
    mkdir -p /usr/share/wordlists
fi

if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    echo "Downloading rockyou.txt wordlist..."
    cd /usr/share/wordlists
    if [ -f "rockyou.txt.gz" ]; then
        gunzip rockyou.txt.gz
    else
        echo "Note: rockyou.txt not found. You may need to install it manually."
        echo "On Kali Linux: apt-get install wordlists"
    fi
fi

echo "[7/7] Verifying tools..."
echo -n "  aircrack-ng: "
if command -v aircrack-ng &> /dev/null; then
    echo "✓ Installed"
else
    echo "✗ NOT FOUND"
fi

echo -n "  hashcat: "
if command -v hashcat &> /dev/null; then
    echo "✓ Installed"
else
    echo "✗ NOT FOUND"
fi

echo -n "  hcxpcapngtool: "
if command -v hcxpcapngtool &> /dev/null; then
    echo "✓ Installed"
else
    echo "✗ NOT FOUND"
fi

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Start the backend server:"
echo "   cd /workspace/backend"
echo "   source venv/bin/activate"
echo "   python -m app.main"
echo ""
echo "2. The API will be available at:"
echo "   http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "3. Make sure you have a compatible WiFi adapter"
echo "   (Alfa AWUS036ACH recommended)"
echo ""
echo "⚠️  WARNING: Only use on networks you own or have"
echo "    explicit permission to test!"
echo ""
