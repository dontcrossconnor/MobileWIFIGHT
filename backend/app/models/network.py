"""Network and Client data models - IMMUTABLE"""
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


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


class Client(BaseModel):
    """WiFi client station - IMMUTABLE"""
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


class Network(BaseModel):
    """WiFi Access Point - IMMUTABLE"""
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
    clients: List[Client] = []
    handshake_captured: bool = False
    pmkid_captured: bool = False
    beacon_count: int = 0
    data_packets: int = 0
    first_seen: datetime
    last_seen: datetime
    manufacturer: Optional[str] = None

    class Config:
        frozen = True
