"""ScannerService implementation - Real network discovery"""
import asyncio
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4
from pathlib import Path
import os

from app.services.interfaces import IScannerService
from app.models import (
    ScanSession,
    ScanConfig,
    ScanStatus,
    Network,
    Client,
    EncryptionType,
    CipherType,
    AuthenticationType,
)
from app.tools import AircrackNG


class ScannerService(IScannerService):
    """Network scanning service - Full implementation"""

    def __init__(self):
        self.aircrack = AircrackNG()
        self._sessions: Dict[UUID, ScanSession] = {}
        self._networks: Dict[UUID, List[Network]] = {}
        self._clients: Dict[UUID, List[Client]] = {}
        self._scan_tasks: Dict[UUID, asyncio.Task] = {}

    async def start_scan(self, config: ScanConfig) -> ScanSession:
        """Start network scan"""
        # Validate interface is in monitor mode
        # This would be checked by adapter service in production
        
        # Create session
        session_id = uuid4()
        session = ScanSession(
            id=session_id,
            config=config,
            status=ScanStatus.STARTING,
            networks_found=0,
            clients_found=0,
            handshakes_captured=0,
            packets_captured=0,
            started_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        self._sessions[session_id] = session
        self._networks[session_id] = []
        self._clients[session_id] = []
        
        # Start capture
        output_prefix = config.capture_file or f"/tmp/scan_{session_id}"
        
        # Determine channel
        channel = config.channels[0] if config.channels and len(config.channels) == 1 else None
        
        # Start airodump-ng
        try:
            await self.aircrack.start_capture(
                interface=config.interface,
                output_prefix=output_prefix,
                channel=channel,
            )
            
            # Update status
            session.status = ScanStatus.RUNNING
            self._sessions[session_id] = session
            
            # Start background task to parse results
            task = asyncio.create_task(self._scan_loop(session_id, output_prefix))
            self._scan_tasks[session_id] = task
            
        except Exception as e:
            session.status = ScanStatus.ERROR
            self._sessions[session_id] = session
            raise RuntimeError(f"Failed to start scan: {e}")
        
        return session

    async def stop_scan(self, session_id: UUID) -> None:
        """Stop active scan"""
        if session_id not in self._sessions:
            raise ValueError(f"Scan session not found: {session_id}")
        
        session = self._sessions[session_id]
        
        # Stop capture
        await self.aircrack.stop_capture(session.config.interface)
        
        # Cancel background task
        if session_id in self._scan_tasks:
            self._scan_tasks[session_id].cancel()
            try:
                await self._scan_tasks[session_id]
            except asyncio.CancelledError:
                pass
            del self._scan_tasks[session_id]
        
        # Update session
        session.status = ScanStatus.STOPPED
        session.updated_at = datetime.now()
        self._sessions[session_id] = session

    async def get_session(self, session_id: UUID) -> ScanSession:
        """Get scan session details"""
        if session_id not in self._sessions:
            raise ValueError(f"Scan session not found: {session_id}")
        
        return self._sessions[session_id]

    async def get_networks(self, session_id: UUID) -> List[Network]:
        """Get discovered networks"""
        if session_id not in self._sessions:
            raise ValueError(f"Scan session not found: {session_id}")
        
        return self._networks.get(session_id, [])

    async def get_network(self, session_id: UUID, bssid: str) -> Network:
        """Get specific network details"""
        networks = await self.get_networks(session_id)
        
        for network in networks:
            if network.bssid.lower() == bssid.lower():
                return network
        
        raise ValueError(f"Network not found: {bssid}")

    async def get_clients(
        self, session_id: UUID, bssid: Optional[str] = None
    ) -> List[Client]:
        """Get clients (optionally filtered by BSSID)"""
        if session_id not in self._sessions:
            raise ValueError(f"Scan session not found: {session_id}")
        
        clients = self._clients.get(session_id, [])
        
        if bssid:
            return [c for c in clients if c.bssid.lower() == bssid.lower()]
        
        return clients

    async def _scan_loop(self, session_id: UUID, output_prefix: str) -> None:
        """Background task to parse scan results"""
        csv_file = f"{output_prefix}-01.csv"
        
        while True:
            try:
                await asyncio.sleep(3)  # Update every 3 seconds
                
                # Check if CSV file exists
                if not os.path.exists(csv_file):
                    continue
                
                # Parse CSV
                networks_data, clients_data = await self.aircrack.parse_csv_output(csv_file)
                
                # Update networks
                networks = []
                for net_data in networks_data:
                    try:
                        network = self._parse_network(net_data)
                        networks.append(network)
                    except Exception as e:
                        print(f"Error parsing network: {e}")
                        continue
                
                self._networks[session_id] = networks
                
                # Update clients
                clients = []
                for client_data in clients_data:
                    try:
                        client = self._parse_client(client_data)
                        clients.append(client)
                    except Exception as e:
                        print(f"Error parsing client: {e}")
                        continue
                
                self._clients[session_id] = clients
                
                # Update session stats
                session = self._sessions[session_id]
                session.networks_found = len(networks)
                session.clients_found = len(clients)
                session.updated_at = datetime.now()
                
                # Check for handshakes
                cap_file = f"{output_prefix}-01.cap"
                if os.path.exists(cap_file):
                    handshake_count = 0
                    for network in networks:
                        try:
                            if await self.aircrack.verify_handshake(cap_file, network.bssid):
                                handshake_count += 1
                        except:
                            pass
                    session.handshakes_captured = handshake_count
                
                self._sessions[session_id] = session
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in scan loop: {e}")
                continue

    def _parse_network(self, data: dict) -> Network:
        """Parse network data from airodump-ng CSV"""
        # Parse encryption
        privacy = data.get('privacy', '').upper()
        cipher = data.get('cipher', '').upper()
        auth = data.get('authentication', '').upper()
        
        # Determine encryption type
        if 'WPA3' in privacy or 'SAE' in auth:
            encryption = EncryptionType.WPA3
        elif 'WPA2' in privacy:
            encryption = EncryptionType.WPA2
        elif 'WPA' in privacy:
            if 'WPA2' in privacy:
                encryption = EncryptionType.WPA_WPA2
            else:
                encryption = EncryptionType.WPA
        elif 'WEP' in privacy:
            encryption = EncryptionType.WEP
        elif 'OPN' in privacy or not privacy:
            encryption = EncryptionType.OPEN
        else:
            encryption = EncryptionType.OPEN
        
        # Determine cipher
        if 'CCMP' in cipher:
            cipher_type = CipherType.CCMP
        elif 'TKIP' in cipher:
            cipher_type = CipherType.TKIP
        elif 'WEP' in cipher:
            cipher_type = CipherType.WEP
        else:
            cipher_type = CipherType.NONE
        
        # Determine authentication
        if 'PSK' in auth:
            auth_type = AuthenticationType.PSK
        elif 'MGT' in auth or 'EAP' in auth:
            auth_type = AuthenticationType.MGT
        elif 'SAE' in auth:
            auth_type = AuthenticationType.SAE
        else:
            auth_type = AuthenticationType.OPEN
        
        # Parse channel
        try:
            channel = int(data.get('channel', 0))
        except:
            channel = 0
        
        # Calculate frequency from channel
        if 1 <= channel <= 13:
            frequency = 2407 + (channel * 5)
        elif channel == 14:
            frequency = 2484
        elif channel >= 32:
            frequency = 5000 + (channel * 5)
        else:
            frequency = 2437  # Default to channel 6
        
        # Parse signal
        try:
            power = int(data.get('power', '-70'))
            if power > 0:
                power = -power  # Ensure negative
        except:
            power = -70
        
        # Parse beacons
        try:
            beacons = int(data.get('beacons', '0'))
        except:
            beacons = 0
        
        now = datetime.now()
        
        return Network(
            bssid=data.get('bssid', '00:00:00:00:00:00'),
            essid=data.get('essid', '').strip(),
            channel=channel,
            frequency=frequency,
            signal=power,
            encryption=encryption,
            cipher=cipher_type,
            authentication=auth_type,
            wps=False,  # Would need separate WPS detection
            wps_locked=False,
            clients=[],
            handshake_captured=False,
            pmkid_captured=False,
            beacon_count=beacons,
            data_packets=0,
            first_seen=now,
            last_seen=now,
            manufacturer=None,
        )

    def _parse_client(self, data: dict) -> Client:
        """Parse client data from airodump-ng CSV"""
        # Parse signal
        try:
            power = int(data.get('power', '-70'))
            if power > 0:
                power = -power
        except:
            power = -70
        
        # Parse packets
        try:
            packets = int(data.get('packets', '0'))
        except:
            packets = 0
        
        # Parse probes
        probes_str = data.get('probes', '')
        probes = [p.strip() for p in probes_str.split(',') if p.strip()]
        
        now = datetime.now()
        
        return Client(
            mac=data.get('station_mac', '00:00:00:00:00:00'),
            bssid=data.get('bssid', '00:00:00:00:00:00'),
            probes=probes,
            signal=power,
            packets=packets,
            first_seen=now,
            last_seen=now,
            manufacturer=None,
        )
