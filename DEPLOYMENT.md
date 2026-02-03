# WiFi Penetration Testing Platform - Deployment Guide

## System Requirements

### Hardware
- **WiFi Adapter**: Alfa AWUS036ACH (RTL8812AU chipset) with 2 external antennas
- **CPU**: 4+ cores (for hashcat)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB+ available space
- **GPU**: Optional (NVIDIA for local cracking) or cloud GPU account

### Software
- **OS**: Ubuntu 22.04+, Kali Linux 2023.1+, or Debian 12+
- **Kernel**: 5.15+ (for driver support)
- **Python**: 3.11+
- **Node.js**: 20+ (for frontend development)

## Quick Start Installation

### 1. Clone Repository

```bash
git clone https://github.com/dontcrossconnor/MobileWIFIGHT.git
cd MobileWIFIGHT
```

### 2. Run Installation Script

```bash
sudo ./scripts/install.sh
```

This script will:
- Install all system dependencies (aircrack-ng, hashcat, hcxtools)
- Set up Python virtual environment
- Install Python dependencies
- Create necessary directories
- Download wordlists (rockyou.txt)
- Verify all tools are installed

### 3. Start Backend Server

```bash
cd backend
source venv/bin/activate
python -m app.main
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Manual Installation

If the automatic script fails, follow these steps:

### Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    python3.11 python3-pip python3-venv \
    aircrack-ng hcxtools hashcat \
    wireless-tools net-tools iw ethtool
```

### Install Python Dependencies

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Verify Tools

```bash
aircrack-ng --version
hashcat --version
hcxpcapngtool --version
```

## Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```env
# API Settings
API_TITLE="WiFi Pentester API"
API_VERSION="1.0.0"
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Storage
CAPTURE_DIR=/tmp/wifi-pentester/captures
WORDLIST_DIR=/usr/share/wordlists
DEFAULT_WORDLIST=rockyou.txt

# CORS (for frontend)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### WiFi Adapter Setup

#### 1. Verify Adapter Detection

```bash
lsusb | grep -i realtek
# Should show: Bus XXX Device XXX: ID 0bda:8812 Realtek Semiconductor Corp.
```

#### 2. Check Interface

```bash
iw dev
# Should list your wireless interface (e.g., wlan0)
```

#### 3. Enable Monitor Mode (Testing)

```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan0
# Interface will become wlan0mon
```

#### 4. Verify Monitor Mode

```bash
iw dev
# Should show type: monitor
```

## Running the Application

### Development Mode

```bash
cd backend
source venv/bin/activate
python -m app.main
```

### Production Mode (with Uvicorn)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Auto-reload (Development)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the Installation

### 1. Check API Health

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### 2. Detect WiFi Adapters

```bash
curl -X POST http://localhost:8000/api/v1/adapter/detect
# Should return JSON array of detected adapters
```

### 3. Access API Documentation

Open browser to: http://localhost:8000/docs

You'll see interactive Swagger UI with all API endpoints.

## Using the API

### Example: Start Network Scan

```bash
# 1. Enable monitor mode
curl -X POST "http://localhost:8000/api/v1/adapter/wlan0/monitor-mode?enable=true"

# 2. Start scan
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "interface": "wlan0mon",
    "mode": "passive",
    "hop_interval_ms": 500
  }'

# Save the session_id from response

# 3. Get discovered networks
curl http://localhost:8000/api/v1/scan/{session_id}/networks
```

### Example: Execute Attack

```bash
# 1. Create attack
curl -X POST http://localhost:8000/api/v1/attacks \
  -H "Content-Type: application/json" \
  -d '{
    "target_bssid": "00:11:22:33:44:55",
    "target_essid": "TargetNetwork",
    "attack_type": "handshake_capture",
    "interface": "wlan0mon",
    "channel": 6,
    "duration_seconds": 60
  }'

# Save attack_id from response

# 2. Start attack
curl -X POST http://localhost:8000/api/v1/attacks/{attack_id}/start

# 3. Check status
curl http://localhost:8000/api/v1/attacks/{attack_id}
```

