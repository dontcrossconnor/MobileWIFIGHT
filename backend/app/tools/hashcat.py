"""Hashcat wrapper"""
from typing import Optional, Dict, Any
import asyncio


class Hashcat:
    """Wrapper for hashcat"""

    async def crack_wpa(
        self,
        hash_file: str,
        wordlist: str,
        rules: Optional[str] = None,
        mask: Optional[str] = None,
    ) -> Optional[str]:
        """Crack WPA/WPA2 (22000). Returns password if found else None."""
        cmd = ["hashcat", "-m", "22000", hash_file, wordlist, "--pot-file-disable"]
        if rules:
            cmd.extend(["-r", rules])
        if mask:
            cmd.extend(["-a", "3", mask])
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        # Parse stdout for cracked password; simplified
        return None

    async def get_status(self, session_name: str) -> Dict[str, Any]:
        """Get cracking session status."""
        proc = await asyncio.create_subprocess_exec(
            "hashcat", "--session", session_name, "--status",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return {"raw": stdout.decode()}
