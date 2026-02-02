"""Password cracking data models - IMMUTABLE"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from uuid import UUID


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
    """Cracking job configuration - IMMUTABLE"""
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

    class Config:
        frozen = True


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
    cost_usd: Decimal = Decimal("0.0")
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[str] = []
