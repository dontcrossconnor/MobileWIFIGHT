"""Attack data models - IMMUTABLE"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


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
    """Attack execution result - IMMUTABLE"""
    success: bool
    message: str
    handshake_file: Optional[str] = None
    pmkid_file: Optional[str] = None
    wps_pin: Optional[str] = None
    wep_key: Optional[str] = None
    capture_files: List[str] = []
    packets_sent: int = 0
    duration_seconds: float

    class Config:
        frozen = True


class AttackConfig(BaseModel):
    """Attack configuration parameters - IMMUTABLE"""
    target_bssid: str
    target_essid: str
    attack_type: AttackType
    duration_seconds: Optional[int] = 300
    deauth_count: Optional[int] = 0  # 0 = continuous
    channel: Optional[int] = None
    interface: str

    class Config:
        frozen = True


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
