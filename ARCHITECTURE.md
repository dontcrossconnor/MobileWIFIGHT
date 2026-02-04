# Wi-Fi Penetration Testing Platform - Architecture

## Executive Summary

This is a fully-featured Wi-Fi penetration testing platform with a polished GUI that integrates battle-tested open-source tools (aircrack-ng, wifite2, hashcat) with cloud GPU acceleration for rapid password cracking during authorized red team operations.

## Legal Notice

⚠️ **CRITICAL**: This tool is designed EXCLUSIVELY for authorized penetration testing and security auditing. Unauthorized access to networks is illegal. Users must obtain explicit written permission before testing any network they do not own.

## System Architecture

### Architecture Pattern: Layered + Microservices Hybrid

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  (Electron + React + TypeScript)                        │
│  - Quick Actions Dashboard                              │
│  - Guided Workflow Wizard                               │
│  - Real-time Status Monitor                             │
└─────────────────────────────────────────────────────────┘
                          ↕ REST API + WebSocket
┌─────────────────────────────────────────────────────────┐
│                   API Gateway Layer                      │
│  (FastAPI + Python 3.11+)                               │
│  - Request routing                                       │
│  - Authentication & Authorization                        │
│  - Rate limiting                                         │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                  Core Service Layer                      │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Adapter    │  │   Scanner    │  │   Attack     │ │
│  │   Service    │  │   Service    │  │   Service    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Capture    │  │   Cracker    │  │   Report     │ │
│  │   Service    │  │   Service    │  │   Service    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│               Tool Integration Layer                     │
│  - Aircrack-ng wrapper                                  │
│  - Wifite2 wrapper                                      │
│  - Hashcat orchestrator                                 │
│  - NetworkManager controller                            │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                Hardware Abstraction Layer                │
│  - Alfa adapter driver manager                          │
│  - Monitor mode controller                              │
│  - Channel hopping controller                           │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│               External Services Layer                    │
│  - GPU Cloud Service (Vast.ai / Lambda Labs)           │
│  - Wordlist Repository Service                         │
│  - Vulnerability Database                               │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend (Electron + React)

**Technology Stack:**
- Electron 28+ for cross-platform desktop app
- React 18+ with TypeScript
- TailwindCSS + shadcn/ui for polished UI
- Zustand for state management
- React Query for API integration
- WebSocket for real-time updates

**Key Views:**
1. **Dashboard** - System status, adapter info, quick stats
2. **Quick Actions** - One-click common operations
3. **Guided Workflow** - Step-by-step attack wizard
4. **Network Scanner** - Real-time AP discovery
5. **Attack Manager** - Execute and monitor attacks
6. **Capture Viewer** - Handshake analysis
7. **Cracking Dashboard** - GPU cluster status and progress
8. **Reports** - Generated findings and recommendations

### 2. Backend (FastAPI + Python)

**Technology Stack:**
- Python 3.11+
- FastAPI 0.109+ for REST API
- WebSocket for real-time communication
- SQLAlchemy + PostgreSQL for persistence
- Redis for caching and job queues
- Celery for async task processing
- Pydantic for data validation

### 3. Core Services

#### a. Adapter Service
**Purpose:** Manage Alfa WiFi adapter configuration
- Detect and initialize Alfa AWUS036ACH adapter
- Enable/disable monitor mode
- Channel management
- TX power configuration
- Antenna configuration (external dual antenna)

#### b. Scanner Service
**Purpose:** Discover WiFi networks and clients
- Passive scanning (monitor mode)
- Active scanning (probe requests)
- Client station enumeration
- Signal strength tracking
- Hidden SSID detection
- WPS vulnerability detection

#### c. Attack Service
**Purpose:** Execute various WiFi attacks
- **Deauthentication attacks** - Force client disconnection
- **Fake AP attacks** - Evil twin/rogue AP
- **WPS attacks** - Pixie dust, PIN bruteforce
- **PMKID attacks** - Clientless handshake capture
- **Fragmentation attacks** - WEP cracking
- **Cafe Latte attacks** - Client-side WEP
- **Hirte attacks** - Advanced client-side WEP
- **ARP replay attacks** - IV generation for WEP

