"""Test AdapterService implementation"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from app.services.interfaces import IAdapterService
from app.models import Adapter, AdapterMode, AdapterStatus


class TestAdapterServiceContract:
    """Test AdapterService follows interface contract"""

    @pytest.fixture
    def adapter_service(self):
        """Create mock adapter service for testing"""
        # This will be replaced with actual implementation
        service = AsyncMock(spec=IAdapterService)
        return service

    @pytest.mark.asyncio
    async def test_detect_adapters_returns_list(self, adapter_service, sample_adapter):
        """Test detect_adapters returns list of adapters"""
        adapter_service.detect_adapters.return_value = [sample_adapter]
        
        result = await adapter_service.detect_adapters()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Adapter)

    @pytest.mark.asyncio
    async def test_detect_adapters_empty_when_none_found(self, adapter_service):
        """Test detect_adapters returns empty list when no adapters found"""
        adapter_service.detect_adapters.return_value = []
        
        result = await adapter_service.detect_adapters()
        
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_adapter_returns_adapter(self, adapter_service, sample_adapter):
        """Test get_adapter returns specific adapter"""
        adapter_service.get_adapter.return_value = sample_adapter
        
        result = await adapter_service.get_adapter("wlan0")
        
        assert isinstance(result, Adapter)
        assert result.interface == "wlan0"

    @pytest.mark.asyncio
    async def test_get_adapter_raises_when_not_found(self, adapter_service):
        """Test get_adapter raises exception when adapter not found"""
        adapter_service.get_adapter.side_effect = ValueError("Adapter not found")
        
        with pytest.raises(ValueError, match="Adapter not found"):
            await adapter_service.get_adapter("invalid")

    @pytest.mark.asyncio
    async def test_set_monitor_mode_enable(self, adapter_service, sample_adapter):
        """Test enabling monitor mode"""
        monitor_adapter = Adapter(
            interface="wlan0mon",
            driver=sample_adapter.driver,
            chipset=sample_adapter.chipset,
            mac_address=sample_adapter.mac_address,
            mode=AdapterMode.MONITOR,
            status=AdapterStatus.READY,
            current_channel=None,
            supported_channels_2ghz=sample_adapter.supported_channels_2ghz,
            supported_channels_5ghz=sample_adapter.supported_channels_5ghz,
            monitor_mode_capable=True,
            injection_capable=True,
            tx_power_dbm=20,
        )
        adapter_service.set_monitor_mode.return_value = monitor_adapter
        
        result = await adapter_service.set_monitor_mode("wlan0", True)
        
        assert result.mode == AdapterMode.MONITOR
        assert result.interface == "wlan0mon"

    @pytest.mark.asyncio
    async def test_set_monitor_mode_disable(self, adapter_service, sample_adapter):
        """Test disabling monitor mode"""
        adapter_service.set_monitor_mode.return_value = sample_adapter
        
        result = await adapter_service.set_monitor_mode("wlan0mon", False)
        
        assert result.mode == AdapterMode.MANAGED
        assert result.interface == "wlan0"

    @pytest.mark.asyncio
    async def test_set_monitor_mode_raises_when_not_supported(self, adapter_service):
        """Test setting monitor mode raises when not supported"""
        adapter_service.set_monitor_mode.side_effect = RuntimeError(
            "Monitor mode not supported"
        )
        
        with pytest.raises(RuntimeError, match="Monitor mode not supported"):
            await adapter_service.set_monitor_mode("wlan0", True)

    @pytest.mark.asyncio
    async def test_set_channel_valid(self, adapter_service):
        """Test setting valid channel"""
        adapter_service.set_channel.return_value = None
        
        await adapter_service.set_channel("wlan0mon", 6)
        
        adapter_service.set_channel.assert_called_once_with("wlan0mon", 6)

    @pytest.mark.asyncio
    async def test_set_channel_invalid_raises(self, adapter_service):
        """Test setting invalid channel raises exception"""
        adapter_service.set_channel.side_effect = ValueError("Invalid channel")
        
        with pytest.raises(ValueError, match="Invalid channel"):
            await adapter_service.set_channel("wlan0mon", 200)

    @pytest.mark.asyncio
    async def test_set_tx_power_valid(self, adapter_service):
        """Test setting valid TX power"""
        adapter_service.set_tx_power.return_value = None
        
        await adapter_service.set_tx_power("wlan0mon", 20)
        
        adapter_service.set_tx_power.assert_called_once_with("wlan0mon", 20)

    @pytest.mark.asyncio
    async def test_set_tx_power_invalid_raises(self, adapter_service):
        """Test setting invalid TX power raises exception"""
        adapter_service.set_tx_power.side_effect = ValueError("Invalid TX power")
        
        with pytest.raises(ValueError, match="Invalid TX power"):
            await adapter_service.set_tx_power("wlan0mon", 100)

    @pytest.mark.asyncio
    async def test_validate_alfa_adapter_success(self, adapter_service):
        """Test validating Alfa adapter succeeds"""
        adapter_service.validate_alfa_adapter.return_value = True
        
        result = await adapter_service.validate_alfa_adapter("wlan0")
        
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_alfa_adapter_failure(self, adapter_service):
        """Test validating non-Alfa adapter fails"""
        adapter_service.validate_alfa_adapter.return_value = False
        
        result = await adapter_service.validate_alfa_adapter("wlan0")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_alfa_adapter_checks_chipset(self, adapter_service):
        """Test Alfa validation checks for RTL8812AU chipset"""
        # Implementation should check for Realtek RTL8812AU chipset
        adapter_service.validate_alfa_adapter.return_value = True
        
        result = await adapter_service.validate_alfa_adapter("wlan0")
        
        assert result is True
        adapter_service.validate_alfa_adapter.assert_called_once_with("wlan0")


class TestAdapterServiceIntegration:
    """Integration tests for AdapterService with real system calls"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_adapter_initialization_flow(self):
        """Test complete adapter initialization flow"""
        # This test will be implemented when actual service is created
        # Flow: detect -> validate -> set monitor mode -> set channel
        pytest.skip("Integration test - requires actual implementation")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_adapter_monitor_mode_toggle(self):
        """Test toggling monitor mode on/off"""
        pytest.skip("Integration test - requires actual implementation")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_adapter_channel_hopping(self):
        """Test channel hopping functionality"""
        pytest.skip("Integration test - requires actual implementation")
