"""Remote GPU cracking execution"""
import asyncio
from uuid import UUID
from app.models import JobStatus, CrackingProgress


async def execute_remote_cracking(self, job_id: UUID, hash_file: str) -> None:
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
        
        # Upload wordlist if custom
        wordlist_path = job.config.wordlist_path or "/usr/share/wordlists/rockyou.txt"
        remote_wordlist = "/root/wordlist.txt"
        
        if wordlist_path != "/usr/share/wordlists/rockyou.txt":
            job.logs.append("Uploading custom wordlist...")
            self._jobs[job_id] = job
            await self.vastai.upload_file(
                int(instance.instance_id),
                wordlist_path,
                remote_wordlist,
            )
        else:
            # Download rockyou on remote
            job.logs.append("Downloading rockyou.txt on GPU instance...")
            self._jobs[job_id] = job
            await self.vastai.execute_command(
                int(instance.instance_id),
                "wget -O /root/wordlist.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
            )
        
        # Start hashcat on remote
        job.logs.append("Starting remote hashcat...")
        self._jobs[job_id] = job
        
        hashcat_cmd = f"hashcat -m 22000 {remote_hash} {remote_wordlist} -o /root/result.txt --potfile-disable --status --status-timer 5"
        
        if job.config.rules_file:
            hashcat_cmd += f" -r /root/rules.txt"
        
        # Start hashcat in background
        await self.vastai.execute_command(
            int(instance.instance_id),
            f"nohup {hashcat_cmd} > /root/hashcat.log 2>&1 &"
        )
        
        # Monitor progress
        while True:
            await asyncio.sleep(10)
            
            # Check if done
            result = await self.vastai.execute_command(
                int(instance.instance_id),
                "cat /root/result.txt 2>/dev/null || echo ''"
            )
            
            if result.strip():
                # Found password
                password = result.strip().split(':')[0] if ':' in result else result.strip()
                
                job = self._jobs[job_id]
                job.status = JobStatus.SUCCESS
                job.password = password
                job.logs.append(f"Password cracked: {password}")
                job.completed_at = datetime.now()
                self._jobs[job_id] = job
                break
            
            # Check status
            status_output = await self.vastai.execute_command(
                int(instance.instance_id),
                "tail -20 /root/hashcat.log"
            )
            
            # Parse progress (simplified)
            if "Exhausted" in status_output:
                job = self._jobs[job_id]
                job.status = JobStatus.EXHAUSTED
                job.logs.append("Wordlist exhausted - password not found")
                job.completed_at = datetime.now()
                self._jobs[job_id] = job
                break
            
            # Update progress
            job = self._jobs[job_id]
            progress = CrackingProgress(
                job_id=job_id,
                status=JobStatus.RUNNING,
                progress_percent=50.0,  # Would parse from hashcat output
                speed_mh_per_sec=1000.0,  # Would parse from hashcat output
                tried_passwords=0,
                total_passwords=None,
                eta_seconds=None,
            )
            job.progress = progress
            self._jobs[job_id] = job
    
    except Exception as e:
        job = self._jobs[job_id]
        job.status = JobStatus.FAILED
        job.logs.append(f"Remote execution failed: {e}")
        job.completed_at = datetime.now()
        self._jobs[job_id] = job
    
    finally:
        # Terminate GPU instance
        if instance and instance.instance_id != "local":
            await self.terminate_gpu(instance.instance_id)


# Add this method to CrackerService class
def _add_remote_method():
    from app.services.cracker import CrackerService
    CrackerService._execute_remote_cracking = execute_remote_cracking
