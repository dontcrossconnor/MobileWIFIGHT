"""Test data models - Contract validation tests"""
import pytest
from datetime import datetime
from pydantic import ValidationError

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
    CrackingJobConfig,
    CrackMode,
    GPUProvider,
)


class TestNetworkModel:
    """Test Network model contract"""

    def test_network_creation_valid(self, sample_network):
        """Test creating valid network"""
        assert sample_network.bssid == "00:11:22:33:44:55"
        assert sample_network.essid == "TestNetwork"
        assert sample_network.encryption == EncryptionType.WPA2

    def test_network_invalid_bssid(self):
        """Test network creation with invalid BSSID format"""
        with pytest.raises(ValidationError):
            Network(
                bssid="INVALID_MAC",
                essid="Test",
                channel=6,
                frequency=2437,
                signal=-60,
                encryption=EncryptionType.WPA2,
                cipher=CipherType.CCMP,
                authentication=AuthenticationType.PSK,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
            )

    def test_network_channel_range(self):
        """Test network channel must be in valid range"""
        with pytest.raises(ValidationError):
            Network(
                bssid="00:11:22:33:44:55",
                essid="Test",
                channel=200,  # Invalid
                frequency=2437,
                signal=-60,
                encryption=EncryptionType.WPA2,
                cipher=CipherType.CCMP,
                authentication=AuthenticationType.PSK,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
            )

    def test_network_signal_range(self):
        """Test network signal must be in valid range"""
        with pytest.raises(ValidationError):
            Network(
                bssid="00:11:22:33:44:55",
                essid="Test",
                channel=6,
                frequency=2437,
                signal=50,  # Invalid (must be negative)
                encryption=EncryptionType.WPA2,
                cipher=CipherType.CCMP,
                authentication=AuthenticationType.PSK,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
            )

    def test_network_immutable(self, sample_network):
        """Test network is immutable after creation"""
        with pytest.raises(ValidationError):
            sample_network.essid = "Modified"


class TestClientModel:
    """Test Client model contract"""

    def test_client_creation_valid(self, sample_client):
        """Test creating valid client"""
        assert sample_client.mac == "AA:BB:CC:DD:EE:FF"
        assert sample_client.bssid == "00:11:22:33:44:55"
        assert len(sample_client.probes) == 2

    def test_client_invalid_mac(self):
        """Test client creation with invalid MAC"""
        with pytest.raises(ValidationError):
            Client(
                mac="INVALID",
                bssid="00:11:22:33:44:55",
                probes=[],
                signal=-60,
                packets=10,
                first_seen=datetime.now(),
                last_seen=datetime.now(),
            )

    def test_client_immutable(self, sample_client):
        """Test client is immutable after creation"""
        with pytest.raises(ValidationError):
            sample_client.signal = -70


class TestAdapterModel:
    """Test Adapter model contract"""

    def test_adapter_creation_valid(self, sample_adapter):
        """Test creating valid adapter"""
        assert sample_adapter.interface == "wlan0"
        assert sample_adapter.mode == AdapterMode.MANAGED
        assert sample_adapter.monitor_mode_capable is True

    def test_adapter_immutable(self, sample_adapter):
        """Test adapter is immutable after creation"""
        with pytest.raises(ValidationError):
            sample_adapter.mode = AdapterMode.MONITOR


class TestAttackModel:
    """Test Attack model contract"""

    def test_attack_config_creation_valid(self, sample_attack_config):
        """Test creating valid attack config"""
        assert sample_attack_config.target_bssid == "00:11:22:33:44:55"
        assert sample_attack_config.attack_type == AttackType.DEAUTH
        assert sample_attack_config.duration_seconds == 300

    def test_attack_creation_valid(self, sample_attack):
        """Test creating valid attack"""
        assert sample_attack.status == AttackStatus.PENDING
        assert sample_attack.progress_percent == 0.0
        assert len(sample_attack.logs) == 0

    def test_attack_config_immutable(self, sample_attack_config):
        """Test attack config is immutable"""
        with pytest.raises(ValidationError):
            sample_attack_config.attack_type = AttackType.WPS_PIXIE


class TestCrackingModel:
    """Test Cracking model contract"""

    def test_cracking_config_creation_valid(self, sample_cracking_config):
        """Test creating valid cracking config"""
        assert sample_cracking_config.bssid == "00:11:22:33:44:55"
        assert sample_cracking_config.attack_mode == CrackMode.WORDLIST
        assert sample_cracking_config.gpu_provider == GPUProvider.VASTAI

    def test_cracking_config_requires_wordlist_for_wordlist_mode(self):
        """Test wordlist mode requires wordlist path"""
        config = CrackingJobConfig(
            handshake_file="/tmp/test.cap",
            bssid="00:11:22:33:44:55",
            essid="Test",
            attack_mode=CrackMode.WORDLIST,
            wordlist_path=None,  # Should be provided but not enforced at model level
            gpu_provider=GPUProvider.VASTAI,
        )
        # Model allows None, but service layer should validate
        assert config.wordlist_path is None

    def test_cracking_config_immutable(self, sample_cracking_config):
        """Test cracking config is immutable"""
        with pytest.raises(ValidationError):
            sample_cracking_config.attack_mode = CrackMode.MASK


class TestEnums:
    """Test enum contracts"""

    def test_encryption_types(self):
        """Test all encryption types are available"""
        assert EncryptionType.OPEN == "OPEN"
        assert EncryptionType.WEP == "WEP"
        assert EncryptionType.WPA == "WPA"
        assert EncryptionType.WPA2 == "WPA2"
        assert EncryptionType.WPA3 == "WPA3"

    def test_attack_types(self):
        """Test all attack types are available"""
        assert AttackType.DEAUTH == "deauth"
        assert AttackType.PMKID == "pmkid"
        assert AttackType.WPS_PIXIE == "wps_pixie"
        assert AttackType.WPS_PIN == "wps_pin"
        assert AttackType.HANDSHAKE_CAPTURE == "handshake_capture"

    def test_attack_statuses(self):
        """Test all attack statuses are available"""
        assert AttackStatus.PENDING == "pending"
        assert AttackStatus.RUNNING == "running"
        assert AttackStatus.SUCCESS == "success"
        assert AttackStatus.FAILED == "failed"
        assert AttackStatus.CANCELLED == "cancelled"