### Example: Crack Password

```bash
# 1. Create cracking job
curl -X POST http://localhost:8000/api/v1/cracking/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "handshake_file": "/tmp/handshake.cap",
    "bssid": "00:11:22:33:44:55",
    "essid": "TargetNetwork",
    "attack_mode": "wordlist",
    "wordlist_path": "/usr/share/wordlists/rockyou.txt",
    "gpu_provider": "local"
  }'

# Save job_id from response

# 2. Start job
curl -X POST http://localhost:8000/api/v1/cracking/jobs/{job_id}/start

# 3. Check progress
curl http://localhost:8000/api/v1/cracking/jobs/{job_id}/progress
```

## Troubleshooting

### Adapter Not Detected

```bash
# Check USB devices
lsusb | grep Realtek

# Check kernel modules
lsmod | grep 8812

# Install driver if needed (Alfa AWUS036ACH)
git clone https://github.com/aircrack-ng/rtl8812au.git
cd rtl8812au
make
sudo make install
sudo modprobe 8812au
```

### Monitor Mode Fails

```bash
# Kill interfering processes
sudo airmon-ng check kill

# Bring interface down
sudo ip link set wlan0 down

# Try again
sudo airmon-ng start wlan0
```

### Hashcat Not Using GPU

```bash
# List devices
hashcat -I

# Benchmark
hashcat -b -m 22000

# If no GPU listed, install NVIDIA drivers:
sudo apt-get install nvidia-driver-525
sudo reboot
```

### Permission Denied Errors

```bash
# Run with sudo
sudo python -m app.main

# Or add user to required groups
sudo usermod -a -G netdev,wireshark $USER
# Logout and login again
```

## Security Notes

⚠️ **CRITICAL WARNINGS**:

1. **Legal**: Only test networks you own or have explicit written permission to test
2. **Root Access**: Application requires root/sudo for packet injection
3. **Network Impact**: Attacks can disrupt network connectivity
4. **Data Exposure**: Captured data may contain sensitive information
5. **Tool Power**: These are real penetration testing tools, not simulations

### Recommended Security Practices

1. **Isolated Environment**: Test in isolated lab environment
2. **Air-gapped Systems**: Use air-gapped machines when possible
3. **Encrypted Storage**: Encrypt captured data and reports
4. **Audit Logging**: Enable comprehensive logging
5. **Access Control**: Restrict who can run attacks
6. **Documentation**: Maintain detailed records of all tests

## Production Deployment

### Using Systemd Service

Create `/etc/systemd/system/wifi-pentester.service`:

```ini
[Unit]
Description=WiFi Pentester API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/wifi-pentester/backend
Environment="PATH=/opt/wifi-pentester/backend/venv/bin"
ExecStart=/opt/wifi-pentester/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable wifi-pentester
sudo systemctl start wifi-pentester
sudo systemctl status wifi-pentester
```

### Using Docker (Optional)

```bash
# Build image
docker build -t wifi-pentester -f Dockerfile .

# Run with privileged mode (required for WiFi)
docker run -d --privileged --network host \
  -v /tmp/wifi-pentester:/tmp/wifi-pentester \
  wifi-pentester
```

## Updating

```bash
cd MobileWIFIGHT
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## Uninstallation

```bash
# Stop service if running
sudo systemctl stop wifi-pentester
sudo systemctl disable wifi-pentester

# Remove files
rm -rf /opt/wifi-pentester
rm /etc/systemd/system/wifi-pentester.service

# Remove system packages (optional)
sudo apt-get remove aircrack-ng hcxtools hashcat
```

## Support

- **GitHub**: https://github.com/dontcrossconnor/MobileWIFIGHT
- **Issues**: https://github.com/dontcrossconnor/MobileWIFIGHT/issues
- **Docs**: See repository documentation

## License

MIT License - See LICENSE file for details.

---

**Remember**: With great power comes great responsibility. Use ethically and legally.
