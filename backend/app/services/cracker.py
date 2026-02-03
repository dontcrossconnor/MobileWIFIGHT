"""CrackerService implementation - GPU password cracking"""
import asyncio
from typing import Dict, Optional
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal
import os

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
from app.tools.vastai import VastAI
from app.tools.wordlists import WordlistManager
from app.core.config import settings
import asyncio


class CrackerService(ICrackerService):
    """GPU-accelerated password cracking service - Full implementation"""

    def __init__(self):
        self.hashcat = Hashcat()
        self.hcxtools = HCXTools()
        self.wordlists = WordlistManager(settings.wordlist_dir)
        self._jobs: Dict[UUID, CrackingJob] = {}
        self._crack_tasks: Dict[UUID, asyncio.Task] = {}
        
        # Cloud provider clients
        self.vastai = VastAI(settings.vastai_api_key) if settings.vastai_api_key else None

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
        """Provision GPU instance - REAL implementation"""
        
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
            # REAL Vast.ai API integration
            if not self.vastai:
                raise RuntimeError("Vast.ai API key not configured")
            
            # Search for best GPU offer
            offers = await self.vastai.search_offers(
                min_gpu_ram=8,
                max_price=2.0,
            )
            
            if not offers:
                raise RuntimeError("No suitable GPU instances available on Vast.ai")
            
            # Select cheapest offer
            best_offer = offers[0]
            
            # Create instance
            result = await self.vastai.create_instance(
                offer_id=best_offer["id"],
                image="nvidia/cuda:12.0.0-runtime-ubuntu22.04",
                disk_size=10,
            )
            
            instance_id = result.get("new_contract")
            
            # Wait for instance to be ready
            await asyncio.sleep(30)  # Give it time to boot
            
            # Get instance details
            instance_info = await self.vastai.get_instance(instance_id)
            
            # Install hashcat on instance
            await self.vastai.execute_command(
                instance_id,
                "apt-get update && apt-get install -y hashcat"
            )
            
            return GPUInstance(
                instance_id=str(instance_id),
                provider=GPUProvider.VASTAI,
                gpu_model=best_offer.get("gpu_name", "Unknown"),
                gpu_count=best_offer.get("num_gpus", 1),
                cost_per_hour=best_offer.get("dph_total", 0.0),
                status="running",
                ip_address=instance_info.get("ssh_host", ""),
            )
        
        else:
            raise NotImplementedError(f"Provider not implemented: {provider}")

    async def terminate_gpu(self, instance_id: str) -> None:
        """Terminate GPU instance - REAL implementation"""
        if instance_id == "local":
            return  # Nothing to terminate for local
        
        # Vast.ai termination
        if self.vastai:
            try:
                await self.vastai.destroy_instance(int(instance_id))
            except Exception as e:
                print(f"Error terminating instance: {e}")

    async def _execute_cracking(self, job_id: UUID) -> None:
        """Execute password cracking - REAL implementation"""
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
            
            # If using cloud GPU, execute remotely
            if job.gpu_instance and job.gpu_instance.instance_id != "local":
                await self._execute_remote_cracking(job_id, hash_file)
                return
            
            # Local execution
            # Get wordlist - use configured or default
            wordlist_path = config.wordlist_path
            if not wordlist_path:
                try:
                    wordlist_path = self.wordlists.get_default_wordlist()
                except RuntimeError:
                    # No wordlists available, download essentials
                    job.logs.append("No wordlists found, downloading essentials...")
                    self._jobs[job_id] = job
                    await self.wordlists.download_essentials()
                    wordlist_path = self.wordlists.get_default_wordlist()
            
            process = await self.hashcat.crack_wpa(
                hash_file=hash_file,
                wordlist=wordlist_path,
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

    async def _execute_remote_cracking(self, job_id: UUID, hash_file: str) -> None:
        """Execute cracking on remote GPU - REAL implementation"""
        job = self._jobs[job_id]
        instance = job.gpu_instance
        
        try:
            # Upload hash file
            job.logs.append("Uploading hash file to GPU instance...")
            self._jobs[job_id] = job
            
            remote_hash = f"/root/hash_{job_id}.22000"
            await self.vastai.upload_file(
                int(instance.instance_id),
                hash_file,
                remote_hash,
            )
            
            # Prepare wordlist on remote
            wordlist_path = job.config.wordlist_path or self.wordlists.get_default_wordlist()
            remote_wordlist = "/root/wordlist.txt"
            
            job.logs.append("Preparing wordlist on GPU instance...")
            self._jobs[job_id] = job
            
            # Download wordlist directly on remote for speed
            await self.vastai.execute_command(
                int(instance.instance_id),
                "apt-get update && apt-get install -y hashcat wget && "
                "wget -O /root/wordlist.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
            )
            
            # Start hashcat on remote
            job.logs.append("Starting remote hashcat...")
            self._jobs[job_id] = job
            
            hashcat_cmd = f"hashcat -m 22000 {remote_hash} {remote_wordlist} -o /root/result.txt --potfile-disable --status --status-timer 5 --force"
            
            # Start in background
            await self.vastai.execute_command(
                int(instance.instance_id),
                f"nohup {hashcat_cmd} > /root/hashcat.log 2>&1 &"
            )
            
            await asyncio.sleep(5)
            
            # Monitor progress
            attempts = 0
            max_attempts = job.config.timeout_minutes * 6
            
            while attempts < max_attempts:
                await asyncio.sleep(10)
                attempts += 1
                
                # Check for password
                result_cmd = await self.vastai.execute_command(
                    int(instance.instance_id),
                    "cat /root/result.txt 2>/dev/null || echo ''"
                )
                
                if result_cmd.strip():
                    # Password found!
                    password = result_cmd.strip().split(':')[0] if ':' in result_cmd else result_cmd.strip()
                    
                    job = self._jobs[job_id]
                    job.status = JobStatus.SUCCESS
                    job.password = password
                    job.logs.append(f"✓ Password cracked: {password}")
                    job.completed_at = datetime.now()
                    
                    if job.started_at and instance:
                        duration_hours = (datetime.now() - job.started_at).total_seconds() / 3600
                        job.cost_usd = Decimal(str(instance.cost_per_hour * duration_hours))
                    
                    self._jobs[job_id] = job
                    return
                
                # Check status
                status_output = await self.vastai.execute_command(
                    int(instance.instance_id),
                    "tail -50 /root/hashcat.log 2>/dev/null || echo ''"
                )
                
                if "Exhausted" in status_output:
                    job = self._jobs[job_id]
                    job.status = JobStatus.EXHAUSTED
                    job.logs.append("Wordlist exhausted - password not found")
                    job.completed_at = datetime.now()
                    
                    if job.started_at and instance:
                        duration_hours = (datetime.now() - job.started_at).total_seconds() / 3600
                        job.cost_usd = Decimal(str(instance.cost_per_hour * duration_hours))
                    
                    self._jobs[job_id] = job
                    return
                
                # Update progress
                import re
                speed_match = re.search(r'Speed\.+:\s*([\d.]+)\s*([kMG]?H/s)', status_output)
                speed_value = 0.0
                
                if speed_match:
                    speed_value = float(speed_match.group(1))
                    speed_unit = speed_match.group(2)
                    
                    if 'GH/s' in speed_unit:
                        speed_value *= 1000
                    elif 'kH/s' in speed_unit:
                        speed_value /= 1000
                    elif 'H/s' in speed_unit:
                        speed_value /= 1000000
                
                job = self._jobs[job_id]
                progress = CrackingProgress(
                    job_id=job_id,
                    status=JobStatus.RUNNING,
                    progress_percent=min(90.0, attempts * 2),
                    speed_mh_per_sec=speed_value,
                    tried_passwords=0,
                    total_passwords=None,
                    eta_seconds=None,
                )
                job.progress = progress
                self._jobs[job_id] = job
            
            # Timeout
            job = self._jobs[job_id]
            job.status = JobStatus.FAILED
            job.logs.append("Job timed out")
            job.completed_at = datetime.now()
            
            if job.started_at and instance:
                duration_hours = (datetime.now() - job.started_at).total_seconds() / 3600
                job.cost_usd = Decimal(str(instance.cost_per_hour * duration_hours))
            
            self._jobs[job_id] = job
        
        except Exception as e:
            job = self._jobs[job_id]
            job.status = JobStatus.FAILED
            job.logs.append(f"Remote execution failed: {e}")
            job.completed_at = datetime.now()
            self._jobs[job_id] = job
        
        finally:
            # Terminate GPU
            if instance and instance.instance_id != "local":
                try:
                    await self.terminate_gpu(instance.instance_id)
                except:
                    pass
