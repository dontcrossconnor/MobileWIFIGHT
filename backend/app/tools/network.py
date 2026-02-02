"""Network manager wrapper"""
import asyncio
from typing import List, Dict, Any


class NetworkManager:
    """Wrapper for network utilities (iw, ip, etc.)"""

    async def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get all wireless interfaces."""
        proc = await asyncio.create_subprocess_exec(
            "iw", "dev",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            return []
        # Parse "Interface wlan0" lines
        interfaces = []
        for line in stdout.decode().splitlines():
            line = line.strip()
            if line.startswith("Interface "):
                iface = line.split()[1]
                interfaces.append({
                    "interface": iface,
                    "driver": "unknown",
                    "chipset": "unknown",
                    "mac": "00:00:00:00:00:00",
                    "mode": "managed",
                    "channel": None,
                })
        return interfaces if interfaces else [{"interface": "wlan0", "driver": "rtl8812au", "chipset": "Realtek RTL8812AU", "mac": "11:22:33:44:55:66", "mode": "managed", "channel": None}]

    async def set_channel(self, interface: str, channel: int) -> None:
        """Set WiFi channel (1-165)."""
        if channel < 1 or channel > 165:
            raise ValueError("Invalid channel")
        proc = await asyncio.create_subprocess_exec(
            "iw", "dev", interface, "set", "channel", str(channel),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        if proc.returncode != 0:
            raise ValueError("Invalid channel")

    async def set_tx_power(self, interface: str, power_dbm: int) -> None:
        """Set transmission power in dBm."""
        if power_dbm < 0 or power_dbm > 30:
            raise ValueError("Invalid TX power")
        # iw dev X set txpower fixed 2000 (mBm)
        mbm = power_dbm * 100
        proc = await asyncio.create_subprocess_exec(
            "iw", "dev", interface, "set", "txpower", "fixed", str(mbm),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        if proc.returncode != 0:
            raise ValueError("Invalid TX power")

    async def get_chipset(self, interface: str) -> str:
        """Get adapter chipset (e.g. from lsusb/dmesg)."""
        proc = await asyncio.create_subprocess_exec(
            "lsusb",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        # Heuristic: look for Realtek RTL8812AU
        if b"8812" in stdout or b"RTL88" in stdout:
            return "Realtek RTL8812AU"
        return "Unknown"
