"""WiFi adapter data models - IMMUTABLE"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


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
    """WiFi adapter information - IMMUTABLE"""
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

    class Config:
        frozen = True


class AdapterConfig(BaseModel):
    """Adapter configuration request - IMMUTABLE"""
    interface: str
    mode: AdapterMode
    channel: Optional[int] = None
    tx_power: Optional[int] = None

    class Config:
        frozen = True
