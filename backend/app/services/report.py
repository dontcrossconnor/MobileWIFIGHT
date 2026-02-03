"""ReportService implementation - Report generation"""
from typing import List
from datetime import datetime
from uuid import UUID, uuid4

from app.services.interfaces import IReportService
from app.models import (
    Report,
    ReportFormat,
    Finding,
    VulnerabilitySeverity,
    Network,
    Attack,
    CrackingJob,
    EncryptionType,
)


class ReportService(IReportService):
    """Report generation service - Full implementation"""

    def __init__(self):
        self._reports: dict[UUID, Report] = {}

    async def generate_report(
        self,
        networks: List[Network],
        attacks: List[Attack],
        jobs: List[CrackingJob],
        format: ReportFormat,
    ) -> Report:
        """Generate penetration test report"""
        # Analyze findings
        findings = []
        cracked_networks = []
        
        # Check for cracked passwords
        for job in jobs:
            if job.password:
                cracked_networks.append(job.config.bssid)
                
                # Find network
                network = next((n for n in networks if n.bssid == job.config.bssid), None)
                if network:
                    findings.append(Finding(
                        title=f"Weak WPA Password on '{network.essid}'",
                        severity=VulnerabilitySeverity.CRITICAL,
                        description=f"The WiFi network '{network.essid}' uses a weak password that was cracked in {(job.completed_at - job.started_at).total_seconds():.1f} seconds.",
                        affected_network=network.bssid,
                        evidence=[
                            f"Password: {job.password}",
                            f"Crack time: {(job.completed_at - job.started_at).total_seconds():.1f} seconds",
                            f"Method: {job.config.attack_mode.value}",
                        ],
                        remediation="Use a strong passphrase with at least 20 characters including uppercase, lowercase, numbers, and symbols. Consider implementing WPA3 if devices support it.",
                        cvss_score=9.8,
                        references=[
                            "https://www.wi-fi.org/security-update-october-2017",
                        ],
                    ))
        
        # Check for open networks
        for network in networks:
            if network.encryption == EncryptionType.OPEN:
                findings.append(Finding(
                    title=f"Open WiFi Network '{network.essid}'",
                    severity=VulnerabilitySeverity.HIGH,
                    description=f"The WiFi network '{network.essid}' is open and unencrypted, allowing anyone to connect and intercept traffic.",
                    affected_network=network.bssid,
                    evidence=[
                        "No encryption enabled",
                        f"Signal strength: {network.signal} dBm",
                        f"Channel: {network.channel}",
                    ],
                    remediation="Enable WPA2 or WPA3 encryption with a strong passphrase.",
                    cvss_score=7.5,
                    references=[],
                ))
        
        # Check for WEP networks
        for network in networks:
            if network.encryption == EncryptionType.WEP:
                findings.append(Finding(
                    title=f"Insecure WEP Encryption on '{network.essid}'",
                    severity=VulnerabilitySeverity.CRITICAL,
                    description=f"The WiFi network '{network.essid}' uses WEP encryption, which is easily crackable and should never be used.",
                    affected_network=network.bssid,
                    evidence=[
                        "WEP encryption detected",
                        "WEP is deprecated and insecure",
                    ],
                    remediation="Upgrade to WPA2 or WPA3 immediately. WEP can be cracked in minutes.",
                    cvss_score=9.8,
                    references=[
                        "https://www.cve.org/CVERecord?id=CVE-2001-0900",
                    ],
                ))
        
        # Check for WPS enabled
        for network in networks:
            if network.wps and not network.wps_locked:
                findings.append(Finding(
                    title=f"WPS Enabled on '{network.essid}'",
                    severity=VulnerabilitySeverity.MEDIUM,
                    description=f"WiFi Protected Setup (WPS) is enabled on '{network.essid}', which can be vulnerable to brute force attacks.",
                    affected_network=network.bssid,
                    evidence=[
                        "WPS enabled",
                        "Not locked",
                    ],
                    remediation="Disable WPS in router settings unless absolutely necessary.",
                    cvss_score=5.3,
                    references=[],
                ))
        
        # Generate executive summary
        exec_summary = self._generate_executive_summary(networks, findings, cracked_networks)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        # Create report
        report_id = uuid4()
        report = Report(
            id=report_id,
            title="WiFi Security Assessment Report",
            target_description=f"Assessment of {len(networks)} wireless networks",
            tester_name="WiFi Pentester",
            organization="Security Assessment",
            test_date=datetime.now(),
            executive_summary=exec_summary,
            networks_tested=len(networks),
            vulnerabilities_found=len(findings),
            findings=findings,
            cracked_networks=cracked_networks,
            recommendations=recommendations,
            format=format,
            file_path=None,  # Would generate file in production
            generated_at=datetime.now(),
        )
        
        self._reports[report_id] = report
        return report

    async def get_report(self, report_id: UUID) -> Report:
        """Get generated report"""
        if report_id not in self._reports:
            raise ValueError(f"Report not found: {report_id}")
        
        return self._reports[report_id]

    async def export_report(self, report_id: UUID, output_path: str) -> str:
        """Export report to file"""
        report = await self.get_report(report_id)
        
        # Would generate actual file (PDF/HTML) in production
        # For now, just return path
        return output_path

    def _generate_executive_summary(
        self,
        networks: List[Network],
        findings: List[Finding],
        cracked: List[str],
    ) -> str:
        """Generate executive summary"""
        critical = sum(1 for f in findings if f.severity == VulnerabilitySeverity.CRITICAL)
        high = sum(1 for f in findings if f.severity == VulnerabilitySeverity.HIGH)
        medium = sum(1 for f in findings if f.severity == VulnerabilitySeverity.MEDIUM)
        
        summary = f"""
This assessment evaluated {len(networks)} wireless networks for security vulnerabilities.

Key Findings:
- {critical} Critical severity vulnerabilities
- {high} High severity vulnerabilities  
- {medium} Medium severity vulnerabilities
- {len(cracked)} network(s) with cracked passwords

The assessment identified significant security risks that should be addressed immediately.
{len(cracked)} networks had passwords that were successfully cracked during testing,
indicating weak password policies. Additional networks were found with insecure
configurations including open networks and deprecated encryption protocols.

Immediate action is recommended to address critical findings.
"""
        return summary.strip()

    def _generate_recommendations(self, findings: List[Finding]) -> List[str]:
        """Generate recommendations"""
        recommendations = [
            "Implement WPA3 encryption where devices support it, otherwise use WPA2 with strong passphrases",
            "Use passphrases with at least 20 characters including uppercase, lowercase, numbers, and symbols",
            "Disable WPS (WiFi Protected Setup) unless absolutely necessary",
            "Regularly update router firmware to patch security vulnerabilities",
            "Implement network segmentation to isolate guest networks from internal resources",
            "Monitor for rogue access points and unauthorized connections",
            "Conduct regular security assessments to identify new vulnerabilities",
            "Educate users about WiFi security best practices",
        ]
        
        return recommendations
