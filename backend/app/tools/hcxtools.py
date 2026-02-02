"""hcxtools wrapper"""
from typing import Optional


class HCXTools:
    """Wrapper for hcxtools"""

    async def extract_pmkid(self, capture_file: str) -> Optional[str]:
        """Extract PMKID from capture. Returns path to .22000 file or None."""
        import asyncio
        output = capture_file.rsplit(".", 1)[0] + ".22000"
        proc = await asyncio.create_subprocess_exec(
            "hcxpcapngtool", "-o", output, capture_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        return output if proc.returncode == 0 else None

    async def convert_to_22000(self, capture_file: str, output: str) -> str:
        """Convert capture to hashcat 22000 format."""
        import asyncio
        proc = await asyncio.create_subprocess_exec(
            "hcxpcapngtool", "-o", output, capture_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("hcxpcapngtool failed")
        return output
