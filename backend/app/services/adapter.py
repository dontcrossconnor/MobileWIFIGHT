"""AdapterService implementation - Real WiFi adapter management"""
from typing import List, Optional
from datetime import datetime

from app.services.interfaces import IAdapterService
from app.models import Adapter, AdapterMode, AdapterStatus
from app.tools import AircrackNG, NetworkManager


class AdapterService(IAdapterService):
    """WiFi adapter management service - Full implementation"""

    def __init__(self):
        self.aircrack = AircrackNG()
        self.network = NetworkManager()
        self._adapters_cache: dict[str, Adapter] = {}

    async def detect_adapters(self) -> List[Adapter]:
        """Detect all available WiFi adapters"""
        interfaces = await self.network.get_interfaces()
        adapters = []
        
        for iface_info in interfaces:
            try:
                adapter = await self._build_adapter(iface_info)
                adapters.append(adapter)
                self._adapters_cache[adapter.interface] = adapter
            except Exception as e:
                print(f"Error building adapter for {iface_info.get('interface')}: {e}")
                continue
        
        return adapters

    async def get_adapter(self, interface: str) -> Adapter:
        """Get adapter information"""
        # Check cache first
        if interface in self._adapters_cache:
            # Refresh status
            return await self._refresh_adapter(interface)
        
        # Not in cache, detect it
        adapters = await self.detect_adapters()
        for adapter in adapters:
            if adapter.interface == interface:
                return adapter
        
        raise ValueError(f"Adapter not found: {interface}")

    async def set_monitor_mode(self, interface: str, enable: bool) -> Adapter:
        """Enable or disable monitor mode"""
        # Get current adapter state
        adapter_info = await self.network.get_interface_info(interface)
        
        if enable:
            # Enable monitor mode
            if adapter_info['mode'] == 'monitor':
                # Already in monitor mode
                return await self.get_adapter(interface)
            
            # Use airmon-ng to enable monitor mode
            monitor_interface = await self.aircrack.start_monitor_mode(interface)
            
            # Wait a moment for interface to be ready
            import asyncio
            await asyncio.sleep(2)
            
            # Bring interface up
            await self.network.set_interface_up(monitor_interface)
            
            # Get updated adapter info
            return await self.get_adapter(monitor_interface)
        
        else:
            # Disable monitor mode
            if adapter_info['mode'] != 'monitor':
                # Already in managed mode
                return await self.get_adapter(interface)
            
            # Use airmon-ng to disable monitor mode
            managed_interface = await self.aircrack.stop_monitor_mode(interface)
            
            # Wait a moment
            import asyncio
            await asyncio.sleep(2)
            
            # Bring interface up
            await self.network.set_interface_up(managed_interface)
            
            # Get updated adapter info
            return await self.get_adapter(managed_interface)

    async def set_channel(self, interface: str, channel: int) -> None:
        """Set WiFi channel"""
        # Validate channel
        if channel < 1 or channel > 165:
            raise ValueError(f"Invalid channel: {channel}. Must be 1-165")
        
        # Check if adapter exists and is in monitor mode
        adapter = await self.get_adapter(interface)
        if adapter.mode != AdapterMode.MONITOR:
            raise RuntimeError(f"Interface must be in monitor mode to set channel")
        
        # Set channel
        await self.network.set_channel(interface, channel)

    async def set_tx_power(self, interface: str, power_dbm: int) -> None:
        """Set transmission power"""
        # Validate power
        if power_dbm < 0 or power_dbm > 30:
            raise ValueError(f"Invalid TX power: {power_dbm}. Must be 0-30 dBm")
        
        # Check if adapter exists
        await self.get_adapter(interface)
        
        # Set TX power
        await self.network.set_tx_power(interface, power_dbm)

    async def validate_alfa_adapter(self, interface: str) -> bool:
        """Validate Alfa AWUS036ACH adapter"""
        try:
            adapter = await self.get_adapter(interface)
            
            # Check for RTL8812AU chipset (used in AWUS036ACH)
            if "RTL8812AU" in adapter.chipset or "8812au" in adapter.chipset.lower():
                # Verify monitor mode and injection capability
                return adapter.monitor_mode_capable and adapter.injection_capable
            
            return False
        
        except Exception:
            return False

    async def _build_adapter(self, iface_info: dict) -> Adapter:
        """Build Adapter model from interface info"""
        interface = iface_info['interface']
        
        # Get detailed info
        info = await self.network.get_interface_info(interface)
        
        # Determine mode
        mode = AdapterMode.MONITOR if info['mode'] == 'monitor' else AdapterMode.MANAGED
        
        # Determine status
        status = AdapterStatus.READY if info.get('mac') else AdapterStatus.ERROR
        
        # Get supported channels
        channels_2ghz, channels_5ghz = await self.network.get_supported_channels(interface)
        
        return Adapter(
            interface=interface,
            driver=info.get('driver', 'unknown'),
            chipset=info.get('chipset', 'unknown'),
            mac_address=info.get('mac', '00:00:00:00:00:00'),
            mode=mode,
            status=status,
            current_channel=info.get('channel'),
            supported_channels_2ghz=channels_2ghz,
            supported_channels_5ghz=channels_5ghz,
            monitor_mode_capable=info.get('monitor_capable', False),
            injection_capable=info.get('injection_capable', False),
            tx_power_dbm=info.get('tx_power', 20),
        )

    async def _refresh_adapter(self, interface: str) -> Adapter:
        """Refresh adapter information"""
        info = await self.network.get_interface_info(interface)
        
        mode = AdapterMode.MONITOR if info['mode'] == 'monitor' else AdapterMode.MANAGED
        status = AdapterStatus.READY if info.get('mac') else AdapterStatus.ERROR
        
        channels_2ghz, channels_5ghz = await self.network.get_supported_channels(interface)
        
        adapter = Adapter(
            interface=interface,
            driver=info.get('driver', 'unknown'),
            chipset=info.get('chipset', 'unknown'),
            mac_address=info.get('mac', '00:00:00:00:00:00'),
            mode=mode,
            status=status,
            current_channel=info.get('channel'),
            supported_channels_2ghz=channels_2ghz,
            supported_channels_5ghz=channels_5ghz,
            monitor_mode_capable=info.get('monitor_capable', False),
            injection_capable=info.get('injection_capable', False),
            tx_power_dbm=info.get('tx_power', 20),
        )
        
        self._adapters_cache[interface] = adapter
        return adapter
