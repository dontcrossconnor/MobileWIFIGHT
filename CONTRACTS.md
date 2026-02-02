# Immutable Contracts & Interfaces

## ⚠️ CONTRACT IMMUTABILITY NOTICE

**Once this document is committed, these contracts are FROZEN.**
Any implementation must strictly adhere to these interfaces.
No additions, modifications, or removals allowed without explicit user authorization.

---

## Data Models (Pydantic Schemas)

### 1. Network Model

```python
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class EncryptionType(str, Enum):
    """WiFi encryption types"""
    OPEN = "OPEN"
    WEP = "WEP"
    WPA = "WPA"
    WPA2 = "WPA2"
    WPA3 = "WPA3"
    WPA_WPA2 = "WPA/WPA2"
    WPA2_WPA3 = "WPA2/WPA3"

class CipherType(str, Enum):
    """Cipher algorithms"""
    NONE = "NONE"
    WEP = "WEP"
    TKIP = "TKIP"
    CCMP = "CCMP"
    GCMP = "GCMP"

class AuthenticationType(str, Enum):
    """Authentication methods"""
    OPEN = "OPN"
    PSK = "PSK"
    MGT = "MGT"
    SAE = "SAE"

class Network(BaseModel):
    """WiFi Access Point"""
    bssid: str = Field(..., regex=r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
    essid: str = Field(..., min_length=0, max_length=32)
    channel: int = Field(..., ge=1, le=165)
    frequency: int = Field(..., ge=2400, le=5900)
    signal: int = Field(..., ge=-100, le=0)
    encryption: EncryptionType
    cipher: CipherType
    authentication: AuthenticationType
    wps: bool = False
    wps_version: Optional[str] = None
    wps_locked: bool = False
    clients: List['Client'] = []
    handshake_captured: bool = False
    pmkid_captured: bool = False
    beacon_count: int = 0
    data_packets: int = 0
    first_seen: datetime
    last_seen: datetime
    manufacturer: Optional[str] = None

    class Config:
        frozen = True  # Immutable after creation
```

### 2. Client Model

```python
class Client(BaseModel):
    """WiFi client station"""
    mac: str = Field(..., regex=r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
    bssid: str = Field(..., regex=r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
    probes: List[str] = []
    signal: int = Field(..., ge=-100, le=0)
    packets: int = 0
    first_seen: datetime
    last_seen: datetime
    manufacturer: Optional[str] = None

    class Config:
        frozen = True
```

### 3. Attack Models

```python
class AttackType(str, Enum):
    """Available attack types"""
    DEAUTH = "deauth"
    PMKID = "pmkid"
    WPS_PIXIE = "wps_pixie"
    WPS_PIN = "wps_pin"
    HANDSHAKE_CAPTURE = "handshake_capture"
    FAKE_AP = "fake_ap"
    WEP_FRAG = "wep_frag"
    WEP_CHOP = "wep_chop"
    WEP_ARP_REPLAY = "wep_arp_replay"

class AttackStatus(str, Enum):
    """Attack execution status"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class AttackResult(BaseModel):
    """Attack execution result"""
    success: bool
    message: str
    handshake_file: Optional[str] = None
    pmkid_file: Optional[str] = None
    wps_pin: Optional[str] = None
    wep_key: Optional[str] = None
    capture_files: List[str] = []
    packets_sent: int = 0
    duration_seconds: float

class AttackConfig(BaseModel):
    """Attack configuration parameters"""
    target_bssid: str
    target_essid: str
    attack_type: AttackType
    duration_seconds: Optional[int] = 300
    deauth_count: Optional[int] = 0  # 0 = continuous
    channel: Optional[int] = None
    interface: str
    
class Attack(BaseModel):
    """Attack execution instance"""
    id: UUID
    config: AttackConfig
    status: AttackStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[AttackResult] = None
    logs: List[str] = []
    progress_percent: float = 0.0
```

### 4. Cracking Models

