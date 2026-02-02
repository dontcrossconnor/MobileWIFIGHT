# Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the WiFi Penetration Testing Platform following TDD principles with immutable contracts.

## Development Principles

### 1. Test-Driven Development (TDD)

**Process**: Red → Green → Refactor

1. **Red**: Write/run test → Watch it fail
2. **Green**: Write minimum code to pass
3. **Refactor**: Improve code while tests pass

### 2. Contract Immutability

**FROZEN FILES** (No modifications without approval):
- `backend/app/models/*.py`
- `backend/app/services/interfaces.py`
- `frontend/src/types/models.ts`
- `CONTRACTS.md`

### 3. Coverage Requirements

- Unit tests: 90%+
- Integration tests: 80%+
- Critical paths: 100%

## Implementation Order

### Phase 1: Tool Wrappers (Week 1-2)

Create wrapper classes for external tools in `backend/app/tools/`:

#### 1.1 Aircrack-ng Wrapper

```python
# File: backend/app/tools/aircrack.py

class AircrackNG:
    """Wrapper for aircrack-ng suite"""
    
    async def start_monitor_mode(self, interface: str) -> str:
        """Enable monitor mode using airmon-ng"""
        # Run: airmon-ng start wlan0
        pass
    
    async def stop_monitor_mode(self, interface: str) -> str:
        """Disable monitor mode"""
        # Run: airmon-ng stop wlan0mon
        pass
    
    async def start_dump(self, interface: str, output: str, channel: Optional[int] = None):
        """Start airodump-ng capture"""
        # Run: airodump-ng wlan0mon -w output --channel 6
        pass
    
    async def deauth(self, interface: str, bssid: str, client: Optional[str] = None, count: int = 0):
        """Send deauth packets"""
        # Run: aireplay-ng --deauth 0 -a BSSID wlan0mon
        pass
    
    async def verify_handshake(self, capture_file: str, bssid: str) -> bool:
        """Verify handshake in capture file"""
        # Run: aircrack-ng capture.cap -b BSSID
        pass
```

**Tests**: Use mocks to avoid running actual commands during unit tests

#### 1.2 hcxtools Wrapper

```python
# File: backend/app/tools/hcxtools.py

class HCXTools:
    """Wrapper for hcxtools"""
    
    async def extract_pmkid(self, capture_file: str) -> Optional[str]:
        """Extract PMKID from capture"""
        # Run: hcxpcapngtool -o pmkid.22000 capture.pcapng
        pass
    
    async def convert_to_22000(self, capture_file: str, output: str) -> str:
        """Convert to hashcat 22000 format"""
        pass
```

#### 1.3 Hashcat Wrapper

```python
# File: backend/app/tools/hashcat.py

class Hashcat:
    """Wrapper for hashcat"""
    
    async def crack_wpa(
        self,
        hash_file: str,
        wordlist: str,
        rules: Optional[str] = None,
        mask: Optional[str] = None,
    ) -> Optional[str]:
        """Crack WPA/WPA2 password"""
        # Run: hashcat -m 22000 hash.22000 wordlist.txt
        pass
    
    async def get_status(self, session_name: str) -> dict:
        """Get cracking session status"""
        # Parse hashcat status output
        pass
```

#### 1.4 Network Manager Wrapper

```python
# File: backend/app/tools/network.py

class NetworkManager:
    """Wrapper for network utilities"""
    
    async def get_interfaces(self) -> List[dict]:
        """Get all network interfaces"""
        # Parse: iw dev, iwconfig, ip link
        pass
    
    async def set_channel(self, interface: str, channel: int):
        """Set WiFi channel"""
        # Run: iw dev wlan0mon set channel 6
        pass
    
    async def set_tx_power(self, interface: str, power_dbm: int):
        """Set transmission power"""
        # Run: iw dev wlan0mon set txpower fixed 2000
        pass
    
    async def get_chipset(self, interface: str) -> str:
        """Get adapter chipset"""
        # Parse: lsusb, dmesg, etc.
        pass
```

### Phase 2: Core Services (Week 3-5)

Implement services following interface contracts.

#### 2.1 Adapter Service

