"""Network interface management wrapper - Real implementation"""
import asyncio
import re
import subprocess
from typing import List, Dict, Optional, Tuple


class NetworkManager:
    """Wrapper for network interface management tools"""

    async def get_interfaces(self) -> List[Dict]:
        """Get all wireless interfaces"""
        interfaces = []
        
        # Use iw dev to list wireless interfaces
        try:
            result = await self._run_command(["iw", "dev"])
            
            # Parse output
            current_interface = None
            for line in result.split('\n'):
                line = line.strip()
                
                if line.startswith('Interface'):
                    current_interface = line.split()[1]
                    interfaces.append({
                        'interface': current_interface,
                        'type': None,
                        'channel': None,
                        'mac': None,
                    })
                
                elif current_interface and 'type' in line.lower():
                    iface_type = line.split()[-1]
                    interfaces[-1]['type'] = iface_type
                
                elif current_interface and 'addr' in line.lower():
                    mac = line.split()[-1]
                    interfaces[-1]['mac'] = mac
        
        except Exception as e:
            # Fallback to iwconfig
            try:
                result = await self._run_command(["iwconfig"])
                # Parse iwconfig output
                for line in result.split('\n'):
                    if 'IEEE' in line or '802.11' in line:
                        iface = line.split()[0]
                        interfaces.append({
                            'interface': iface,
                            'type': 'managed',
                            'channel': None,
                            'mac': None,
                        })
            except:
                pass
        
        # Get additional info for each interface
        for iface in interfaces:
            try:
                iface['driver'] = await self._get_driver(iface['interface'])
                iface['chipset'] = await self._get_chipset(iface['interface'])
                iface['mac'] = iface['mac'] or await self._get_mac(iface['interface'])
            except:
                pass
        
        return interfaces

    async def get_interface_info(self, interface: str) -> Dict:
        """Get detailed information about interface"""
        info = {
            'interface': interface,
            'driver': await self._get_driver(interface),
            'chipset': await self._get_chipset(interface),
            'mac': await self._get_mac(interface),
            'mode': await self._get_mode(interface),
            'channel': await self._get_channel(interface),
            'tx_power': await self._get_tx_power(interface),
            'monitor_capable': await self._check_monitor_support(interface),
            'injection_capable': await self._check_injection_support(interface),
        }
        return info

    async def set_channel(self, interface: str, channel: int) -> None:
        """Set WiFi channel"""
        # Try iw first
        try:
            await self._run_command(["iw", "dev", interface, "set", "channel", str(channel)])
            return
        except:
            pass
        
        # Fallback to iwconfig
        try:
            await self._run_command(["iwconfig", interface, "channel", str(channel)])
        except Exception as e:
            raise RuntimeError(f"Failed to set channel: {e}")

    async def set_tx_power(self, interface: str, power_dbm: int) -> None:
        """Set transmission power in dBm"""
        # Convert dBm to mBm for iw (millidecibels)
        power_mbm = power_dbm * 100
        
        try:
            await self._run_command([
                "iw", "dev", interface, "set", "txpower", "fixed", str(power_mbm)
            ])
        except Exception as e:
            raise RuntimeError(f"Failed to set TX power: {e}")

    async def set_interface_up(self, interface: str) -> None:
        """Bring interface up"""
        await self._run_command(["ip", "link", "set", interface, "up"])

    async def set_interface_down(self, interface: str) -> None:
        """Bring interface down"""
        await self._run_command(["ip", "link", "set", interface, "down"])

    async def get_supported_channels(self, interface: str) -> Tuple[List[int], List[int]]:
        """Get supported channels (2.4GHz, 5GHz)"""
        channels_2ghz = []
        channels_5ghz = []
        
        try:
            result = await self._run_command(["iw", "phy"])
            
            in_frequencies = False
            for line in result.split('\n'):
                line = line.strip()
                
                if 'Frequencies:' in line:
                    in_frequencies = True
                    continue
                
                if in_frequencies:
                    if line.startswith('*'):
                        # Parse frequency line
                        match = re.search(r'\[(\d+)\]', line)
                        if match:
                            channel = int(match.group(1))
                            # Determine band by channel number
                            if 1 <= channel <= 14:
                                channels_2ghz.append(channel)
                            elif channel >= 32:
                                channels_5ghz.append(channel)
                    elif not line.startswith('*') and line:
                        in_frequencies = False
        except:
            # Default channels if detection fails
            channels_2ghz = list(range(1, 12))  # 1-11
            channels_5ghz = [36, 40, 44, 48, 149, 153, 157, 161, 165]
        
        return sorted(channels_2ghz), sorted(channels_5ghz)

    async def _get_driver(self, interface: str) -> str:
        """Get driver name"""
        try:
            result = await self._run_command(["readlink", f"/sys/class/net/{interface}/device/driver"])
            return result.split('/')[-1].strip()
        except:
            return "unknown"

    async def _get_chipset(self, interface: str) -> str:
        """Get chipset information"""
        try:
            # Try to get from lsusb for USB adapters
            result = await self._run_command(["lsusb"])
            
            # Common chipsets
            if "RTL8812AU" in result or "0bda:8812" in result:
                return "Realtek RTL8812AU"
            elif "RTL8814AU" in result or "0bda:8813" in result:
                return "Realtek RTL8814AU"
            elif "Atheros" in result or "ath" in result.lower():
                return "Atheros"
            elif "Ralink" in result or "148f:" in result:
                return "Ralink"
            
            # Try ethtool
            result = await self._run_command(["ethtool", "-i", interface])
            for line in result.split('\n'):
                if 'driver:' in line.lower():
                    return line.split(':')[1].strip()
        except:
            pass
        
        return "unknown"

    async def _get_mac(self, interface: str) -> str:
        """Get MAC address"""
        try:
            result = await self._run_command(["cat", f"/sys/class/net/{interface}/address"])
            return result.strip()
        except:
            try:
                result = await self._run_command(["ip", "link", "show", interface])
                match = re.search(r'link/ether ([0-9a-f:]{17})', result)
                if match:
                    return match.group(1)
            except:
                pass
        return "00:00:00:00:00:00"

    async def _get_mode(self, interface: str) -> str:
        """Get current mode (managed/monitor)"""
        try:
            result = await self._run_command(["iw", "dev", interface, "info"])
            if "type monitor" in result.lower():
                return "monitor"
            elif "type managed" in result.lower():
                return "managed"
        except:
            pass
        return "unknown"

    async def _get_channel(self, interface: str) -> Optional[int]:
        """Get current channel"""
        try:
            result = await self._run_command(["iw", "dev", interface, "info"])
            match = re.search(r'channel (\d+)', result)
            if match:
                return int(match.group(1))
        except:
            pass
        return None

    async def _get_tx_power(self, interface: str) -> int:
        """Get current TX power in dBm"""
        try:
            result = await self._run_command(["iw", "dev", interface, "info"])
            match = re.search(r'txpower ([\d.]+) dBm', result)
            if match:
                return int(float(match.group(1)))
        except:
            pass
        return 20  # Default

    async def _check_monitor_support(self, interface: str) -> bool:
        """Check if interface supports monitor mode"""
        try:
            result = await self._run_command(["iw", "phy"])
            return "monitor" in result.lower()
        except:
            return False

    async def _check_injection_support(self, interface: str) -> bool:
        """Check if interface supports packet injection"""
        # Most monitor-capable cards support injection
        # More sophisticated check could use aireplay-ng --test
        return await self._check_monitor_support(interface)

    async def _run_command(self, cmd: List[str], timeout: int = 10) -> str:
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