```python
class CrackMode(str, Enum):
    """Hashcat attack modes"""
    WORDLIST = "wordlist"
    MASK = "mask"
    HYBRID_WORDLIST_MASK = "hybrid_wm"
    HYBRID_MASK_WORDLIST = "hybrid_mw"
    COMBINATOR = "combinator"

class JobStatus(str, Enum):
    """Cracking job status"""
    QUEUED = "queued"
    PROVISIONING = "provisioning"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    SUCCESS = "success"
    EXHAUSTED = "exhausted"  # No password found
    FAILED = "failed"
    CANCELLED = "cancelled"

class GPUProvider(str, Enum):
    """GPU cloud providers"""
    VASTAI = "vastai"
    LAMBDA = "lambda"
    RUNPOD = "runpod"
    LOCAL = "local"

class CrackingJobConfig(BaseModel):
    """Cracking job configuration"""
    handshake_file: str
    bssid: str
    essid: str
    attack_mode: CrackMode
    wordlist_path: Optional[str] = None
    wordlist_name: Optional[str] = None
    mask: Optional[str] = None
    rules_file: Optional[str] = None
    gpu_provider: GPUProvider = GPUProvider.VASTAI
    max_cost_usd: float = 10.0
    timeout_minutes: int = 120

class GPUInstance(BaseModel):
    """GPU instance information"""
    instance_id: str
    provider: GPUProvider
    gpu_model: str
    gpu_count: int
    cost_per_hour: float
    status: str
    ip_address: Optional[str] = None

class CrackingProgress(BaseModel):
    """Real-time cracking progress"""
    job_id: UUID
    status: JobStatus
    progress_percent: float
    speed_mh_per_sec: float
    tried_passwords: int
    total_passwords: Optional[int] = None
    eta_seconds: Optional[int] = None
    current_wordlist_position: Optional[int] = None

class CrackingJob(BaseModel):
    """Password cracking job"""
    id: UUID
    config: CrackingJobConfig
    status: JobStatus
    gpu_instance: Optional[GPUInstance] = None
    progress: CrackingProgress
    password: Optional[str] = None
    cost_usd: float = 0.0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[str] = []
```

### 5. Adapter Models

```python
class AdapterMode(str, Enum):
    """WiFi adapter operating modes"""
    MANAGED = "managed"
    MONITOR = "monitor"

class AdapterStatus(str, Enum):
    """Adapter availability status"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"

class Adapter(BaseModel):
    """WiFi adapter information"""
    interface: str
    driver: str
    chipset: str
    mac_address: str
    mode: AdapterMode
    status: AdapterStatus
    current_channel: Optional[int] = None
    supported_channels_2ghz: List[int]
    supported_channels_5ghz: List[int]
    monitor_mode_capable: bool
    injection_capable: bool
    tx_power_dbm: int

class AdapterConfig(BaseModel):
    """Adapter configuration request"""
    interface: str
    mode: AdapterMode
    channel: Optional[int] = None
    tx_power: Optional[int] = None
```

### 6. Scan Models

```python
class ScanMode(str, Enum):
    """Scanning modes"""
    PASSIVE = "passive"
    ACTIVE = "active"
    BOTH = "both"

class ScanStatus(str, Enum):
    """Scan session status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class ScanConfig(BaseModel):
    """Scan configuration"""
    interface: str
    mode: ScanMode = ScanMode.PASSIVE
    channels: Optional[List[int]] = None  # None = all channels
    hop_interval_ms: int = 500
    capture_file: Optional[str] = None

class ScanSession(BaseModel):
    """Active scan session"""
    id: UUID
    config: ScanConfig
    status: ScanStatus
    networks_found: int = 0
    clients_found: int = 0
    handshakes_captured: int = 0
    packets_captured: int = 0
    started_at: datetime
    updated_at: datetime
```

### 7. Report Models

```python
class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    MARKDOWN = "md"

class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Finding(BaseModel):
    """Security finding"""
    title: str
    severity: VulnerabilitySeverity
    description: str
    affected_network: str  # BSSID
    evidence: List[str]
    remediation: str
    cvss_score: Optional[float] = None
    references: List[str] = []

class Report(BaseModel):
    """Penetration test report"""
    id: UUID
    title: str
    target_description: str
    tester_name: str
    organization: str
    test_date: datetime
    executive_summary: str
    networks_tested: int
    vulnerabilities_found: int
    findings: List[Finding]
    cracked_networks: List[str]  # BSSIDs
    recommendations: List[str]
    format: ReportFormat
    file_path: Optional[str] = None
    generated_at: datetime
```