```python
# File: backend/app/services/adapter.py

from app.services.interfaces import IAdapterService
from app.tools.aircrack import AircrackNG
from app.tools.network import NetworkManager

class AdapterService(IAdapterService):
    """WiFi adapter management service"""
    
    def __init__(self):
        self.aircrack = AircrackNG()
        self.network = NetworkManager()
    
    async def detect_adapters(self) -> List[Adapter]:
        """Detect all available WiFi adapters"""
        interfaces = await self.network.get_interfaces()
        adapters = []
        for iface in interfaces:
            # Build Adapter model from interface info
            pass
        return adapters
    
    # Implement all interface methods...
```

**TDD Steps**:
1. Run: `pytest app/tests/test_adapter_service.py` (all fail)
2. Implement one method
3. Run tests again (some pass)
4. Repeat until all pass

#### 2.2 Scanner Service

```python
# File: backend/app/services/scanner.py

from app.services.interfaces import IScannerService
from app.tools.aircrack import AircrackNG

class ScannerService(IScannerService):
    """Network scanning service"""
    
    def __init__(self):
        self.aircrack = AircrackNG()
        self.active_sessions: Dict[UUID, ScanSession] = {}
        self.discovered_networks: Dict[UUID, List[Network]] = {}
    
    async def start_scan(self, config: ScanConfig) -> ScanSession:
        """Start network scan"""
        # 1. Create session
        # 2. Start airodump-ng
        # 3. Parse output in background
        # 4. Update discovered networks
        pass
    
    # Implement all interface methods...
```

#### 2.3 Attack Service

```python
# File: backend/app/services/attack.py

from app.services.interfaces import IAttackService
from app.tools.aircrack import AircrackNG

class AttackService(IAttackService):
    """Attack execution service"""
    
    def __init__(self):
        self.aircrack = AircrackNG()
        self.attacks: Dict[UUID, Attack] = {}
    
    async def create_attack(self, config: AttackConfig) -> Attack:
        """Create and queue attack"""
        # 1. Validate target
        # 2. Create Attack model
        # 3. Queue for execution
        pass
    
    async def start_attack(self, attack_id: UUID) -> Attack:
        """Start queued attack"""
        attack = self.attacks[attack_id]
        
        if attack.config.attack_type == AttackType.DEAUTH:
            # Execute deauth attack
            pass
        elif attack.config.attack_type == AttackType.WPS_PIXIE:
            # Execute WPS pixie dust
            pass
        # ... handle other attack types
        
        return attack
    
    # Implement all interface methods...
```

#### 2.4 Capture Service

```python
# File: backend/app/services/capture.py

from app.services.interfaces import ICaptureService
from app.tools.aircrack import AircrackNG
from app.tools.hcxtools import HCXTools

class CaptureService(ICaptureService):
    """Handshake capture and validation service"""
    
    def __init__(self):
        self.aircrack = AircrackNG()
        self.hcxtools = HCXTools()
    
    async def verify_handshake(self, capture_file: str, bssid: str) -> bool:
        """Verify 4-way handshake in capture file"""
        return await self.aircrack.verify_handshake(capture_file, bssid)
    
    async def extract_pmkid(self, capture_file: str) -> Optional[str]:
        """Extract PMKID from capture"""
        return await self.hcxtools.extract_pmkid(capture_file)
    
    # Implement all interface methods...
```

#### 2.5 Cracker Service

```python
# File: backend/app/services/cracker.py

from app.services.interfaces import ICrackerService
from app.tools.hashcat import Hashcat
from app.tools.gpu_cloud import GPUCloudProvider

class CrackerService(ICrackerService):
    """GPU-accelerated password cracking service"""
    
    def __init__(self):
        self.hashcat = Hashcat()
        self.gpu_providers = {
            GPUProvider.VASTAI: VastAIProvider(),
            GPUProvider.LAMBDA: LambdaProvider(),
            # ...
        }
        self.jobs: Dict[UUID, CrackingJob] = {}
    
    async def create_job(self, config: CrackingJobConfig) -> CrackingJob:
        """Create cracking job"""
        # 1. Validate handshake file
        # 2. Create job
        # 3. Queue for execution
        pass
    
    async def start_job(self, job_id: UUID) -> CrackingJob:
        """Start cracking job"""
        job = self.jobs[job_id]
        
        # 1. Provision GPU
        gpu = await self.provision_gpu(job.config.gpu_provider)
        
        # 2. Upload files to GPU
        # 3. Start hashcat
        # 4. Monitor progress
        
        return job
    
    # Implement all interface methods...
```

#### 2.6 Report Service