#### d. Capture Service
**Purpose:** Capture and validate handshakes
- Monitor for 4-way handshakes
- Validate EAPOL frames
- PMKID extraction
- Capture file management (.cap, .pcap)
- Handshake verification

#### e. Cracker Service
**Purpose:** GPU-accelerated password cracking
- Cloud GPU cluster orchestration
- Hashcat integration (WPA/WPA2/WPA3)
- Wordlist management (rockyou, custom lists)
- Rule-based attacks
- Mask attacks
- Hybrid attacks
- Distributed cracking coordination
- Progress tracking and ETA calculation

#### f. Report Service
**Purpose:** Generate professional reports
- Executive summaries
- Technical findings
- Remediation recommendations
- Compliance mapping (PCI-DSS, HIPAA, etc.)
- Export formats (PDF, HTML, JSON)

## Tool Integration

### Primary Tools (All Open Source)

1. **Aircrack-ng Suite** (GPLv2)
   - `airmon-ng` - Monitor mode management
   - `airodump-ng` - Packet capture
   - `aireplay-ng` - Packet injection
   - `aircrack-ng` - WEP/WPA cracking

2. **Wifite2** (GPLv2)
   - Automated wireless auditing
   - Integration layer for consistent workflows

3. **Hashcat** (MIT License)
   - GPU-accelerated cracking
   - Cloud deployment support

4. **Bully** (GPLv3)
   - WPS attacks

5. **Reaver** (GPLv2)
   - WPS PIN attacks

6. **hcxtools** (MIT License)
   - PMKID attacks
   - Modern handshake capture

## Hardware Requirements

### Supported Adapter
**Alfa AWUS036ACH**
- Chipset: Realtek RTL8812AU
- Frequency: Dual-band (2.4GHz + 5GHz)
- Standards: 802.11a/b/g/n/ac
- TX Power: 300mW
- Antenna: 2x external RP-SMA connectors
- Monitor mode: ✅ Supported
- Packet injection: ✅ Supported

### System Requirements
- OS: Linux (Ubuntu 22.04+ / Kali Linux)
- RAM: 8GB minimum, 16GB recommended
- CPU: 4+ cores
- Storage: 50GB+ for captures and wordlists
- Internet: Required for GPU cloud access

## GPU Cloud Integration

### Architecture
```
Local App → API Gateway → Job Queue → Cloud GPU Cluster → Results
```

### Supported Providers
1. **Vast.ai** - On-demand GPU rental
2. **Lambda Labs** - GPU cloud instances
3. **RunPod** - Serverless GPU
4. **Local GPU** - Fallback for CUDA-capable systems

### Cracking Workflow
1. Capture handshake locally
2. Upload to job queue
3. Provision GPU instance(s)
4. Deploy hashcat container
5. Execute attack (wordlist/mask/hybrid)
6. Stream progress via WebSocket
7. Download results on success
8. Terminate instance
9. Display cracked password in UI

### Security
- End-to-end encryption for uploaded captures
- Ephemeral instances (destroyed after job)
- No data retention on cloud provider
- API key management

## Data Models (Immutable Contracts)

### Network
```python
class Network:
    bssid: str              # MAC address
    essid: str              # Network name
    channel: int            # WiFi channel
    frequency: int          # Frequency in MHz
    signal: int             # Signal strength (dBm)
    encryption: str         # WEP/WPA/WPA2/WPA3/Open
    cipher: str             # TKIP/CCMP/etc
    authentication: str     # PSK/MGT/OPN
    wps: bool              # WPS enabled
    wps_locked: bool       # WPS locked
    clients: List[Client]  # Connected clients
    handshake: bool        # Handshake captured
    pmkid: bool           # PMKID captured
    first_seen: datetime
    last_seen: datetime
```

### Client
```python
class Client:
    mac: str               # Client MAC
    bssid: str            # Associated AP
    probes: List[str]     # Probe requests
    signal: int           # Signal strength
    first_seen: datetime
    last_seen: datetime
```