---

## Service Interfaces (Abstract Base Classes)

### 1. Adapter Service Interface

```python
from abc import ABC, abstractmethod
from typing import List

class IAdapterService(ABC):
    """WiFi adapter management service"""
    
    @abstractmethod
    async def detect_adapters(self) -> List[Adapter]:
        """Detect all available WiFi adapters"""
        pass
    
    @abstractmethod
    async def get_adapter(self, interface: str) -> Adapter:
        """Get adapter information"""
        pass
    
    @abstractmethod
    async def set_monitor_mode(self, interface: str, enable: bool) -> Adapter:
        """Enable or disable monitor mode"""
        pass
    
    @abstractmethod
    async def set_channel(self, interface: str, channel: int) -> None:
        """Set WiFi channel"""
        pass
    
    @abstractmethod
    async def set_tx_power(self, interface: str, power_dbm: int) -> None:
        """Set transmission power"""
        pass
    
    @abstractmethod
    async def validate_alfa_adapter(self, interface: str) -> bool:
        """Validate Alfa AWUS036ACH adapter"""
        pass
```

### 2. Scanner Service Interface

```python
class IScannerService(ABC):
    """Network scanning service"""
    
    @abstractmethod
    async def start_scan(self, config: ScanConfig) -> ScanSession:
        """Start network scan"""
        pass
    
    @abstractmethod
    async def stop_scan(self, session_id: UUID) -> None:
        """Stop active scan"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: UUID) -> ScanSession:
        """Get scan session details"""
        pass
    
    @abstractmethod
    async def get_networks(self, session_id: UUID) -> List[Network]:
        """Get discovered networks"""
        pass
    
    @abstractmethod
    async def get_network(self, session_id: UUID, bssid: str) -> Network:
        """Get specific network details"""
        pass
    
    @abstractmethod
    async def get_clients(self, session_id: UUID, bssid: Optional[str] = None) -> List[Client]:
        """Get clients (optionally filtered by BSSID)"""
        pass
```

### 3. Attack Service Interface

```python
class IAttackService(ABC):
    """Attack execution service"""
    
    @abstractmethod
    async def create_attack(self, config: AttackConfig) -> Attack:
        """Create and queue attack"""
        pass
    
    @abstractmethod
    async def start_attack(self, attack_id: UUID) -> Attack:
        """Start queued attack"""
        pass
    
    @abstractmethod
    async def stop_attack(self, attack_id: UUID) -> Attack:
        """Stop running attack"""
        pass
    
    @abstractmethod
    async def get_attack(self, attack_id: UUID) -> Attack:
        """Get attack details"""
        pass
    
    @abstractmethod
    async def get_active_attacks(self) -> List[Attack]:
        """Get all active attacks"""
        pass
    
    @abstractmethod
    async def validate_target(self, bssid: str) -> bool:
        """Validate attack target (prevent accidental attacks)"""
        pass
```

### 4. Capture Service Interface

```python
class ICaptureService(ABC):
    """Handshake capture and validation service"""
    
    @abstractmethod
    async def verify_handshake(self, capture_file: str, bssid: str) -> bool:
        """Verify 4-way handshake in capture file"""
        pass
    
    @abstractmethod
    async def extract_pmkid(self, capture_file: str) -> Optional[str]:
        """Extract PMKID from capture"""
        pass
    
    @abstractmethod
    async def convert_capture(self, input_file: str, output_format: str) -> str:
        """Convert capture file format"""
        pass
    
    @abstractmethod
    async def get_capture_info(self, capture_file: str) -> dict:
        """Get capture file metadata"""
        pass
```

### 5. Cracker Service Interface

