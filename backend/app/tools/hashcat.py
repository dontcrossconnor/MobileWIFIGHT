"""Hashcat wrapper - Real implementation for GPU password cracking"""
import asyncio
import os
import re
import signal
from typing import Optional, Dict, List
from pathlib import Path


class Hashcat:
    """Wrapper for hashcat GPU password cracking"""

    def __init__(self):
        self._processes: Dict[str, asyncio.subprocess.Process] = {}
        self._verify_installation()

    def _verify_installation(self) -> None:
        """Verify hashcat is installed"""
        if not self._check_command("hashcat"):
            raise RuntimeError(
                "Hashcat not installed. "
                "Install with: apt-get install hashcat"
            )

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

    async def crack_wpa(
        self,
        hash_file: str,
        wordlist: str,
        session_name: str,
        rules: Optional[str] = None,
        mask: Optional[str] = None,
    ) -> asyncio.subprocess.Process:
        """Start WPA/WPA2 password cracking"""
        if not os.path.exists(hash_file):
            raise FileNotFoundError(f"Hash file not found: {hash_file}")
        
        if mask is None and not os.path.exists(wordlist):
            raise FileNotFoundError(f"Wordlist not found: {wordlist}")
        
        # Mode 22000 for WPA-PBKDF2-PMKID+EAPOL
        cmd = [
            "hashcat",
            "-m", "22000",  # WPA/WPA2 mode
            hash_file,
            "-o", f"{hash_file}.cracked",
            "--outfile-format", "2",  # plain:hash format
            "--session", session_name,
            "--status",
            "--status-timer", "5",  # Status update every 5 seconds
            "--potfile-disable",  # Don't use potfile to avoid conflicts
        ]
        
        # Add attack mode based on parameters
        if mask:
            # Mask attack
            cmd.extend(["-a", "3", mask])
        elif rules:
            # Wordlist with rules
            cmd.extend(["-a", "0", wordlist, "-r", rules])
        else:
            # Straight wordlist attack
            cmd.extend(["-a", "0", wordlist])
        
        # Start hashcat
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        self._processes[session_name] = process
        return process

    async def get_status(self, session_name: str) -> Optional[Dict]:
        """Get cracking session status"""
        # Use hashcat restore to get status
        cmd = ["hashcat", "--session", session_name, "--status"]
        
        try:
            result = await self._run_command(cmd, timeout=5)
            
            # Parse status output
            status = {
                'session': session_name,
                'status': 'unknown',
                'progress': 0.0,
                'speed': 0.0,
                'recovered': 0,
                'total': 0,
                'eta': None,
            }
            
            # Parse various fields
            if "Status.........: Running" in result:
                status['status'] = 'running'
            elif "Status.........: Exhausted" in result:
                status['status'] = 'exhausted'
            elif "Status.........: Cracked" in result:
                status['status'] = 'cracked'
            
            # Parse progress
            progress_match = re.search(r'Progress\.*:\s*(\d+)/(\d+)', result)
            if progress_match:
                current = int(progress_match.group(1))
                total = int(progress_match.group(2))
                status['recovered'] = current
                status['total'] = total
                if total > 0:
                    status['progress'] = (current / total) * 100
            
            # Parse speed (H/s, kH/s, MH/s)
            speed_match = re.search(r'Speed\.+:\s*([\d.]+)\s*([kMG]?H/s)', result)
            if speed_match:
                speed_value = float(speed_match.group(1))
                speed_unit = speed_match.group(2)
                
                # Convert to MH/s
                if 'GH/s' in speed_unit:
                    speed_value *= 1000
                elif 'kH/s' in speed_unit:
                    speed_value /= 1000
                elif 'H/s' in speed_unit:
                    speed_value /= 1000000
                
                status['speed'] = speed_value
            
            # Parse ETA
            eta_match = re.search(r'Time\.Estimated\.*:\s*(.+)', result)
            if eta_match:
                status['eta'] = eta_match.group(1).strip()
            
            # Parse recovered passwords
            recovered_match = re.search(r'Recovered\.*:\s*(\d+)/(\d+)', result)
            if recovered_match:
                status['recovered'] = int(recovered_match.group(1))
            
            return status
        
        except Exception as e:
            return None

    async def check_result(self, hash_file: str) -> Optional[str]:
        """Check if password was cracked"""
        output_file = f"{hash_file}.cracked"
        
        if not os.path.exists(output_file):
            return None
        
        try:
            with open(output_file, 'r') as f:
                content = f.read().strip()
                if content:
                    # Format is plain:hash, extract plain password
                    if ':' in content:
                        return content.split(':')[0]
                    return content
        except:
            pass
        
        return None

    async def stop_session(self, session_name: str) -> None:
        """Stop cracking session"""
        if session_name in self._processes:
            process = self._processes[session_name]
            try:
                process.send_signal(signal.SIGTERM)
                await asyncio.sleep(2)
                if process.returncode is None:
                    process.kill()
            except:
                pass
            del self._processes[session_name]
        
        # Also try to stop via checkpoint
        try:
            cmd = ["hashcat", "--session", session_name, "--quit"]
            await self._run_command(cmd, timeout=5)
        except:
            pass

    async def restore_session(self, session_name: str) -> asyncio.subprocess.Process:
        """Restore a previous session"""
        cmd = ["hashcat", "--session", session_name, "--restore"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        self._processes[session_name] = process
        return process

    async def benchmark(self, mode: int = 22000) -> Dict:
        """Run hashcat benchmark for specific mode"""
        cmd = ["hashcat", "-b", "-m", str(mode)]
        
        try:
            result = await self._run_command(cmd, timeout=60)
            
            # Parse benchmark results
            speed_match = re.search(r'Speed\.+:\s*([\d.]+)\s*([kMG]?H/s)', result)
            if speed_match:
                speed_value = float(speed_match.group(1))
                speed_unit = speed_match.group(2)
                
                # Convert to MH/s
                if 'GH/s' in speed_unit:
                    speed_value *= 1000
                elif 'kH/s' in speed_unit:
                    speed_value /= 1000
                elif 'H/s' in speed_unit:
                    speed_value /= 1000000
                
                return {
                    'mode': mode,
                    'speed_mhs': speed_value,
                    'unit': 'MH/s',
                }
        except:
            pass
        
        return {'mode': mode, 'speed_mhs': 0, 'unit': 'MH/s'}

    async def list_devices(self) -> List[Dict]:
        """List available GPUs/devices"""
        cmd = ["hashcat", "-I"]
        
        try:
            result = await self._run_command(cmd, timeout=10)
            
            devices = []
            current_device = None
            
            for line in result.split('\n'):
                line = line.strip()
                
                if line.startswith('Device ID #'):
                    device_id = line.split('#')[1].strip()
                    current_device = {'id': device_id}
                    devices.append(current_device)
                
                elif current_device:
                    if 'Name:' in line:
                        current_device['name'] = line.split('Name:')[1].strip()
                    elif 'Type:' in line:
                        current_device['type'] = line.split('Type:')[1].strip()
                    elif 'Global Memory:' in line:
                        current_device['memory'] = line.split('Memory:')[1].strip()
            
            return devices
        
        except Exception:
            return []

    async def _run_command(self, cmd: List[str], timeout: int = 30) -> str:
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
        for session_name in list(self._processes.keys()):
            await self.stop_session(session_name)