### Attack
```python
class Attack:
    id: UUID
    type: AttackType      # Enum: DEAUTH, WPS, PMKID, etc
    target: Network
    status: AttackStatus  # PENDING/RUNNING/SUCCESS/FAILED
    started_at: datetime
    completed_at: Optional[datetime]
    result: Optional[AttackResult]
    logs: List[str]
```

### CrackingJob
```python
class CrackingJob:
    id: UUID
    handshake_file: str
    bssid: str
    essid: str
    attack_mode: CrackMode  # WORDLIST/MASK/HYBRID
    wordlist: Optional[str]
    mask: Optional[str]
    rules: Optional[str]
    gpu_provider: str
    instance_id: Optional[str]
    status: JobStatus
    progress: float          # 0-100
    eta_seconds: Optional[int]
    password: Optional[str]  # Result
    cost: Decimal           # USD spent
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

## API Contracts (Immutable)

### REST Endpoints

```
POST   /api/v1/adapter/initialize
POST   /api/v1/adapter/monitor-mode
GET    /api/v1/adapter/status

POST   /api/v1/scan/start
POST   /api/v1/scan/stop
GET    /api/v1/scan/networks
GET    /api/v1/scan/networks/{bssid}

POST   /api/v1/attacks
GET    /api/v1/attacks/{id}
DELETE /api/v1/attacks/{id}
POST   /api/v1/attacks/{id}/stop

POST   /api/v1/captures/verify
GET    /api/v1/captures/{id}

POST   /api/v1/cracking/jobs
GET    /api/v1/cracking/jobs/{id}
DELETE /api/v1/cracking/jobs/{id}

GET    /api/v1/reports
POST   /api/v1/reports/generate
```

### WebSocket Events

```
Client → Server:
- subscribe:scan
- subscribe:attack:{id}
- subscribe:crack:{id}

Server → Client:
- scan:network_discovered
- scan:network_updated
- attack:status_changed
- attack:log_entry
- crack:progress_update
- crack:completed
- system:error
```

## UI/UX Flow

### Quick Actions (Dashboard)
- **Scan Networks** → One-click scan → Results table
- **Attack WPA Network** → Select target → Capture handshake → Auto-crack
- **Attack WPS Network** → Select target → Execute Pixie Dust/PIN
- **Capture Only** → Select target → Save handshake → Manual crack later

### Guided Workflow (Wizard)
1. **Setup** - Verify adapter, select interface, set channel
2. **Scan** - Discover networks, filter by encryption/signal
3. **Target Selection** - Choose AP, view details, connected clients
4. **Attack Strategy** - Recommend attack based on target (WPS/PMKID/Deauth)
5. **Execute** - Run attack, display real-time logs
6. **Capture** - Verify handshake quality
7. **Crack** - Configure GPU job, select wordlist/mask
8. **Results** - Display password, generate report

### UI Components

**Dashboard Cards:**
- Adapter Status (connected, mode, channel, TX power)
- Active Scans (networks found, handshakes captured)
- Running Attacks (count, types, targets)
- Cracking Jobs (active, queued, estimated cost)

**Network Table Columns:**
- Signal strength indicator (bars + dBm)
- ESSID with channel badge
- Encryption type (color-coded)
- Client count
- WPS status (icon)
- Handshake status (icon)
- Actions dropdown (Attack, Deauth, Details)

**Attack Panel:**
- Attack type selection with descriptions
- Target information
- Configuration options (duration, packet count, etc.)
- Real-time log output
- Progress indicators
- Stop/Pause controls

**Cracking Dashboard:**
- GPU instance status
- Progress bars per job
- Speed (MH/s)
- ETA countdown
- Cost meter (running total)
- Password reveal on success

## Security Considerations

1. **Authentication** - Local user auth, no remote access
2. **Audit Logging** - All actions logged with timestamps
3. **Target Validation** - Require explicit target confirmation
4. **Rate Limiting** - Prevent accidental DoS
5. **Secure Storage** - Encrypted captures and credentials
6. **Session Management** - Auto-lock on inactivity

## Testing Strategy (TDD)

### Test Pyramid

```
        /\
       /E2E\          10% - End-to-end tests
      /------\
     /Integ.  \       20% - Integration tests
    /----------\
   /   Unit     \     70% - Unit tests
  /--------------\
