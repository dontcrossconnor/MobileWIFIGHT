"""Data models package - IMMUTABLE CONTRACTS"""
from .network import Network, Client, EncryptionType, CipherType, AuthenticationType
from .attack import Attack, AttackType, AttackStatus, AttackConfig, AttackResult
from .cracking import CrackingJob, CrackingJobConfig, CrackingProgress, CrackMode, JobStatus, GPUProvider, GPUInstance
from .adapter import Adapter, AdapterMode, AdapterStatus, AdapterConfig
from .scan import ScanSession, ScanConfig, ScanMode, ScanStatus
from .report import Report, Finding, ReportFormat, VulnerabilitySeverity

__all__ = [
    # Network models
    "Network",
    "Client",
    "EncryptionType",
    "CipherType",
    "AuthenticationType",
    # Attack models
    "Attack",
    "AttackType",
    "AttackStatus",
    "AttackConfig",
    "AttackResult",
    # Cracking models
    "CrackingJob",
    "CrackingJobConfig",
    "CrackingProgress",
    "CrackMode",
    "JobStatus",
    "GPUProvider",
    "GPUInstance",
    # Adapter models
    "Adapter",
    "AdapterMode",
    "AdapterStatus",
    "AdapterConfig",
    # Scan models
    "ScanSession",
    "ScanConfig",
    "ScanMode",
    "ScanStatus",
    # Report models
    "Report",
    "Finding",
    "ReportFormat",
    "VulnerabilitySeverity",
]
