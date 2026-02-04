"""Scanning data models - IMMUTABLE"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


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
    """Scan configuration - IMMUTABLE"""
    interface: str
    mode: ScanMode = ScanMode.PASSIVE
    channels: Optional[List[int]] = None  # None = all channels
    hop_interval_ms: int = 500
    capture_file: Optional[str] = None

    class Config:
        frozen = True


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