```python
# File: backend/app/services/report.py

from app.services.interfaces import IReportService
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

class ReportService(IReportService):
    """Report generation service"""
    
    async def generate_report(
        self,
        networks: List[Network],
        attacks: List[Attack],
        jobs: List[CrackingJob],
        format: ReportFormat,
    ) -> Report:
        """Generate penetration test report"""
        # 1. Analyze results
        findings = self._analyze_findings(networks, attacks, jobs)
        
        # 2. Generate report based on format
        if format == ReportFormat.PDF:
            return await self._generate_pdf(findings)
        elif format == ReportFormat.HTML:
            return await self._generate_html(findings)
        # ...
    
    # Implement all interface methods...
```

### Phase 3: API Layer (Week 6-7)

Create FastAPI routes in `backend/app/api/`:

#### 3.1 API Structure

```
backend/app/api/
├── __init__.py
├── deps.py              # Dependency injection
├── v1/
│   ├── __init__.py
│   ├── adapter.py       # Adapter endpoints
│   ├── scanner.py       # Scanner endpoints
│   ├── attacks.py       # Attack endpoints
│   ├── cracking.py      # Cracking endpoints
│   ├── captures.py      # Capture endpoints
│   └── reports.py       # Report endpoints
```

#### 3.2 Example: Adapter API

```python
# File: backend/app/api/v1/adapter.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.interfaces import IAdapterService
from app.api.deps import get_adapter_service

router = APIRouter(prefix="/adapter", tags=["adapter"])

@router.post("/detect", response_model=List[Adapter])
async def detect_adapters(
    service: IAdapterService = Depends(get_adapter_service)
):
    """Detect all available WiFi adapters"""
    return await service.detect_adapters()

@router.get("/{interface}", response_model=Adapter)
async def get_adapter(
    interface: str,
    service: IAdapterService = Depends(get_adapter_service)
):
    """Get adapter information"""
    try:
        return await service.get_adapter(interface)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{interface}/monitor-mode", response_model=Adapter)
async def set_monitor_mode(
    interface: str,
    enable: bool,
    service: IAdapterService = Depends(get_adapter_service)
):
    """Enable or disable monitor mode"""
    return await service.set_monitor_mode(interface, enable)

# ... other endpoints
```

#### 3.3 WebSocket Handler

```python
# File: backend/app/api/websocket.py

import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.on('connect')
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.on('subscribe:scan')
async def subscribe_scan(sid, data):
    """Subscribe to scan updates"""
    session_id = data['session_id']
    await sio.enter_room(sid, f"scan:{session_id}")

@sio.on('subscribe:attack')
async def subscribe_attack(sid, data):
    """Subscribe to attack updates"""
    attack_id = data['attack_id']
    await sio.enter_room(sid, f"attack:{attack_id}")

# Emit events from services:
# await sio.emit('scan:network_discovered', network.dict(), room=f"scan:{session_id}")
```

### Phase 4: Frontend Implementation (Week 8-10)

Implement React components and views.

#### 4.1 API Client

```typescript
// File: frontend/src/api/client.ts

import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
});

export const adapterAPI = {
  detect: () => api.get<Adapter[]>('/adapter/detect'),
  get: (iface: string) => api.get<Adapter>(`/adapter/${iface}`),
  setMonitorMode: (iface: string, enable: boolean) => 
    api.post<Adapter>(`/adapter/${iface}/monitor-mode`, { enable }),
};

export const scannerAPI = {
  start: (config: ScanConfig) => api.post<ScanSession>('/scan', config),
  stop: (sessionId: string) => api.delete(`/scan/${sessionId}`),
  getNetworks: (sessionId: string) => api.get<Network[]>(`/scan/${sessionId}/networks`),
};

// ... other APIs
```

#### 4.2 WebSocket Hook

```typescript
// File: frontend/src/hooks/useWebSocket.ts

import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

export const useWebSocket = () => {
  const [socket] = useState(() => io('http://localhost:8000'));
  
  useEffect(() => {
    return () => socket.disconnect();
  }, []);
  
  return socket;
};

// Usage:
const socket = useWebSocket();
socket.emit('subscribe:scan', { session_id });
socket.on('scan:network_discovered', (network) => {
  // Update UI
});
```

#### 4.3 State Management (Zustand)

```typescript
// File: frontend/src/store/adapterStore.ts

import create from 'zustand';
import { Adapter } from '@/types/models';

interface AdapterStore {
  adapters: Adapter[];
  selectedAdapter: Adapter | null;
  setAdapters: (adapters: Adapter[]) => void;
  selectAdapter: (adapter: Adapter) => void;
}

export const useAdapterStore = create<AdapterStore>((set) => ({
  adapters: [],
  selectedAdapter: null,
  setAdapters: (adapters) => set({ adapters }),
  selectAdapter: (adapter) => set({ selectedAdapter: adapter }),
}));
```