```python
class ICrackerService(ABC):
    """GPU-accelerated password cracking service"""
    
    @abstractmethod
    async def create_job(self, config: CrackingJobConfig) -> CrackingJob:
        """Create cracking job"""
        pass
    
    @abstractmethod
    async def start_job(self, job_id: UUID) -> CrackingJob:
        """Start cracking job"""
        pass
    
    @abstractmethod
    async def stop_job(self, job_id: UUID) -> CrackingJob:
        """Stop running job"""
        pass
    
    @abstractmethod
    async def get_job(self, job_id: UUID) -> CrackingJob:
        """Get job details"""
        pass
    
    @abstractmethod
    async def get_progress(self, job_id: UUID) -> CrackingProgress:
        """Get real-time progress"""
        pass
    
    @abstractmethod
    async def provision_gpu(self, provider: GPUProvider) -> GPUInstance:
        """Provision GPU instance"""
        pass
    
    @abstractmethod
    async def terminate_gpu(self, instance_id: str) -> None:
        """Terminate GPU instance"""
        pass
```

### 6. Report Service Interface

```python
class IReportService(ABC):
    """Report generation service"""
    
    @abstractmethod
    async def generate_report(
        self,
        networks: List[Network],
        attacks: List[Attack],
        jobs: List[CrackingJob],
        format: ReportFormat
    ) -> Report:
        """Generate penetration test report"""
        pass
    
    @abstractmethod
    async def get_report(self, report_id: UUID) -> Report:
        """Get generated report"""
        pass
    
    @abstractmethod
    async def export_report(self, report_id: UUID, output_path: str) -> str:
        """Export report to file"""
        pass
```

---

## API Contracts (FastAPI Routes)

### Adapter Endpoints

```python
# POST /api/v1/adapter/detect
Request: None
Response: List[Adapter]

# GET /api/v1/adapter/{interface}
Response: Adapter

# POST /api/v1/adapter/{interface}/monitor-mode
Request: {"enable": bool}
Response: Adapter

# POST /api/v1/adapter/{interface}/channel
Request: {"channel": int}
Response: {"success": bool}

# POST /api/v1/adapter/{interface}/tx-power
Request: {"power_dbm": int}
Response: {"success": bool}
```

### Scanner Endpoints

```python
# POST /api/v1/scan
Request: ScanConfig
Response: ScanSession

# DELETE /api/v1/scan/{session_id}
Response: {"success": bool}

# GET /api/v1/scan/{session_id}
Response: ScanSession

# GET /api/v1/scan/{session_id}/networks
Query: ?min_signal=-80&encryption=WPA2
Response: List[Network]

# GET /api/v1/scan/{session_id}/networks/{bssid}
Response: Network

# GET /api/v1/scan/{session_id}/clients
Query: ?bssid=XX:XX:XX:XX:XX:XX
Response: List[Client]
```

### Attack Endpoints

```python
# POST /api/v1/attacks
Request: AttackConfig
Response: Attack

# GET /api/v1/attacks/{attack_id}
Response: Attack

# POST /api/v1/attacks/{attack_id}/start
Response: Attack

# DELETE /api/v1/attacks/{attack_id}
Response: {"success": bool}

# GET /api/v1/attacks/active
Response: List[Attack]
```

### Capture Endpoints

```python
# POST /api/v1/captures/verify
Request: {"file": str, "bssid": str}
Response: {"valid": bool, "quality": int}

# POST /api/v1/captures/extract-pmkid
Request: {"file": str}
Response: {"pmkid": str | null}

# GET /api/v1/captures/{file}/info
Response: {"bssid": str, "essid": str, "packets": int, ...}
```

### Cracking Endpoints

```python
# POST /api/v1/cracking/jobs
Request: CrackingJobConfig
Response: CrackingJob

# GET /api/v1/cracking/jobs/{job_id}
Response: CrackingJob

# POST /api/v1/cracking/jobs/{job_id}/start
Response: CrackingJob

# DELETE /api/v1/cracking/jobs/{job_id}
Response: {"success": bool}

# GET /api/v1/cracking/jobs/{job_id}/progress
Response: CrackingProgress

# GET /api/v1/cracking/jobs/active
Response: List[CrackingJob]
```

### Report Endpoints

