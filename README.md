# WiFi Penetration Testing Platform

A fully-featured, professional-grade WiFi penetration testing platform with GPU-accelerated password cracking, polished GUI, and guided workflows for authorized security assessments.

## ⚠️ Legal Notice

**CRITICAL WARNING**: This tool is designed EXCLUSIVELY for:
- ✅ Authorized penetration testing with explicit written permission
- ✅ Security research in controlled environments
- ✅ Red team operations within scope
- ✅ Educational purposes with proper authorization

**ILLEGAL USES**:
- ❌ Unauthorized network access
- ❌ Malicious attacks
- ❌ Surveillance without consent
- ❌ Any use without explicit permission

**Users are solely responsible for ensuring compliance with all applicable laws and regulations. Unauthorized use is illegal and may result in criminal prosecution.**

## Architecture

This project follows a TDD (Test-Driven Development) approach with **immutable contracts**. See `ARCHITECTURE.md` and `CONTRACTS.md` for complete specifications.

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (REST API)
- PostgreSQL (persistence)
- Redis (caching & job queue)
- Celery (async tasks)
- WebSocket (real-time updates)

**Frontend:**
- Electron 28+ (desktop app)
- React 18+ with TypeScript
- TailwindCSS + shadcn/ui
- Zustand (state management)
- React Query (API integration)

**Integrations:**
- Aircrack-ng suite
- Wifite2
- Hashcat (GPU-accelerated)
- hcxtools
- Bully/Reaver (WPS attacks)

**Hardware:**
- Alfa AWUS036ACH WiFi adapter
- Realtek RTL8812AU chipset
- Dual external antennas
- Monitor mode & packet injection support

## Project Structure

```
wifi-pentester/
├── ARCHITECTURE.md           # Complete system architecture
├── CONTRACTS.md             # Immutable interface contracts
├── backend/                 # Python backend
│   ├── app/
│   │   ├── api/            # REST API routes
│   │   ├── models/         # Data models (IMMUTABLE)
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic services
│   │   │   └── interfaces.py  # Service contracts (IMMUTABLE)
│   │   ├── tools/          # Tool wrappers (aircrack-ng, etc)
│   │   └── tests/          # Test suites
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/               # Electron + React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── views/         # Main application views
│   │   ├── types/         # TypeScript types (IMMUTABLE)
│   │   └── api/           # API client
│   └── package.json
├── gpu-worker/            # Hashcat worker for cloud GPU
└── docs/                  # Documentation
```

## Features

### Core Capabilities

1. **Adapter Management**
   - Detect and configure WiFi adapters
   - Enable/disable monitor mode
   - Channel configuration
   - TX power management

2. **Network Scanning**
   - Passive/active scanning
   - Real-time network discovery
   - Client enumeration
   - Automatic handshake capture
   - PMKID detection
   - WPS vulnerability detection

3. **Attack Execution**
   - Deauthentication attacks
   - WPA/WPA2 handshake capture
   - PMKID attacks (clientless)
   - WPS Pixie Dust
   - WPS PIN bruteforce
   - WEP attacks (fragmentation, ARP replay)
   - Fake AP / Evil Twin

4. **GPU-Accelerated Cracking**
   - Cloud GPU provisioning (Vast.ai, Lambda Labs, RunPod)
   - Hashcat integration
   - Wordlist attacks
   - Mask attacks
   - Hybrid attacks
   - Rule-based attacks
   - Real-time progress tracking
   - Cost monitoring

5. **Professional Reporting**
   - Executive summaries
   - Technical findings
   - Remediation recommendations
   - CVSS scoring
   - Multiple formats (PDF, HTML, JSON, Markdown)

### UI Features

- **Dashboard** - System overview, adapter status, statistics
- **Quick Actions** - One-click common operations
- **Guided Workflow** - Step-by-step attack wizard
- **Network Scanner** - Live network discovery table
- **Attack Manager** - Execute and monitor attacks
- **Cracking Dashboard** - GPU status and progress
- **Reports** - Generate professional pentest reports

## Development Setup

### Prerequisites

- Linux (Ubuntu 22.04+ or Kali Linux)
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Alfa AWUS036ACH WiFi adapter

### Installation

```bash
# Clone repository
git clone https://github.com/dontcrossconnor/MobileWIFIGHT.git
cd MobileWIFIGHT

# Backend setup
cd backend
pip install -r requirements.txt
# or with poetry:
poetry install

# Frontend setup
cd ../frontend
npm install

# System dependencies
sudo apt-get install -y \
    aircrack-ng \
    hcxtools \
    hashcat \
    reaver \
    bully \
    wireless-tools \
    net-tools
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Run only unit tests (skip integration tests)
pytest -m "not integration"

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test

# With coverage
npm run test:coverage
```

