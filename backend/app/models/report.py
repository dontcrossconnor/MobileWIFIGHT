"""Report data models - IMMUTABLE"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


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
    """Security finding - IMMUTABLE"""
    title: str
    severity: VulnerabilitySeverity
    description: str
    affected_network: str  # BSSID
    evidence: List[str]
    remediation: str
    cvss_score: Optional[float] = None
    references: List[str] = []

    class Config:
        frozen = True


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
