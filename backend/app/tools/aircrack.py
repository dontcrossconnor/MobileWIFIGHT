"""Aircrack-ng suite wrapper"""
import asyncio
from typing import Optional


class AircrackNG:
    """Wrapper for aircrack-ng suite"""

    async def start_monitor_mode(self, interface: str) -> str:
        """Enable monitor mode using airmon-ng. Returns monitor interface name."""
        proc = await asyncio.create_subprocess_exec(
            "airmon-ng", "start", interface,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        if proc.returncode != 0 and "monitor mode" not in (proc.stderr.read().decode() if proc.stderr else ""):
            raise RuntimeError(f"Failed to start monitor mode: {interface}")
        return f"{interface}mon" if not interface.endswith("mon") else interface

    async def stop_monitor_mode(self, interface: str) -> str:
        """Disable monitor mode. Returns managed interface name."""
        base = interface.rstrip("mon") if interface.endswith("mon") else interface
        proc = await asyncio.create_subprocess_exec(
            "airmon-ng", "stop", interface,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        return base

    async def start_dump(
        self, interface: str, output: str, channel: Optional[int] = None
    ) -> asyncio.subprocess.Process:
        """Start airodump-ng capture. Returns process handle."""
        cmd = ["airodump-ng", interface, "-w", output]
        if channel is not None:
            cmd.extend(["--channel", str(channel)])
        return await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def deauth(
        self,
        interface: str,
        bssid: str,
        client: Optional[str] = None,
        count: int = 0,
    ) -> None:
        """Send deauth packets."""
        cmd = ["aireplay-ng", "--deauth", str(count), "-a", bssid, interface]
        if client:
            cmd.extend(["-c", client])
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()

    async def verify_handshake(self, capture_file: str, bssid: str) -> bool:
        """Verify 4-way handshake in capture file."""
        proc = await asyncio.create_subprocess_exec(
            "aircrack-ng", capture_file, "-b", bssid,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return b"1 handshake" in stdout or b"Handshake" in stdout
