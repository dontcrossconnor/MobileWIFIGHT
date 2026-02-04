"""API dependencies - Service instances"""
from app.services.adapter import AdapterService
from app.services.scanner import ScannerService
from app.services.attack import AttackService
from app.services.capture import CaptureService
from app.services.cracker import CrackerService
from app.services.report import ReportService

# Service singletons
adapter_service = AdapterService()
scanner_service = ScannerService()
attack_service = AttackService()
capture_service = CaptureService()
cracker_service = CrackerService()
report_service = ReportService()


def get_adapter_service() -> AdapterService:
    """Get adapter service instance"""
    return adapter_service


def get_scanner_service() -> ScannerService:
    """Get scanner service instance"""
    return scanner_service


def get_attack_service() -> AttackService:
    """Get attack service instance"""
    return attack_service


def get_capture_service() -> CaptureService:
    """Get capture service instance"""
    return capture_service


def get_cracker_service() -> CrackerService:
    """Get cracker service instance"""
    return cracker_service


def get_report_service() -> ReportService:
    """Get report service instance"""
    return report_service
