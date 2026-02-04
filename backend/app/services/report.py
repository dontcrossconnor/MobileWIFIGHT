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
        """Export report to file - REAL implementation"""
        report = await self.get_report(report_id)
        
        if report.format == ReportFormat.PDF:
            return await self._generate_pdf_file(report, output_path)
        elif report.format == ReportFormat.HTML:
            return await self._generate_html_file(report, output_path)
        elif report.format == ReportFormat.JSON:
            return await self._generate_json_file(report, output_path)
        elif report.format == ReportFormat.MARKDOWN:
            return await self._generate_markdown_file(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {report.format}")
    
    async def _generate_pdf_file(self, report: Report, output_path: str) -> str:
        """Generate PDF report file"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        import os
        
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
        )
        story.append(Paragraph(report.title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Metadata
        metadata = [
            ['Organization:', report.organization],
            ['Tester:', report.tester_name],
            ['Test Date:', report.test_date.strftime('%Y-%m-%d %H:%M')],
            ['Networks Tested:', str(report.networks_tested)],
            ['Vulnerabilities Found:', str(report.vulnerabilities_found)],
        ]
        meta_table = Table(metadata, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Executive Summary
        story.append(Paragraph('Executive Summary', styles['Heading1']))
        story.append(Paragraph(report.executive_summary, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Findings
        story.append(PageBreak())
        story.append(Paragraph('Security Findings', styles['Heading1']))
        
        for i, finding in enumerate(report.findings, 1):
            # Finding title with severity
            severity_colors = {
                VulnerabilitySeverity.CRITICAL: '#ef4444',
                VulnerabilitySeverity.HIGH: '#f59e0b',
                VulnerabilitySeverity.MEDIUM: '#3b82f6',
                VulnerabilitySeverity.LOW: '#10b981',
                VulnerabilitySeverity.INFO: '#6b7280',
            }
            
            story.append(Paragraph(f'{i}. {finding.title}', styles['Heading2']))
            story.append(Paragraph(f'<b>Severity:</b> <font color="{severity_colors[finding.severity]}">{finding.severity.value.upper()}</font>', styles['Normal']))
            story.append(Paragraph(f'<b>Affected Network:</b> {finding.affected_network}', styles['Normal']))
            story.append(Paragraph(f'<b>Description:</b> {finding.description}', styles['Normal']))
            story.append(Paragraph('<b>Remediation:</b>', styles['Normal']))
            story.append(Paragraph(finding.remediation, styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Recommendations
        story.append(PageBreak())
        story.append(Paragraph('Recommendations', styles['Heading1']))
        
        for i, rec in enumerate(report.recommendations, 1):
            story.append(Paragraph(f'{i}. {rec}', styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    async def _generate_html_file(self, report: Report, output_path: str) -> str:
        """Generate HTML report file"""
        import os
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        severity_colors = {
            'critical': '#dc2626',
            'high': '#ea580c',
            'medium': '#2563eb',
            'low': '#059669',
            'info': '#4b5563',
        }
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f9fafb; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
        h2 {{ color: #374151; margin-top: 30px; }}
        .metadata {{ background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .finding {{ border-left: 4px solid #e5e7eb; padding: 15px; margin: 20px 0; background: #f9fafb; }}
        .severity {{ display: inline-block; padding: 4px 12px; border-radius: 4px; color: white; font-weight: bold; font-size: 12px; }}
        .evidence {{ background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 4px; font-family: monospace; }}
        .recommendation {{ margin: 10px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report.title}</h1>
        
        <div class="metadata">
            <p><strong>Organization:</strong> {report.organization}</p>
            <p><strong>Tester:</strong> {report.tester_name}</p>
            <p><strong>Test Date:</strong> {report.test_date.strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Networks Tested:</strong> {report.networks_tested}</p>
            <p><strong>Vulnerabilities Found:</strong> {report.vulnerabilities_found}</p>
        </div>
        
        <h2>Executive Summary</h2>
        <p>{report.executive_summary}</p>
        
        <h2>Security Findings</h2>
"""
        
        for i, finding in enumerate(report.findings, 1):
            color = severity_colors.get(finding.severity.value, '#6b7280')
            html += f"""
        <div class="finding">
            <h3>{i}. {finding.title}</h3>
            <p><span class="severity" style="background-color: {color};">{finding.severity.value.upper()}</span></p>
            <p><strong>Affected Network:</strong> {finding.affected_network}</p>
            <p><strong>Description:</strong> {finding.description}</p>
            <p><strong>Evidence:</strong></p>
            <div class="evidence">
                {'<br>'.join(finding.evidence)}
            </div>
            <p><strong>Remediation:</strong> {finding.remediation}</p>
        </div>
"""
        
        html += """
        <h2>Recommendations</h2>
        <div class="recommendation">
"""
        
        for i, rec in enumerate(report.recommendations, 1):
            html += f"            <p>{i}. {rec}</p>\n"
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    async def _generate_json_file(self, report: Report, output_path: str) -> str:
        """Generate JSON report file"""
        import json
        import os
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report.dict(), f, indent=2, default=str)
        
        return output_path
    
    async def _generate_markdown_file(self, report: Report, output_path: str) -> str:
        """Generate Markdown report file"""
        import os
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        md = f"""# {report.title}

## Metadata

- **Organization**: {report.organization}
- **Tester**: {report.tester_name}
- **Test Date**: {report.test_date.strftime('%Y-%m-%d %H:%M')}
- **Networks Tested**: {report.networks_tested}
- **Vulnerabilities Found**: {report.vulnerabilities_found}

## Executive Summary

{report.executive_summary}

## Security Findings

"""
        
        for i, finding in enumerate(report.findings, 1):
            md += f"""### {i}. {finding.title}

**Severity**: {finding.severity.value.upper()}  
**Affected Network**: {finding.affected_network}

**Description**: {finding.description}

**Evidence**:
{chr(10).join('- ' + e for e in finding.evidence)}

**Remediation**: {finding.remediation}

---

"""
        
        md += f"""## Recommendations

"""
        
        for i, rec in enumerate(report.recommendations, 1):
            md += f"{i}. {rec}\n"
        
        with open(output_path, 'w') as f:
            f.write(md)
        
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
