"""CaptureService implementation - Handshake validation"""
from typing import Optional
import os

from app.services.interfaces import ICaptureService
from app.tools import AircrackNG, HCXTools


class CaptureService(ICaptureService):
    """Handshake capture and validation service - Full implementation"""

    def __init__(self):
        self.aircrack = AircrackNG()
        self.hcxtools = HCXTools()

    async def verify_handshake(self, capture_file: str, bssid: str) -> bool:
        """Verify 4-way handshake in capture file"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        # Use aircrack-ng to verify handshake
        return await self.aircrack.verify_handshake(capture_file, bssid)

    async def extract_pmkid(self, capture_file: str) -> Optional[str]:
        """Extract PMKID from capture"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        # Use hcxtools to extract PMKID
        return await self.hcxtools.extract_pmkid(capture_file)

    async def convert_capture(self, input_file: str, output_format: str) -> str:
        """Convert capture file format"""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Capture file not found: {input_file}")
        
        output_file = input_file.replace('.cap', f'.{output_format}').replace('.pcap', f'.{output_format}')
        
        if output_format == "22000":
            # Convert to hashcat 22000 format
            return await self.hcxtools.convert_to_22000(input_file, output_file)
        elif output_format == "hccapx":
            # Convert to hashcat hccapx format (legacy)
            return await self.hcxtools.convert_to_hccapx(input_file, output_file)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    async def get_capture_info(self, capture_file: str) -> dict:
        """Get capture file metadata"""
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"Capture file not found: {capture_file}")
        
        # Use hcxtools to get info
        return await self.hcxtools.get_capture_info(capture_file)