#### 4.4 Example Component

```typescript
// File: frontend/src/components/NetworkScanner.tsx

import { useQuery } from '@tanstack/react-query';
import { useWebSocket } from '@/hooks/useWebSocket';
import { scannerAPI } from '@/api/client';

export const NetworkScanner = () => {
  const socket = useWebSocket();
  const [networks, setNetworks] = useState<Network[]>([]);
  
  const { data: session } = useQuery({
    queryKey: ['scan-session'],
    queryFn: () => scannerAPI.start({ interface: 'wlan0mon', mode: 'passive' }),
  });
  
  useEffect(() => {
    if (session) {
      socket.emit('subscribe:scan', { session_id: session.id });
      socket.on('scan:network_discovered', (network: Network) => {
        setNetworks(prev => [...prev, network]);
      });
    }
  }, [session]);
  
  return (
    <div>
      <h2>Discovered Networks: {networks.length}</h2>
      <table>
        {networks.map(network => (
          <tr key={network.bssid}>
            <td>{network.essid}</td>
            <td>{network.signal} dBm</td>
            <td>{network.encryption}</td>
          </tr>
        ))}
      </table>
    </div>
  );
};
```

### Phase 5: Integration & Testing (Week 11-12)

1. **End-to-End Testing**
   - Use Playwright for E2E tests
   - Test complete user workflows
   
2. **Integration Testing**
   - Enable integration test markers
   - Test with real hardware
   
3. **Performance Testing**
   - Load testing with concurrent operations
   - Memory leak detection
   
4. **Security Audit**
   - Input validation
   - Command injection prevention
   - Rate limiting

## Daily Development Workflow

### Morning Checklist

1. Pull latest changes
2. Run tests: `pytest`
3. Check coverage: `pytest --cov=app`
4. Review failing tests

### Development Cycle

1. Pick a test file: `test_adapter_service.py`
2. Run tests: `pytest app/tests/test_adapter_service.py -v`
3. Implement code to pass one test
4. Run tests again
5. Refactor if needed
6. Commit: `git commit -m "feat: implement adapter detection"`
7. Repeat

### End of Day Checklist

1. All tests passing for today's work
2. Coverage maintained/improved
3. Code formatted: `black .`
4. Linting passed: `ruff .`
5. Type checking passed: `mypy .`
6. Commit and push

## Common Patterns

### Error Handling

```python
from fastapi import HTTPException

try:
    result = await service.method()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Async Background Tasks

```python
from celery import Celery

celery = Celery('wifi-pentester', broker='redis://localhost')

@celery.task
def run_attack(attack_id: UUID):
    """Execute attack in background"""
    # Implementation
    pass

# Start task:
run_attack.delay(attack_id)
```

### WebSocket Updates

```python
# In service method:
await sio.emit('scan:network_discovered', network.dict(), room=f"scan:{session_id}")
```

## Debugging Tips

### 1. Test Failures

```bash
# Verbose output
pytest -vv

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Debug with pdb
pytest --pdb
```

### 2. Integration Issues

```bash
# Check if tools are installed
which aircrack-ng
which hashcat

# Check adapter
iw dev
iwconfig

# Check permissions
groups $USER  # Should include: root or admin
```

### 3. Frontend Issues

```bash
# Check API connectivity
curl http://localhost:8000/api/v1/adapter/detect

# WebSocket test
wscat -c ws://localhost:8000
```

## Deployment

### Docker Compose (Development)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    privileged: true  # Required for WiFi adapter access
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: wifipentest
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    
  redis:
    image: redis:7
    
  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
    ports:
      - "5173:5173"
```

### Production Considerations

- Use separate database server
- Enable HTTPS
- Implement rate limiting
- Add authentication
- Set up monitoring (Prometheus, Grafana)
- Log aggregation (ELK stack)

## Next Steps

1. ✅ Architecture complete
2. ✅ Contracts defined
3. ✅ Tests written
4. ⏳ Awaiting implementation start signal
5. ⏳ Implement tool wrappers
6. ⏳ Implement core services
7. ⏳ Build API layer
8. ⏳ Create frontend UI

---

**Ready to begin implementation when you give the signal!**
