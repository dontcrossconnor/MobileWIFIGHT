"""Pytest configuration and fixtures"""
import pytest
from datetime import datetime
from uuid import uuid4
from decimal import Decimal

from app.models import (
    Network,
    Client,
    EncryptionType,
    CipherType,
    AuthenticationType,
    Adapter,
    AdapterMode,
    AdapterStatus,
    Attack,
    AttackType,
    AttackStatus,
    AttackConfig,
    AttackResult,
    CrackingJob,
    CrackingJobConfig,
    CrackingProgress,
    CrackMode,
    JobStatus,
    GPUProvider,
    GPUInstance,
    ScanSession,
    ScanConfig,
    ScanMode,
    ScanStatus,
)


@pytest.fixture
def sample_network():
    """Sample network for testing"""
    return Network(
        bssid="00:11:22:33:44:55",
        essid="TestNetwork",
        channel=6,
        frequency=2437,
        signal=-60,
        encryption=EncryptionType.WPA2,
        cipher=CipherType.CCMP,
        authentication=AuthenticationType.PSK,
        wps=False,
        wps_locked=False,
        clients=[],
        handshake_captured=False,
        pmkid_captured=False,
        beacon_count=100,
        data_packets=50,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        manufacturer="Cisco",
    )


@pytest.fixture
def sample_client():
    """Sample client for testing"""
    return Client(
        mac="AA:BB:CC:DD:EE:FF",
        bssid="00:11:22:33:44:55",
        probes=["HomeNetwork", "WorkNetwork"],
        signal=-55,
        packets=25,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        manufacturer="Apple",
    )


@pytest.fixture
def sample_adapter():
    """Sample WiFi adapter for testing"""
    return Adapter(
        interface="wlan0",
        driver="rtl8812au",
        chipset="Realtek RTL8812AU",
        mac_address="11:22:33:44:55:66",
        mode=AdapterMode.MANAGED,
        status=AdapterStatus.READY,
        current_channel=None,
        supported_channels_2ghz=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        supported_channels_5ghz=[36, 40, 44, 48, 149, 153, 157, 161, 165],
        monitor_mode_capable=True,
        injection_capable=True,
        tx_power_dbm=20,
    )


@pytest.fixture
def sample_attack_config():
    """Sample attack configuration for testing"""
    return AttackConfig(
        target_bssid="00:11:22:33:44:55",
        target_essid="TestNetwork",
        attack_type=AttackType.DEAUTH,
        duration_seconds=300,
        deauth_count=0,
        channel=6,
        interface="wlan0mon",
    )


@pytest.fixture
def sample_attack(sample_attack_config):
    """Sample attack for testing"""
    return Attack(
        id=uuid4(),
        config=sample_attack_config,
        status=AttackStatus.PENDING,
        started_at=datetime.now(),
        completed_at=None,
        result=None,
        logs=[],
        progress_percent=0.0,
    )


@pytest.fixture
def sample_attack_result():
    """Sample attack result for testing"""
    return AttackResult(
        success=True,
        message="Handshake captured successfully",
        handshake_file="/tmp/handshake.cap",
        pmkid_file=None,
        wps_pin=None,
        wep_key=None,
        capture_files=["/tmp/handshake.cap"],
        packets_sent=1000,
        duration_seconds=45.5,
    )


@pytest.fixture
def sample_cracking_config():
    """Sample cracking job configuration for testing"""
    return CrackingJobConfig(
        handshake_file="/tmp/handshake.cap",
        bssid="00:11:22:33:44:55",
        essid="TestNetwork",
        attack_mode=CrackMode.WORDLIST,
        wordlist_path="/usr/share/wordlists/rockyou.txt",
        wordlist_name="rockyou.txt",
        mask=None,
        rules_file=None,
        gpu_provider=GPUProvider.VASTAI,
        max_cost_usd=10.0,
        timeout_minutes=120,
    )


@pytest.fixture
def sample_gpu_instance():
    """Sample GPU instance for testing"""
    return GPUInstance(
        instance_id="12345",
        provider=GPUProvider.VASTAI,
        gpu_model="RTX 4090",
        gpu_count=1,
        cost_per_hour=0.50,
        status="running",
        ip_address="192.168.1.100",
    )


@pytest.fixture
def sample_cracking_progress():
    """Sample cracking progress for testing"""
    job_id = uuid4()
    return CrackingProgress(
        job_id=job_id,
        status=JobStatus.RUNNING,
        progress_percent=25.5,
        speed_mh_per_sec=1234.56,
        tried_passwords=1000000,
        total_passwords=4000000,
        eta_seconds=3600,
        current_wordlist_position=1000000,
    )


@pytest.fixture
def sample_cracking_job(sample_cracking_config, sample_cracking_progress):
    """Sample cracking job for testing"""
    return CrackingJob(
        id=sample_cracking_progress.job_id,
        config=sample_cracking_config,
        status=JobStatus.RUNNING,
        gpu_instance=None,
        progress=sample_cracking_progress,
        password=None,
        cost_usd=Decimal("0.50"),
        created_at=datetime.now(),
        started_at=datetime.now(),
        completed_at=None,
        logs=[],
    )


@pytest.fixture
def sample_scan_config():
    """Sample scan configuration for testing"""
    return ScanConfig(
        interface="wlan0mon",
        mode=ScanMode.PASSIVE,
        channels=None,
        hop_interval_ms=500,
        capture_file="/tmp/scan.cap",
    )


@pytest.fixture
def sample_scan_session(sample_scan_config):
    """Sample scan session for testing"""
    return ScanSession(
        id=uuid4(),
        config=sample_scan_config,
        status=ScanStatus.RUNNING,
        networks_found=10,
        clients_found=25,
        handshakes_captured=2,
        packets_captured=5000,
        started_at=datetime.now(),
        updated_at=datetime.now(),
    )