```python
# POST /api/v1/reports
Request: {
    "title": str,
    "networks": List[str],  # BSSIDs
    "format": ReportFormat
}
Response: Report

# GET /api/v1/reports/{report_id}
Response: Report

# GET /api/v1/reports/{report_id}/download
Response: File (PDF/HTML/JSON)
```

---

## WebSocket Events (Socket.IO)

### Client → Server Events

```python
# Subscribe to scan updates
{
    "event": "subscribe:scan",
    "data": {"session_id": UUID}
}

# Subscribe to attack updates
{
    "event": "subscribe:attack",
    "data": {"attack_id": UUID}
}

# Subscribe to cracking job updates
{
    "event": "subscribe:crack",
    "data": {"job_id": UUID}
}

# Unsubscribe from updates
{
    "event": "unsubscribe",
    "data": {"subscription_type": str, "id": UUID}
}
```

### Server → Client Events

```python
# Network discovered
{
    "event": "scan:network_discovered",
    "data": Network
}

# Network updated
{
    "event": "scan:network_updated",
    "data": Network
}

# Client discovered
{
    "event": "scan:client_discovered",
    "data": Client
}

# Handshake captured
{
    "event": "scan:handshake_captured",
    "data": {"bssid": str, "file": str}
}

# Attack status changed
{
    "event": "attack:status_changed",
    "data": Attack
}

# Attack log entry
{
    "event": "attack:log",
    "data": {"attack_id": UUID, "message": str, "timestamp": datetime}
}

# Cracking progress update
{
    "event": "crack:progress",
    "data": CrackingProgress
}

# Cracking job completed
{
    "event": "crack:completed",
    "data": CrackingJob
}

# System error
{
    "event": "system:error",
    "data": {"message": str, "severity": str}
}
```

---

## Error Response Contract

All API errors follow this format:

```python
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str              # Error type/code
    message: str            # Human-readable message
    details: Optional[dict] = None  # Additional context
    timestamp: datetime
    request_id: UUID

# HTTP Status Codes:
# 400 - Bad Request (validation errors)
# 401 - Unauthorized
# 403 - Forbidden
# 404 - Not Found
# 409 - Conflict (e.g., adapter already in use)
# 422 - Unprocessable Entity
# 500 - Internal Server Error
# 503 - Service Unavailable (e.g., GPU provider down)
```

---

## Database Schema (PostgreSQL)

```sql
-- Networks table
CREATE TABLE networks (
    bssid VARCHAR(17) PRIMARY KEY,
    essid VARCHAR(32),
    channel INTEGER,
    frequency INTEGER,
    signal INTEGER,
    encryption VARCHAR(20),
    cipher VARCHAR(20),
    authentication VARCHAR(10),
    wps BOOLEAN,
    wps_locked BOOLEAN,
    handshake_captured BOOLEAN,
    pmkid_captured BOOLEAN,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    scan_session_id UUID,
    metadata JSONB
);

-- Clients table
CREATE TABLE clients (
    mac VARCHAR(17) PRIMARY KEY,
    bssid VARCHAR(17),
    signal INTEGER,
    packets INTEGER,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    probes JSONB,
    FOREIGN KEY (bssid) REFERENCES networks(bssid)
);

-- Attacks table
CREATE TABLE attacks (
    id UUID PRIMARY KEY,
    target_bssid VARCHAR(17),
    attack_type VARCHAR(50),
    status VARCHAR(20),
    config JSONB,
    result JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Cracking jobs table
CREATE TABLE cracking_jobs (
    id UUID PRIMARY KEY,
    handshake_file VARCHAR(255),
    bssid VARCHAR(17),
    essid VARCHAR(32),
    config JSONB,
    status VARCHAR(20),
    password VARCHAR(255),
    cost_usd DECIMAL(10, 4),
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    format VARCHAR(10),
    file_path VARCHAR(500),
    generated_at TIMESTAMP,
    metadata JSONB
);

-- Scan sessions table
CREATE TABLE scan_sessions (
    id UUID PRIMARY KEY,
    interface VARCHAR(20),
    status VARCHAR(20),
    config JSONB,
    started_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Configuration Schema

### Backend Config (config.yaml)

```yaml
app:
  name: "WiFi Pentester"
  version: "1.0.0"
  debug: false

