"""Service interfaces - IMMUTABLE CONTRACTS"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.models import (
    Adapter,
    AdapterConfig,
    Network,
    Client,
    ScanConfig,
    ScanSession,
    Attack,
    AttackConfig,
    CrackingJob,
    CrackingJobConfig,
    CrackingProgress,
    GPUProvider,
    GPUInstance,
    Report,
    ReportFormat,
)


class IAdapterService(ABC):
    """WiFi adapter management service interface - IMMUTABLE"""

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


class IScannerService(ABC):
    """Network scanning service interface - IMMUTABLE"""

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
    async def get_clients(
        self, session_id: UUID, bssid: Optional[str] = None
    ) -> List[Client]:
        """Get clients (optionally filtered by BSSID)"""
        pass


class IAttackService(ABC):
    """Attack execution service interface - IMMUTABLE"""

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


class ICaptureService(ABC):
    """Handshake capture and validation service interface - IMMUTABLE"""

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


class ICrackerService(ABC):
    """GPU-accelerated password cracking service interface - IMMUTABLE"""

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


class IReportService(ABC):
    """Report generation service interface - IMMUTABLE"""

    @abstractmethod
    async def generate_report(
        self,
        networks: List[Network],
        attacks: List[Attack],
        jobs: List[CrackingJob],
        format: ReportFormat,
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
