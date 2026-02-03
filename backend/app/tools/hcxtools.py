"""HCXTools wrapper - Real implementation for PMKID and handshake conversion"""
import asyncio
import os
import re
from typing import Optional, List
from pathlib import Path


class HCXTools:
    """Wrapper for hcxtools suite"""

    def __init__(self):
        self._verify_installation()

    def _verify_installation(self) -> None:
        """Verify hcxtools is installed"""
        required_tools = ["hcxpcapngtool", "hcxpmkidtool"]
        missing = []
        
        for tool in required_tools:
            if not self._check_command(tool):
                missing.append(tool)
        
        if missing:
            raise RuntimeError(
                f"Missing hcxtools: {', '.join(missing)}. "
                "Install with: apt-get install hcxtools"
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

    async def extract_pmkid(self, capture_file: str, output_file: Optional[str] = None) -> Optional[str]:
        """Extract PMKID from capture file"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        if output_file is None:
            output_file = capture_file.replace('.pcap', '.22000').replace('.cap', '.22000')
        
        # Convert to hashcat 22000 format which includes PMKID
        cmd = ["hcxpcapngtool", "-o", output_file, capture_file]
        
        try:
            result = await self._run_command(cmd)
            
            # Check if PMKID was found
            if os.path.exists(output_file):
                # Read and check for PMKID entries
                with open(output_file, 'r') as f:
                    content = f.read()
                    # PMKID lines start with WPA*01* in hashcat 22000 format
                    pmkid_match = re.search(r'WPA\*01\*([a-f0-9]{32})', content)
                    if pmkid_match:
                        return pmkid_match.group(1)
            
            return None
        
        except Exception as e:
            raise RuntimeError(f"PMKID extraction failed: {e}")

    async def convert_to_22000(self, capture_file: str, output_file: Optional[str] = None) -> str:
        """Convert capture file to hashcat 22000 format"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        if output_file is None:
            output_file = capture_file.replace('.pcap', '.22000').replace('.cap', '.22000')
        
        cmd = ["hcxpcapngtool", "-o", output_file, capture_file, "--eapoltimeout=60000"]
        
        try:
            await self._run_command(cmd)
            
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                raise RuntimeError("No valid handshakes found in capture")
            
            return output_file
        
        except Exception as e:
            raise RuntimeError(f"Conversion to 22000 format failed: {e}")

    async def convert_to_hccapx(self, capture_file: str, output_file: Optional[str] = None) -> str:
        """Convert capture file to hashcat hccapx format (legacy)"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        # First convert to 22000, then to hccapx if needed
        # Note: hccapx is deprecated, 22000 is preferred
        if output_file is None:
            output_file = capture_file.replace('.pcap', '.hccapx').replace('.cap', '.hccapx')
        
        # For now, just use 22000 format as it's more modern
        return await self.convert_to_22000(capture_file, output_file.replace('.hccapx', '.22000'))

    async def get_capture_info(self, capture_file: str) -> dict:
        """Get information about capture file"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        # Convert and analyze
        temp_output = f"/tmp/hcx_info_{os.path.basename(capture_file)}.22000"
        
        cmd = ["hcxpcapngtool", "-o", temp_output, capture_file, "--eapoltimeout=60000"]
        
        try:
            result = await self._run_command(cmd)
            
            info = {
                'file': capture_file,
                'size': os.path.getsize(capture_file),
                'handshakes': 0,
                'pmkids': 0,
                'networks': [],
            }
            
            # Parse output for statistics
            if "EAPOL" in result:
                matches = re.findall(r'(\d+) EAPOL', result)
                if matches:
                    info['handshakes'] = int(matches[0])
            
            if "PMKID" in result:
                matches = re.findall(r'(\d+) PMKID', result)
                if matches:
                    info['pmkids'] = int(matches[0])
            
            # Parse converted file for network details
            if os.path.exists(temp_output):
                with open(temp_output, 'r') as f:
                    for line in f:
                        # Extract BSSID and ESSID from hashcat format
                        # Format: WPA*TYPE*PMKID*MAC_AP*MAC_CLIENT*ESSID_HEX...
                        parts = line.strip().split('*')
                        if len(parts) >= 5 and parts[0] == 'WPA':
                            bssid = ':'.join([parts[3][i:i+2] for i in range(0, 12, 2)])
                            # ESSID is hex-encoded in parts[5]
                            try:
                                essid_hex = parts[5] if len(parts) > 5 else ''
                                essid = bytes.fromhex(essid_hex).decode('utf-8', errors='ignore')
                            except:
                                essid = ''
                            
                            if bssid not in [n['bssid'] for n in info['networks']]:
                                info['networks'].append({
                                    'bssid': bssid,
                                    'essid': essid,
                                })
                
                # Cleanup temp file
                try:
                    os.remove(temp_output)
                except:
                    pass
            
            return info
        
        except Exception as e:
            raise RuntimeError(f"Failed to get capture info: {e}")

    async def filter_by_bssid(self, capture_file: str, bssid: str, output_file: str) -> str:
        """Filter capture file to only include specific BSSID"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        # hcxpcapngtool can filter by MAC
        mac_filter = bssid.replace(':', '').lower()
        
        cmd = [
            "hcxpcapngtool",
            "-o", output_file,
            capture_file,
            f"--filtermac={mac_filter}",
        ]
        
        try:
            await self._run_command(cmd)
            
            if not os.path.exists(output_file):
                raise RuntimeError(f"Failed to create filtered capture")
            
            return output_file
        
        except Exception as e:
            raise RuntimeError(f"Filtering failed: {e}")

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
