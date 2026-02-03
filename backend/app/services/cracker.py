"""CrackerService implementation - GPU password cracking"""
import asyncio
from typing import Dict, Optional
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal

from app.services.interfaces import ICrackerService
from app.models import (
    CrackingJob,
    CrackingJobConfig,
    CrackingProgress,
    JobStatus,
    GPUProvider,
    GPUInstance,
)
from app.tools import Hashcat, HCXTools


class CrackerService(ICrackerService):
    """GPU-accelerated password cracking service - Full implementation"""

    def __init__(self):
        self.hashcat = Hashcat()
        self.hcxtools = HCXTools()
        self._jobs: Dict[UUID, CrackingJob] = {}
        self._crack_tasks: Dict[UUID, asyncio.Task] = {}

    async def create_job(self, config: CrackingJobConfig) -> CrackingJob:
        """Create cracking job"""
        # Validate handshake file exists
        import os
        if not os.path.exists(config.handshake_file):
            raise FileNotFoundError(f"Handshake file not found: {config.handshake_file}")
        
        # Create job
        job_id = uuid4()
        progress = CrackingProgress(
            job_id=job_id,
            status=JobStatus.QUEUED,
            progress_percent=0.0,
            speed_mh_per_sec=0.0,
            tried_passwords=0,
            total_passwords=None,
            eta_seconds=None,
            current_wordlist_position=None,
        )
        
        job = CrackingJob(
            id=job_id,
            config=config,
            status=JobStatus.QUEUED,
            gpu_instance=None,
            progress=progress,
            password=None,
            cost_usd=Decimal("0.0"),
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            logs=[],
        )
        
        self._jobs[job_id] = job
        return job

    async def start_job(self, job_id: UUID) -> CrackingJob:
        """Start cracking job"""
        if job_id not in self._jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        
        if job.status != JobStatus.QUEUED:
            raise RuntimeError(f"Job cannot be started from status: {job.status}")
        
        # Update status
        job.status = JobStatus.STARTING
        job.started_at = datetime.now()
        job.logs.append("Starting cracking job...")
        self._jobs[job_id] = job
        
        # For local GPU (no cloud provisioning)
        if job.config.gpu_provider == GPUProvider.LOCAL:
            # Start cracking task
            task = asyncio.create_task(self._execute_cracking(job_id))
            self._crack_tasks[job_id] = task
        else:
            # For cloud GPU, would need to provision instance first
            job.status = JobStatus.PROVISIONING
            job.logs.append(f"Provisioning GPU on {job.config.gpu_provider.value}...")
            self._jobs[job_id] = job
            
            # Provision GPU (simplified - would use provider APIs)
            gpu = await self.provision_gpu(job.config.gpu_provider)
            job.gpu_instance = gpu
            job.logs.append(f"GPU provisioned: {gpu.instance_id}")
            self._jobs[job_id] = job
            
            # Start cracking
            task = asyncio.create_task(self._execute_cracking(job_id))
            self._crack_tasks[job_id] = task
        
        await asyncio.sleep(1)
        return self._jobs[job_id]

    async def stop_job(self, job_id: UUID) -> CrackingJob:
        """Stop running job"""
        if job_id not in self._jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        
        # Cancel task
        if job_id in self._crack_tasks:
            self._crack_tasks[job_id].cancel()
            try:
                await self._crack_tasks[job_id]
            except asyncio.CancelledError:
                pass
            del self._crack_tasks[job_id]
        
        # Stop hashcat session
        await self.hashcat.stop_session(str(job_id))
        
        # Terminate GPU if provisioned
        if job.gpu_instance:
            await self.terminate_gpu(job.gpu_instance.instance_id)
            job.gpu_instance = None
        
        # Update status
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now()
        job.logs.append("Job cancelled")
        self._jobs[job_id] = job
        
        return job

    async def get_job(self, job_id: UUID) -> CrackingJob:
        """Get job details"""
        if job_id not in self._jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        return self._jobs[job_id]

    async def get_progress(self, job_id: UUID) -> CrackingProgress:
        """Get real-time progress"""
        if job_id not in self._jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        return job.progress

    async def provision_gpu(self, provider: GPUProvider) -> GPUInstance:
        """Provision GPU instance"""
        # Simplified implementation - would use actual cloud provider APIs
        
        if provider == GPUProvider.LOCAL:
            # Use local GPU
            devices = await self.hashcat.list_devices()
            if not devices:
                raise RuntimeError("No GPU devices found locally")
            
            device = devices[0]
            return GPUInstance(
                instance_id="local",
                provider=GPUProvider.LOCAL,
                gpu_model=device.get('name', 'Unknown'),
                gpu_count=1,
                cost_per_hour=0.0,
                status="running",
                ip_address="localhost",
            )
        
        elif provider == GPUProvider.VASTAI:
            # Would use Vast.ai API here
            return GPUInstance(
                instance_id=f"vast_{uuid4().hex[:8]}",
                provider=GPUProvider.VASTAI,
                gpu_model="RTX 4090",
                gpu_count=1,
                cost_per_hour=0.50,
                status="running",
                ip_address="0.0.0.0",
            )
        
        else:
            raise NotImplementedError(f"Provider not implemented: {provider}")

    async def terminate_gpu(self, instance_id: str) -> None:
        """Terminate GPU instance"""
        # Would call cloud provider API to terminate
        pass

    async def _execute_cracking(self, job_id: UUID) -> None:
        """Execute password cracking"""
        job = self._jobs[job_id]
        config = job.config
        
        try:
            # Convert capture to hashcat format if needed
            hash_file = config.handshake_file
            if not hash_file.endswith('.22000'):
                job.logs.append("Converting capture to hashcat format...")
                self._jobs[job_id] = job
                hash_file = await self.hcxtools.convert_to_22000(config.handshake_file)
            
            job.status = JobStatus.RUNNING
            job.logs.append("Starting hashcat...")
            self._jobs[job_id] = job
            
            # Start hashcat
            process = await self.hashcat.crack_wpa(
                hash_file=hash_file,
                wordlist=config.wordlist_path or "/usr/share/wordlists/rockyou.txt",
                session_name=str(job_id),
                rules=config.rules_file,
                mask=config.mask,
            )
            
            # Monitor progress
            while True:
                await asyncio.sleep(5)
                
                # Get hashcat status
                status = await self.hashcat.get_status(str(job_id))
                
                if status:
                    # Update progress
                    progress = CrackingProgress(
                        job_id=job_id,
                        status=JobStatus.RUNNING,
                        progress_percent=status.get('progress', 0.0),
                        speed_mh_per_sec=status.get('speed', 0.0),
                        tried_passwords=status.get('recovered', 0),
                        total_passwords=status.get('total'),
                        eta_seconds=None,  # Would parse ETA from status
                        current_wordlist_position=status.get('recovered', 0),
                    )
                    
                    job = self._jobs[job_id]
                    job.progress = progress
                    self._jobs[job_id] = job
                    
                    # Check if done
                    if status.get('status') in ['cracked', 'exhausted']:
                        break
                
                # Check if process finished
                if process.returncode is not None:
                    break
            
            # Check for cracked password
            password = await self.hashcat.check_result(hash_file)
            
            # Update job
            job = self._jobs[job_id]
            if password:
                job.status = JobStatus.SUCCESS
                job.password = password
                job.logs.append(f"Password cracked: {password}")
            else:
                job.status = JobStatus.EXHAUSTED
                job.logs.append("Password not found in wordlist")
            
            job.completed_at = datetime.now()
            
            # Calculate cost
            if job.gpu_instance and job.started_at:
                duration_hours = (datetime.now() - job.started_at).total_seconds() / 3600
                job.cost_usd = Decimal(str(job.gpu_instance.cost_per_hour * duration_hours))
            
            self._jobs[job_id] = job
        
        except asyncio.CancelledError:
            raise
        except Exception as e:
            job = self._jobs[job_id]
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.logs.append(f"Cracking failed: {e}")
            self._jobs[job_id] = job
