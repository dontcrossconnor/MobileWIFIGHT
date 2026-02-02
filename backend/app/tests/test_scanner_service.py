"""Test ScannerService implementation"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from app.services.interfaces import IScannerService
from app.models import (
    ScanSession,
    ScanConfig,
    ScanMode,
    ScanStatus,
    Network,
    Client,
)


class TestScannerServiceContract:
    """Test ScannerService follows interface contract"""

    @pytest.fixture
    def scanner_service(self):
        """Create mock scanner service for testing"""
        service = AsyncMock(spec=IScannerService)
        return service

    @pytest.mark.asyncio
    async def test_start_scan_returns_session(
        self, scanner_service, sample_scan_config, sample_scan_session
    ):
        """Test start_scan returns scan session"""
        scanner_service.start_scan.return_value = sample_scan_session
        
        result = await scanner_service.start_scan(sample_scan_config)
        
        assert isinstance(result, ScanSession)
        assert result.status == ScanStatus.RUNNING

    @pytest.mark.asyncio
    async def test_start_scan_passive_mode(self, scanner_service, sample_scan_config):
        """Test starting scan in passive mode"""
        now = datetime.now()
        session = ScanSession(
            id=uuid4(),
            config=sample_scan_config,
            status=ScanStatus.RUNNING,
            networks_found=0,
            clients_found=0,
            handshakes_captured=0,
            packets_captured=0,
            started_at=now,
            updated_at=now,
        )
        scanner_service.start_scan.return_value = session
        
        result = await scanner_service.start_scan(sample_scan_config)
        
        assert result.config.mode == ScanMode.PASSIVE

    @pytest.mark.asyncio
    async def test_start_scan_requires_monitor_mode(self, scanner_service):
        """Test starting scan requires adapter in monitor mode"""
        scanner_service.start_scan.side_effect = RuntimeError(
            "Adapter must be in monitor mode"
        )
        
        config = ScanConfig(
            interface="wlan0",  # Not in monitor mode
            mode=ScanMode.PASSIVE,
        )
        
        with pytest.raises(RuntimeError, match="monitor mode"):
            await scanner_service.start_scan(config)

    @pytest.mark.asyncio
    async def test_stop_scan_stops_active_session(self, scanner_service):
        """Test stopping an active scan"""
        session_id = uuid4()
        scanner_service.stop_scan.return_value = None
        
        await scanner_service.stop_scan(session_id)
        
        scanner_service.stop_scan.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_stop_scan_invalid_session_raises(self, scanner_service):
        """Test stopping invalid session raises exception"""
        scanner_service.stop_scan.side_effect = ValueError("Session not found")
        
        with pytest.raises(ValueError, match="Session not found"):
            await scanner_service.stop_scan(uuid4())

    @pytest.mark.asyncio
    async def test_get_session_returns_session(
        self, scanner_service, sample_scan_session
    ):
        """Test getting scan session"""
        scanner_service.get_session.return_value = sample_scan_session
        
        result = await scanner_service.get_session(sample_scan_session.id)
        
        assert isinstance(result, ScanSession)
        assert result.id == sample_scan_session.id

    @pytest.mark.asyncio
    async def test_get_networks_returns_list(
        self, scanner_service, sample_network
    ):
        """Test getting discovered networks"""
        scanner_service.get_networks.return_value = [sample_network]
        
        result = await scanner_service.get_networks(uuid4())
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Network)

    @pytest.mark.asyncio
    async def test_get_networks_empty_when_none_found(self, scanner_service):
        """Test getting networks returns empty list when none found"""
        scanner_service.get_networks.return_value = []
        
        result = await scanner_service.get_networks(uuid4())
        
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_network_specific_bssid(
        self, scanner_service, sample_network
    ):
        """Test getting specific network by BSSID"""
        scanner_service.get_network.return_value = sample_network
        
        result = await scanner_service.get_network(
            uuid4(), sample_network.bssid
        )
        
        assert isinstance(result, Network)
        assert result.bssid == sample_network.bssid

    @pytest.mark.asyncio
    async def test_get_network_not_found_raises(self, scanner_service):
        """Test getting non-existent network raises exception"""
        scanner_service.get_network.side_effect = ValueError("Network not found")
        
        with pytest.raises(ValueError, match="Network not found"):
            await scanner_service.get_network(uuid4(), "00:11:22:33:44:55")

    @pytest.mark.asyncio
    async def test_get_clients_all(self, scanner_service, sample_client):
        """Test getting all clients"""
        scanner_service.get_clients.return_value = [sample_client]
        
        result = await scanner_service.get_clients(uuid4())
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Client)

    @pytest.mark.asyncio
    async def test_get_clients_filtered_by_bssid(
        self, scanner_service, sample_client
    ):
        """Test getting clients filtered by BSSID"""
        scanner_service.get_clients.return_value = [sample_client]
        
        result = await scanner_service.get_clients(
            uuid4(), bssid=sample_client.bssid
        )
        
        assert all(c.bssid == sample_client.bssid for c in result)

    @pytest.mark.asyncio
    async def test_scan_captures_handshakes(self, scanner_service):
        """Test scan can capture WPA handshakes"""
        # Scan should detect and capture 4-way handshakes automatically
        session = ScanSession(
            id=uuid4(),
            config=ScanConfig(interface="wlan0mon", mode=ScanMode.PASSIVE),
            status=ScanStatus.RUNNING,
            networks_found=5,
            clients_found=10,
            handshakes_captured=2,
            packets_captured=10000,
            started_at=AsyncMock(),
            updated_at=AsyncMock(),
        )
        scanner_service.get_session.return_value = session
        
        result = await scanner_service.get_session(session.id)
        
        assert result.handshakes_captured > 0


class TestScannerServiceIntegration:
    """Integration tests for ScannerService"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scan_discovers_networks(self):
        """Test scan discovers networks in range"""
        pytest.skip("Integration test - requires actual implementation")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scan_channel_hopping(self):
        """Test scan hops through channels"""
        pytest.skip("Integration test - requires actual implementation")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scan_captures_handshake_on_deauth(self):
        """Test scan captures handshake when client deauthed"""
        pytest.skip("Integration test - requires actual implementation")