### Development Workflow

This project follows **strict TDD** with **immutable contracts**:

1. **Phase 1: Contracts (COMPLETE)** ✅
   - All data models defined in `backend/app/models/`
   - All service interfaces defined in `backend/app/services/interfaces.py`
   - All TypeScript types defined in `frontend/src/types/models.ts`
   - **NO MODIFICATIONS ALLOWED WITHOUT EXPLICIT APPROVAL**

2. **Phase 2: Tests (COMPLETE)** ✅
   - Comprehensive test suites in `backend/app/tests/`
   - Tests define expected behavior
   - All tests currently fail (no implementation)
   - Coverage requirements: 90% unit, 80% integration

3. **Phase 3: Implementation (NEXT)**
   - Implement services to pass tests
   - Follow TDD: Red → Green → Refactor
   - No deviation from contracts
   - All tests must pass before moving forward

4. **Phase 4: Integration**
   - Connect all services
   - API gateway implementation
   - Tool wrapper implementation
   - WebSocket real-time updates

5. **Phase 5: Frontend**
   - React components
   - UI/UX implementation
   - Real-time features
   - Polish and responsive design

## Contract Immutability

⚠️ **The following are FROZEN and cannot be modified:**

- `backend/app/models/*.py` - Data models
- `backend/app/services/interfaces.py` - Service interfaces
- `frontend/src/types/models.ts` - TypeScript types
- `CONTRACTS.md` - Interface specifications

Any changes require:
1. Explicit user approval
2. Version increment
3. Migration plan
4. All tests updated

## Testing Strategy

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

### Coverage Requirements

- Unit tests: 90%+
- Integration tests: 80%+
- Critical paths: 100%

### Running Specific Test Suites

```bash
# Model contract tests
pytest app/tests/test_models.py

# Service tests
pytest app/tests/test_adapter_service.py
pytest app/tests/test_scanner_service.py
pytest app/tests/test_attack_service.py
pytest app/tests/test_cracker_service.py
pytest app/tests/test_capture_service.py
pytest app/tests/test_report_service.py

# Integration tests only
pytest -m integration

# Skip integration tests
pytest -m "not integration"
```

## API Documentation

Once the backend is running, API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Configuration

See `backend/app/core/config.py` (to be implemented) for configuration options.

Key environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `VASTAI_API_KEY` - Vast.ai API key for GPU provisioning
- `LAMBDA_API_KEY` - Lambda Labs API key
- `RUNPOD_API_KEY` - RunPod API key

## Contributing

This project follows TDD with immutable contracts. Contributions must:

1. Not modify frozen contracts without approval
2. Include tests for all new functionality
3. Maintain minimum coverage thresholds
4. Pass all linting and type checking
5. Follow existing code style

## Current Status

**Phase**: Planning & Testing Framework Complete ✅

**Completed**:
- ✅ Architecture design
- ✅ Contract definitions (data models, interfaces)
- ✅ Comprehensive test framework
- ✅ Project structure
- ✅ Configuration files

**Next Steps**:
- ⏳ Awaiting user direction for implementation phase
- ⏳ Service implementations (TDD approach)
- ⏳ API gateway
- ⏳ Tool wrappers
- ⏳ Frontend implementation

## Test Execution Status

```bash
# Current test status (all tests written, none passing yet)
$ pytest
=============== TESTS WRITTEN, AWAITING IMPLEMENTATION ===============

Total tests: ~150+
- Model contract tests: 20+
- Adapter service tests: 15+
- Scanner service tests: 15+
- Attack service tests: 20+
- Cracker service tests: 25+
- Capture service tests: 10+
- Report service tests: 15+

Status: All tests fail (no implementation exists yet)
This is expected and correct for TDD approach.
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is provided "as is" for authorized security testing only. The authors and contributors are not responsible for any misuse or damage caused by this software. Users must comply with all applicable laws and obtain proper authorization before testing any networks.

## Repository

**GitHub**: https://github.com/dontcrossconnor/MobileWIFIGHT

**Issues**: https://github.com/dontcrossconnor/MobileWIFIGHT/issues

**Pull Requests**: https://github.com/dontcrossconnor/MobileWIFIGHT/pulls

---

**Built with TDD principles and immutable contracts for maximum reliability and maintainability.**
