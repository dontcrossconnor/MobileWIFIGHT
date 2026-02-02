"""Adapter service implementation"""
from typing import List
from app.services.interfaces import IAdapterService
from app.models import Adapter, AdapterMode, AdapterStatus
from app.tools.aircrack import AircrackNG
from app.tools.network import NetworkManager

# Standard 2.4GHz and 5GHz channels
CHANNELS_2GHZ = list(range(1, 12))
CHANNELS_5GHZ = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165]


class AdapterService(IAdapterService):
    """WiFi adapter management service"""

    def __init__(self) -> None:
        self._aircrack = AircrackNG()
        self._network = NetworkManager()

    async def detect_adapters(self) -> List[Adapter]:
        """Detect all available WiFi adapters."""
        interfaces = await self._network.get_interfaces()
        adapters: List[Adapter] = []
        for iface in interfaces:
            mode = AdapterMode.MONITOR if (iface.get("mode") or "").lower() == "monitor" else AdapterMode.MANAGED
            chipset = iface.get("chipset") or await self._network.get_chipset(iface["interface"])
            adapters.append(
                Adapter(
                    interface=iface["interface"],
                    driver=iface.get("driver", "unknown"),
                    chipset=chipset,
                    mac_address=iface.get("mac", "00:00:00:00:00:00"),
                    mode=mode,
                    status=AdapterStatus.READY,
                    current_channel=iface.get("channel"),
                    supported_channels_2ghz=CHANNELS_2GHZ,
                    supported_channels_5ghz=CHANNELS_5GHZ,
                    monitor_mode_capable=True,
                    injection_capable=True,
                    tx_power_dbm=20,
                )
            )
        return adapters

    async def get_adapter(self, interface: str) -> Adapter:
        """Get adapter information by interface name."""
        adapters = await self.detect_adapters()
        for a in adapters:
            if a.interface == interface:
                return a
        raise ValueError("Adapter not found")

    async def set_monitor_mode(self, interface: str, enable: bool) -> Adapter:
        """Enable or disable monitor mode."""
        current = await self.get_adapter(interface)
        if enable:
            mon_iface = await self._aircrack.start_monitor_mode(interface)
            return Adapter(
                interface=mon_iface,
                driver=current.driver,
                chipset=current.chipset,
                mac_address=current.mac_address,
                mode=AdapterMode.MONITOR,
                status=AdapterStatus.READY,
                current_channel=current.current_channel,
                supported_channels_2ghz=current.supported_channels_2ghz,
                supported_channels_5ghz=current.supported_channels_5ghz,
                monitor_mode_capable=current.monitor_mode_capable,
                injection_capable=current.injection_capable,
                tx_power_dbm=current.tx_power_dbm,
            )
        managed = await self._aircrack.stop_monitor_mode(interface)
        return Adapter(
            interface=managed,
            driver=current.driver,
            chipset=current.chipset,
            mac_address=current.mac_address,
            mode=AdapterMode.MANAGED,
            status=AdapterStatus.READY,
            current_channel=current.current_channel,
            supported_channels_2ghz=current.supported_channels_2ghz,
            supported_channels_5ghz=current.supported_channels_5ghz,
            monitor_mode_capable=current.monitor_mode_capable,
            injection_capable=current.injection_capable,
            tx_power_dbm=current.tx_power_dbm,
        )

    async def set_channel(self, interface: str, channel: int) -> None:
        """Set WiFi channel (1-165)."""
        if channel < 1 or channel > 165:
            raise ValueError("Invalid channel")
        await self._network.set_channel(interface, channel)

    async def set_tx_power(self, interface: str, power_dbm: int) -> None:
        """Set transmission power in dBm."""
        if power_dbm < 0 or power_dbm > 30:
            raise ValueError("Invalid TX power")
        await self._network.set_tx_power(interface, power_dbm)

    async def validate_alfa_adapter(self, interface: str) -> bool:
        """Validate Alfa AWUS036ACH (RTL8812AU) adapter."""
        adapter = await self.get_adapter(interface)
        chipset_lower = adapter.chipset.lower()
        return "8812" in chipset_lower or "rtl8812au" in chipset_lower or "rtl88" in chipset_lower
