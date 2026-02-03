"""Aircrack-ng suite wrapper - Real implementation"""
import asyncio
import os
import re
import signal
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import subprocess


class AircrackNG:
    """Wrapper for aircrack-ng suite with real subprocess calls"""

    def __init__(self):
        self._processes: Dict[str, subprocess.Popen] = {}
        self._verify_installation()

    def _verify_installation(self) -> None:
        """Verify aircrack-ng suite is installed"""
        required_tools = ["airmon-ng", "airodump-ng", "aireplay-ng", "aircrack-ng"]
        missing = []
        
        for tool in required_tools:
            if not self._check_command(tool):
                missing.append(tool)
        
        if missing:
            raise RuntimeError(
                f"Missing aircrack-ng tools: {', '.join(missing)}. "
                "Install with: apt-get install aircrack-ng"
            )

    def _check_command(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run(
                ["which", cmd],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    async def start_monitor_mode(self, interface: str) -> str:
        """Enable monitor mode using airmon-ng"""
        # Kill interfering processes
        await self._run_command(["airmon-ng", "check", "kill"])
        
        # Start monitor mode
        result = await self._run_command(["airmon-ng", "start", interface])
        
        # Parse output to get monitor interface name
        match = re.search(r"monitor mode (?:vif )?enabled (?:on )?(\w+)", result)
        if match:
            return match.group(1)
        
        # Fallback: assume mon suffix
        return f"{interface}mon"

    async def stop_monitor_mode(self, interface: str) -> str:
        """Disable monitor mode using airmon-ng"""
        result = await self._run_command(["airmon-ng", "stop", interface])
        
        # Parse output to get managed interface name
        match = re.search(r"(?:mode vif )?disabled (?:for )?(\w+)", result)
        if match:
            return match.group(1)
        
        # Fallback: remove mon suffix
        if interface.endswith("mon"):
            return interface[:-3]
        return interface

    async def start_capture(
        self,
        interface: str,
        output_prefix: str,
        channel: Optional[int] = None,
        bssid: Optional[str] = None,
    ) -> subprocess.Popen:
        """Start airodump-ng packet capture"""
        cmd = ["airodump-ng", interface, "-w", output_prefix, "--output-format", "pcap,csv"]
        
        if channel:
            cmd.extend(["--channel", str(channel)])
        else:
            # Channel hopping mode
            cmd.append("--band")
            cmd.append("abg")
        
        if bssid:
            cmd.extend(["--bssid", bssid])
        
        # Start process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        self._processes[f"capture_{interface}"] = process
        return process

    async def stop_capture(self, interface: str) -> None:
        """Stop airodump-ng capture"""
        key = f"capture_{interface}"
        if key in self._processes:
            process = self._processes[key]
            process.send_signal(signal.SIGTERM)
            await asyncio.sleep(1)
            if process.poll() is None:
                process.kill()
            del self._processes[key]

    async def deauth_attack(
        self,
        interface: str,
        bssid: str,
        client: Optional[str] = None,
        count: int = 0,
        duration: Optional[int] = None,
    ) -> subprocess.Popen:
        """Execute deauthentication attack"""
        cmd = ["aireplay-ng", "--deauth", str(count), "-a", bssid]
        
        if client:
            cmd.extend(["-c", client])
        
        cmd.append(interface)
        
        # Start attack
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        self._processes[f"deauth_{bssid}"] = process
        
        # If duration specified, schedule stop
        if duration:
            asyncio.create_task(self._stop_after_duration(f"deauth_{bssid}", duration))
        
        return process

    async def fake_auth(
        self,
        interface: str,
        bssid: str,
        essid: str,
    ) -> subprocess.Popen:
        """Fake authentication attack"""
        cmd = ["aireplay-ng", "--fakeauth", "0", "-a", bssid, "-e", essid, interface]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        return process

    async def arp_replay(
        self,
        interface: str,
        bssid: str,
    ) -> subprocess.Popen:
        """ARP replay attack (for WEP)"""
        cmd = ["aireplay-ng", "--arpreplay", "-b", bssid, interface]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        self._processes[f"arp_{bssid}"] = process
        return process

    async def verify_handshake(self, capture_file: str, bssid: str) -> bool:
        """Verify WPA handshake in capture file"""
        if not os.path.exists(capture_file):
            return False
        
        cmd = ["aircrack-ng", capture_file, "-b", bssid]
        
        result = await self._run_command(cmd)
        
        # Check for handshake in output
        return "1 handshake" in result.lower() or "handshake" in result.lower()

    async def crack_wep(
        self,
        capture_file: str,
        bssid: str,
    ) -> Optional[str]:
        """Attempt to crack WEP key"""
        cmd = ["aircrack-ng", capture_file, "-b", bssid]
        
        result = await self._run_command(cmd, timeout=300)
        
        # Parse key from output
        match = re.search(r"KEY FOUND! \[ ([\dA-F:]+) \]", result)
        if match:
            return match.group(1)
        
        return None

    async def parse_csv_output(self, csv_file: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse airodump-ng CSV output"""
        if not os.path.exists(csv_file):
            return [], []
        
        networks = []
        clients = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Split by station marker
            parts = content.split("Station MAC,")
            
            if len(parts) >= 1:
                # Parse networks (APs)
                network_lines = parts[0].strip().split('\n')[2:]  # Skip headers
                for line in network_lines:
                    if not line.strip():
                        continue
                    fields = [f.strip() for f in line.split(',')]
                    if len(fields) >= 14:
                        networks.append({
                            'bssid': fields[0],
                            'first_seen': fields[1],
                            'last_seen': fields[2],
                            'channel': fields[3],
                            'speed': fields[4],
                            'privacy': fields[5],
                            'cipher': fields[6],
                            'authentication': fields[7],
                            'power': fields[8],
                            'beacons': fields[9],
                            'ivs': fields[10],
                            'lan_ip': fields[11],
                            'id_length': fields[12],
                            'essid': fields[13],
                        })
            
            if len(parts) >= 2:
                # Parse clients
                client_lines = parts[1].strip().split('\n')[1:]  # Skip header
                for line in client_lines:
                    if not line.strip():
                        continue
                    fields = [f.strip() for f in line.split(',')]
                    if len(fields) >= 6:
                        clients.append({
                            'station_mac': fields[0],
                            'first_seen': fields[1],
                            'last_seen': fields[2],
                            'power': fields[3],
                            'packets': fields[4],
                            'bssid': fields[5],
                            'probes': fields[6] if len(fields) > 6 else '',
                        })
        
        except Exception as e:
            print(f"Error parsing CSV: {e}")
        
        return networks, clients

    async def _stop_after_duration(self, process_key: str, duration: int) -> None:
        """Stop process after duration"""
        await asyncio.sleep(duration)
        if process_key in self._processes:
            process = self._processes[process_key]
            process.send_signal(signal.SIGTERM)
            await asyncio.sleep(1)
            if process.poll() is None:
                process.kill()
            del self._processes[process_key]

    async def _run_command(
        self,
        cmd: List[str],
        timeout: int = 30,
    ) -> str:
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
            
            output = stdout.decode('utf-8', errors='ignore')
            error = stderr.decode('utf-8', errors='ignore')
            
            return output + error
        
        except asyncio.TimeoutError:
            raise RuntimeError(f"Command timed out: {' '.join(cmd)}")
        except Exception as e:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}: {e}")

    async def cleanup(self) -> None:
        """Stop all running processes"""
        for key in list(self._processes.keys()):
            process = self._processes[key]
            try:
                process.send_signal(signal.SIGTERM)
                await asyncio.sleep(1)
                if process.poll() is None:
                    process.kill()
            except:
                pass
            del self._processes[key]
