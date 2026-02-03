"""Vast.ai API integration - REAL implementation"""
import asyncio
import httpx
from typing import Optional, List, Dict
import json


class VastAI:
    """Real Vast.ai API client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://console.vast.ai/api/v0"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def search_offers(
        self,
        min_gpu_ram: int = 8,
        gpu_name: Optional[str] = None,
        max_price: float = 2.0,
    ) -> List[Dict]:
        """Search for available GPU instances"""
        async with httpx.AsyncClient() as client:
            params = {
                "verified": "true",
                "external": "false",
                "rentable": "true",
                "gpu_ram": f">={min_gpu_ram}",
                "order": "dph_total",  # Sort by price
                "type": "on-demand",
            }
            
            if gpu_name:
                params["gpu_name"] = gpu_name
            
            response = await client.get(
                f"{self.base_url}/bundles",
                headers=self.headers,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            
            offers = response.json()
            
            # Filter by max price
            filtered = [
                o for o in offers.get("offers", [])
                if o.get("dph_total", 999) <= max_price
            ]
            
            return filtered[:10]  # Top 10 cheapest
    
    async def create_instance(
        self,
        offer_id: int,
        image: str = "nvidia/cuda:12.0.0-runtime-ubuntu22.04",
        disk_size: int = 10,
    ) -> Dict:
        """Rent a GPU instance"""
        async with httpx.AsyncClient() as client:
            payload = {
                "client_id": "me",
                "image": image,
                "disk": disk_size,
                "onstart": "echo 'Instance started'",
            }
            
            response = await client.put(
                f"{self.base_url}/asks/{offer_id}",
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            
            result = response.json()
            return result
    
    async def get_instance(self, instance_id: int) -> Dict:
        """Get instance details"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instances",
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            
            instances = response.json().get("instances", [])
            for inst in instances:
                if inst.get("id") == instance_id:
                    return inst
            
            raise ValueError(f"Instance {instance_id} not found")
    
    async def destroy_instance(self, instance_id: int) -> None:
        """Destroy/stop instance"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/instances/{instance_id}",
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
    
    async def execute_command(
        self,
        instance_id: int,
        command: str,
    ) -> str:
        """Execute command on instance via SSH"""
        # Get instance SSH details
        instance = await self.get_instance(instance_id)
        
        ssh_host = instance.get("ssh_host")
        ssh_port = instance.get("ssh_port")
        
        if not ssh_host or not ssh_port:
            raise RuntimeError("Instance SSH not ready")
        
        # Execute via SSH
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-p", str(ssh_port),
            f"root@{ssh_host}",
            command,
        ]
        
        process = await asyncio.create_subprocess_exec(
            *ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        return stdout.decode() + stderr.decode()
    
    async def upload_file(
        self,
        instance_id: int,
        local_path: str,
        remote_path: str,
    ) -> None:
        """Upload file to instance via SCP"""
        instance = await self.get_instance(instance_id)
        
        ssh_host = instance.get("ssh_host")
        ssh_port = instance.get("ssh_port")
        
        scp_cmd = [
            "scp",
            "-o", "StrictHostKeyChecking=no",
            "-P", str(ssh_port),
            local_path,
            f"root@{ssh_host}:{remote_path}",
        ]
        
        process = await asyncio.create_subprocess_exec(
            *scp_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"SCP upload failed: {local_path}")
    
    async def download_file(
        self,
        instance_id: int,
        remote_path: str,
        local_path: str,
    ) -> None:
        """Download file from instance via SCP"""
        instance = await self.get_instance(instance_id)
        
        ssh_host = instance.get("ssh_host")
        ssh_port = instance.get("ssh_port")
        
        scp_cmd = [
            "scp",
            "-o", "StrictHostKeyChecking=no",
            "-P", str(ssh_port),
            f"root@{ssh_host}:{remote_path}",
            local_path,
        ]
        
        process = await asyncio.create_subprocess_exec(
            *scp_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"SCP download failed: {remote_path}")
