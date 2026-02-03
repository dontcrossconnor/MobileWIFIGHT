# 🚀 HOW TO RUN - WiFi Penetration Testing Platform

## ✅ EVERYTHING IS REAL AND FUNCTIONAL

---

## Step-by-Step Instructions

### 1. Install (First Time Only)

```bash
cd /workspace
sudo ./scripts/install.sh
```

**Wait for completion** - Downloads tools and wordlists (5-10 minutes)

### 2. Start Backend (Terminal 1)

```bash
cd /workspace
./scripts/start-backend.sh
```

**Wait for**: "Uvicorn running on http://0.0.0.0:8000"

### 3. Start Frontend (Terminal 2)

```bash
cd /workspace
./scripts/start-frontend.sh
```

**Wait for**: "Local: http://localhost:5173"

### 4. Open Browser

Navigate to: **http://localhost:5173**

---

## Using the App

### 1. Dashboard - Setup Adapter

1. Click **"Detect Adapters"** button
2. Click on your WiFi adapter (should show up in list)
3. Click **"Enable Monitor Mode"** button
4. Wait for confirmation (adapter mode should show "monitor")

### 2. Scanner - Find Networks

1. Click **"Scanner"** in navigation
2. Click **"Start Scan"** button
3. Wait for networks to appear in table (updates every 3 seconds)
4. Click on a network to see details
5. Note the BSSID for attacking

### 3. Attacks - Capture Handshake

1. Click **"Attacks"** in navigation
2. Enter target BSSID (or select from dropdown)
3. Choose **"Handshake Capture"** from attack type
4. Set duration (60 seconds recommended)
5. Click **"Launch Attack"** button
6. Watch progress bar
7. When complete, note the handshake file path in results

### 4. Cracking - Find Password

1. Click **"Cracking"** in navigation
2. Enter handshake file path (from attack results)
3. Enter BSSID and ESSID
4. Select **"Wordlist"** attack mode
5. Select **"Local"** GPU provider (or Vast.ai if configured)
6. Click **"Create Job"** button
7. Watch progress (speed in MH/s, cost tracking)
8. Password shows in green box when cracked

### 5. Wordlists - Manage Lists

1. Click **"Wordlists"** in navigation
2. View all available wordlists
3. Click **"Download Essentials"** to get top 4 wordlists
4. Or download individual wordlists as needed

---

## Running E2E Tests

### Terminal 1: Backend Running

```bash
./scripts/start-backend.sh
```

### Terminal 2: Run Tests

```bash
./scripts/run-e2e-tests.sh
```

**Tests will**:
- Click all buttons
- Fill all forms
- Navigate all views
- Verify functionality
- Take screenshots

---

## What Each Button Does

### Dashboard
- **"Detect Adapters"** → Finds WiFi adapters on your system
- **"Enable/Disable Monitor Mode"** → Toggles packet injection mode

### Scanner
- **"Start Scan"** → Begins network discovery (requires monitor mode)
- **"Stop Scan"** → Stops network discovery
- **Click Network Row** → Shows detailed network info

### Attacks
- **"Launch Attack"** → Executes selected attack type
- **"Stop Attack"** → Cancels running attack
- **Quick Select Dropdown** → Select from scanned networks

### Cracking
- **"Create Job"** → Starts password cracking
- **"Stop Job"** → Cancels cracking and terminates GPU

### Wordlists
- **"Refresh"** → Reloads wordlist status
- **"Download Essentials"** → Downloads top 4 wordlists (RockYou, Common, WiFi, WPA)
- **"Download"** (individual) → Downloads specific wordlist

---

## API Documentation

While backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Troubleshooting

### "No adapters detected"
- Check WiFi adapter is plugged in: `lsusb | grep Realtek`
- Run: `sudo iw dev`

### "Adapter must be in monitor mode"
- Click "Enable Monitor Mode" on Dashboard
- Or manually: `sudo airmon-ng start wlan0`

### "Backend server offline"
- Check Terminal 1 - backend should be running
- Check: `curl http://localhost:8000/health`

### Frontend won't load
- Check Terminal 2 - frontend should be running
- Check: http://localhost:5173 in browser

### Tests fail
- Make sure backend is running
- Install Playwright: `cd frontend && npx playwright install chromium`
- Run headed mode to see: `npm run test:e2e:headed`

---

## Cloud GPU Setup (Optional)

To use Vast.ai for faster cracking:

### 1. Get API Key
- Sign up at https://vast.ai
- Go to Account → API Keys
- Copy your API key

### 2. Configure
Create `backend/.env`:
```env
VASTAI_API_KEY=your_api_key_here
```

### 3. Use in UI
- Cracking view → GPU Provider → Select "Vast.ai Cloud"
- System will automatically provision GPU, crack, and terminate

---

## File Locations

### Handshakes
- `/tmp/handshake_*.cap`
- `/tmp/wifi-pentester/captures/`

### Wordlists
- `/usr/share/wordlists/rockyou.txt`
- `/usr/share/wordlists/*.txt`

### Reports
- Specify output path when generating
- Default: `/tmp/report.pdf`

---

## ⚠️ LEGAL WARNING

**ONLY** use on networks you own or have **explicit written permission** to test.

Unauthorized network access is **ILLEGAL** and can result in:
- Criminal prosecution
- Heavy fines
- Imprisonment

**USE RESPONSIBLY.**

---

## Quick Command Reference

```bash
# Install
sudo ./scripts/install.sh

# Start backend
./scripts/start-backend.sh

# Start frontend (new terminal)
./scripts/start-frontend.sh

# Run tests (new terminal, backend must be running)
./scripts/run-e2e-tests.sh

# Download wordlists manually
cd backend
source venv/bin/activate
python scripts/download-wordlists.py
```

---

**Repository**: https://github.com/dontcrossconnor/MobileWIFIGHT

**Everything is functional. Start using it now.**