```

### Test Categories

1. **Unit Tests** (pytest)
   - Service methods
   - Data models
   - Utility functions
   - Mock all external dependencies

2. **Integration Tests** (pytest)
   - API endpoints
   - Database operations
   - Tool wrappers (mocked commands)
   - WebSocket communication

3. **E2E Tests** (Playwright)
   - Complete user workflows
   - UI interactions
   - Real-time updates
   - Error handling

4. **Contract Tests** (Pact)
   - API schema validation
   - Frontend-backend contracts

### Coverage Requirements
- Unit tests: 90%+ coverage
- Integration tests: 80%+ coverage
- Critical paths: 100% coverage

## Development Workflow

### Phase 1: Foundation (Immutable Contracts)
- Define all data models
- Define all API contracts
- Define all service interfaces
- Write comprehensive test framework
- **No changes allowed after this phase**

### Phase 2: Implementation
- Implement services following contracts
- Write tests first (TDD)
- All tests must pass before moving forward
- No deviation from architecture

### Phase 3: Integration
- Connect all services
- Implement API gateway
- Tool wrappers
- GPU cloud integration

### Phase 4: Frontend
- Build UI components
- Implement workflows
- Real-time features
- Polish and UX

### Phase 5: Validation
- Full E2E testing
- Security audit
- Performance testing
- Documentation

## Technology Decisions

### Why Python for Backend?
- Aircrack-ng suite has excellent Python bindings
- Rich ecosystem for system/network programming
- Easy subprocess management for external tools
- Rapid development with FastAPI

### Why Electron for Frontend?
- Cross-platform desktop app
- Native system access
- Hardware control (adapter management)
- No browser security restrictions

### Why PostgreSQL?
- Robust data persistence
- Complex queries for reporting
- JSONB for flexible capture metadata

### Why Redis?
- Fast caching for scan results
- Job queue for async tasks
- Real-time pub/sub for WebSocket

## File Structure

```
wifi-pentester/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core config
│   │   ├── models/        # Data models (IMMUTABLE)
│   │   ├── schemas/       # Pydantic schemas (IMMUTABLE)
│   │   ├── services/      # Business logic
│   │   ├── tools/         # Tool wrappers
│   │   └── tests/         # Test suites
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── views/         # Main views
│   │   ├── hooks/         # Custom hooks
│   │   ├── store/         # Zustand stores
│   │   ├── api/           # API client
│   │   └── types/         # TypeScript types (IMMUTABLE)
│   ├── package.json
│   └── tsconfig.json
├── gpu-worker/            # Hashcat worker for cloud
│   ├── Dockerfile
│   └── worker.py
├── docs/
│   ├── ARCHITECTURE.md    # This file
│   ├── API.md            # API documentation
│   ├── DEPLOYMENT.md     # Deployment guide
│   └── USER_GUIDE.md     # User manual
├── scripts/
│   ├── setup.sh          # Environment setup
│   └── install-deps.sh   # Install system deps
└── docker-compose.yml    # Local dev environment
```

## Performance Targets

- **Scan startup:** < 2 seconds
- **Network discovery:** Real-time updates (< 100ms latency)
- **Handshake capture:** < 60 seconds (target dependent)
- **GPU provisioning:** < 120 seconds
- **UI responsiveness:** < 100ms for all interactions
- **Cracking speed:** > 1000 MH/s (GPU dependent)

## Future Enhancements (Post-MVP)

- Bluetooth attack support
- Rogue AP detection
- MITM attack automation
- Evil portal captive portal
- Mobile app (Android)
- Multi-adapter support
- Distributed scanning (multiple machines)
- ML-based password prediction
- Integration with Metasploit
- Cloud-based collaboration

## Compliance & Ethics

This tool is designed for:
✅ Authorized penetration testing
✅ Security research (with permission)
✅ Red team operations (authorized)
✅ Educational purposes (controlled environments)

❌ Unauthorized network access
❌ Illegal surveillance
❌ Malicious attacks

Users are solely responsible for compliance with local laws and regulations.