server:
  host: "127.0.0.1"
  port: 8000
  workers: 4

database:
  url: "postgresql://user:pass@localhost/wifipentest"
  pool_size: 10

redis:
  url: "redis://localhost:6379/0"

adapter:
  preferred_interface: "wlan0"
  default_channel: 6
  default_tx_power: 20

scanning:
  default_hop_interval_ms: 500
  capture_dir: "/var/wifipentest/captures"

cracking:
  wordlists_dir: "/usr/share/wordlists"
  default_wordlist: "rockyou.txt"
  max_concurrent_jobs: 3
  gpu_providers:
    vastai:
      api_key: "${VASTAI_API_KEY}"
      max_cost_per_hour: 2.0
    lambda:
      api_key: "${LAMBDA_API_KEY}"

logging:
  level: "INFO"
  file: "/var/log/wifipentest/app.log"

security:
  require_target_confirmation: true
  audit_log: true
  session_timeout_minutes: 30
```

---

## TypeScript Types (Frontend)

```typescript
// Must match Python models exactly

export enum EncryptionType {
  OPEN = "OPEN",
  WEP = "WEP",
  WPA = "WPA",
  WPA2 = "WPA2",
  WPA3 = "WPA3",
  WPA_WPA2 = "WPA/WPA2",
  WPA2_WPA3 = "WPA2/WPA3",
}

export interface Network {
  bssid: string;
  essid: string;
  channel: number;
  frequency: number;
  signal: number;
  encryption: EncryptionType;
  cipher: string;
  authentication: string;
  wps: boolean;
  wps_locked: boolean;
  clients: Client[];
  handshake_captured: boolean;
  pmkid_captured: boolean;
  first_seen: string;
  last_seen: string;
}

export interface Client {
  mac: string;
  bssid: string;
  probes: string[];
  signal: number;
  packets: number;
  first_seen: string;
  last_seen: string;
}

export enum AttackType {
  DEAUTH = "deauth",
  PMKID = "pmkid",
  WPS_PIXIE = "wps_pixie",
  WPS_PIN = "wps_pin",
  HANDSHAKE_CAPTURE = "handshake_capture",
  FAKE_AP = "fake_ap",
}

export enum AttackStatus {
  PENDING = "pending",
  RUNNING = "running",
  SUCCESS = "success",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export interface Attack {
  id: string;
  config: AttackConfig;
  status: AttackStatus;
  started_at: string;
  completed_at?: string;
  result?: AttackResult;
  logs: string[];
  progress_percent: number;
}

// ... (all other types matching Python models)
```

---

## Testing Contracts

### Test Coverage Requirements

```python
MINIMUM_COVERAGE = {
    "unit": 0.90,      # 90% coverage
    "integration": 0.80,  # 80% coverage
    "e2e": 0.70,       # 70% coverage
}

CRITICAL_PATHS_COVERAGE = 1.0  # 100% coverage required
```

### Test Naming Convention

```python
# Unit tests
def test_<service>_<method>_<scenario>_<expected_result>():
    pass

# Example:
def test_adapter_service_set_monitor_mode_valid_interface_returns_adapter():
    pass

def test_scanner_service_start_scan_invalid_config_raises_validation_error():
    pass
```

### Mock Interfaces

```python
class MockAdapterService(IAdapterService):
    """Mock implementation for testing"""
    # Must implement all interface methods
    pass

class MockGPUProvider:
    """Mock GPU provider for testing cracking without real cloud costs"""
    pass
```

---

## Contract Validation

All implementations must pass these validation checks:

1. **Type Safety**: All Pydantic models validate correctly
2. **API Schema**: OpenAPI spec matches contracts
3. **Database Schema**: Alembic migrations match models
4. **Frontend Types**: TypeScript types match Python models exactly
5. **Test Coverage**: Meets minimum coverage requirements
6. **Interface Compliance**: All services implement required interfaces

**Validation Command:**
```bash
pytest tests/contracts/ --validate-only
```

---

## Contract Signature

**Version:** 1.0.0  
**Date:** 2026-02-02  
**Status:** IMMUTABLE  

Any deviation from these contracts requires explicit approval and version increment.
