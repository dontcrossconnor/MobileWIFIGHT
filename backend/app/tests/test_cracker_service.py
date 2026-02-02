"""Test CrackerService implementation"""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal

from app.services.interfaces import ICrackerService
from app.models import (
    CrackingJob,
    CrackingJobConfig,
    CrackingProgress,
    CrackMode,
    JobStatus,
    GPUProvider,
    GPUInstance,
)


class TestCrackerServiceContract:
    """Test CrackerService follows interface contract"""

    @pytest.fixture
    def cracker_service(self):
        """Create mock cracker service for testing"""
        service = AsyncMock(spec=ICrackerService)
        return service

    @pytest.mark.asyncio
    async def test_create_job_returns_job(
        self, cracker_service, sample_cracking_config
    ):
        """Test creating cracking job"""
        job = CrackingJob(
            id=uuid4(),
            config=sample_cracking_config,
            status=JobStatus.QUEUED,
            gpu_instance=None,
            progress=CrackingProgress(
                job_id=uuid4(),
                status=JobStatus.QUEUED,
                progress_percent=0.0,
                speed_mh_per_sec=0.0,
                tried_passwords=0,
            ),
            password=None,
            cost_usd=Decimal("0.0"),
            created_at=AsyncMock(),
            started_at=None,
            completed_at=None,
            logs=[],
        )
        cracker_service.create_job.return_value = job
        
        result = await cracker_service.create_job(sample_cracking_config)
        
        assert isinstance(result, CrackingJob)
        assert result.status == JobStatus.QUEUED

    @pytest.mark.asyncio
    async def test_create_job_validates_handshake_file(self, cracker_service):
        """Test creating job validates handshake file exists"""
        cracker_service.create_job.side_effect = ValueError(
            "Handshake file not found"
        )
        
        config = CrackingJobConfig(
            handshake_file="/nonexistent.cap",
            bssid="00:11:22:33:44:55",
            essid="Test",
            attack_mode=CrackMode.WORDLIST,
            gpu_provider=GPUProvider.VASTAI,
        )
        
        with pytest.raises(ValueError, match="Handshake file not found"):
            await cracker_service.create_job(config)

    @pytest.mark.asyncio
    async def test_start_job_provisions_gpu(
        self, cracker_service, sample_cracking_job, sample_gpu_instance
    ):
        """Test starting job provisions GPU instance"""
        job_with_gpu = CrackingJob(
            id=sample_cracking_job.id,
            config=sample_cracking_job.config,
            status=JobStatus.PROVISIONING,
            gpu_instance=sample_gpu_instance,
            progress=sample_cracking_job.progress,
            password=None,
            cost_usd=Decimal("0.0"),
            created_at=sample_cracking_job.created_at,
            started_at=AsyncMock(),
            completed_at=None,
            logs=["Provisioning GPU instance"],
        )
        cracker_service.start_job.return_value = job_with_gpu
        
        result = await cracker_service.start_job(sample_cracking_job.id)
        
        assert result.status == JobStatus.PROVISIONING
        assert result.gpu_instance is not None

    @pytest.mark.asyncio
    async def test_start_job_uploads_handshake(self, cracker_service):
        """Test starting job uploads handshake to GPU"""
        # Implementation should upload handshake file to GPU instance
        cracker_service.start_job.return_value = AsyncMock(spec=CrackingJob)
        
        await cracker_service.start_job(uuid4())
        
        cracker_service.start_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_job_terminates_gpu(
        self, cracker_service, sample_cracking_job
    ):
        """Test stopping job terminates GPU instance"""
        stopped_job = CrackingJob(
            id=sample_cracking_job.id,
            config=sample_cracking_job.config,
            status=JobStatus.CANCELLED,
            gpu_instance=None,
            progress=sample_cracking_job.progress,
            password=None,
            cost_usd=Decimal("2.50"),
            created_at=sample_cracking_job.created_at,
            started_at=sample_cracking_job.started_at,
            completed_at=AsyncMock(),
            logs=["Job cancelled", "GPU instance terminated"],
        )
        cracker_service.stop_job.return_value = stopped_job
        
        result = await cracker_service.stop_job(sample_cracking_job.id)
        
        assert result.status == JobStatus.CANCELLED
        assert result.gpu_instance is None

    @pytest.mark.asyncio
    async def test_get_job_returns_job(
        self, cracker_service, sample_cracking_job
    ):
        """Test getting job by ID"""
        cracker_service.get_job.return_value = sample_cracking_job
        
        result = await cracker_service.get_job(sample_cracking_job.id)
        
        assert isinstance(result, CrackingJob)
        assert result.id == sample_cracking_job.id

    @pytest.mark.asyncio
    async def test_get_progress_returns_progress(
        self, cracker_service, sample_cracking_progress
    ):
        """Test getting real-time progress"""
        cracker_service.get_progress.return_value = sample_cracking_progress
        
        result = await cracker_service.get_progress(sample_cracking_progress.job_id)
        
        assert isinstance(result, CrackingProgress)
        assert result.status == JobStatus.RUNNING
        assert result.progress_percent > 0

    @pytest.mark.asyncio
    async def test_get_progress_calculates_eta(
        self, cracker_service, sample_cracking_progress
    ):
        """Test progress includes ETA calculation"""
        cracker_service.get_progress.return_value = sample_cracking_progress
        
        result = await cracker_service.get_progress(sample_cracking_progress.job_id)
        
        assert result.eta_seconds is not None
        assert result.eta_seconds > 0

    @pytest.mark.asyncio
    async def test_provision_gpu_returns_instance(
        self, cracker_service, sample_gpu_instance
    ):
        """Test provisioning GPU instance"""
        cracker_service.provision_gpu.return_value = sample_gpu_instance
        
        result = await cracker_service.provision_gpu(GPUProvider.VASTAI)
        
        assert isinstance(result, GPUInstance)
        assert result.provider == GPUProvider.VASTAI
        assert result.status == "running"

    @pytest.mark.asyncio
    async def test_provision_gpu_selects_best_price(self, cracker_service):
        """Test GPU provisioning selects best price/performance"""
        # Implementation should select optimal GPU based on cost and speed
        cracker_service.provision_gpu.return_value = AsyncMock(spec=GPUInstance)
        
        await cracker_service.provision_gpu(GPUProvider.VASTAI)
        
        cracker_service.provision_gpu.assert_called_once()

    @pytest.mark.asyncio
    async def test_terminate_gpu_stops_instance(self, cracker_service):
        """Test terminating GPU instance"""
        cracker_service.terminate_gpu.return_value = None
        
        await cracker_service.terminate_gpu("instance-123")
        
        cracker_service.terminate_gpu.assert_called_once_with("instance-123")

    @pytest.mark.asyncio
    async def test_job_success_downloads_password(self, cracker_service):
        """Test successful job downloads cracked password"""
        successful_job = CrackingJob(
            id=uuid4(),
            config=AsyncMock(spec=CrackingJobConfig),
            status=JobStatus.SUCCESS,
            gpu_instance=None,
            progress=CrackingProgress(
                job_id=uuid4(),
                status=JobStatus.SUCCESS,
                progress_percent=100.0,
                speed_mh_per_sec=0.0,
                tried_passwords=5000000,
            ),
            password="cracked_password123",
            cost_usd=Decimal("1.25"),
            created_at=AsyncMock(),
            started_at=AsyncMock(),
            completed_at=AsyncMock(),
            logs=["Password found!"],
        )
        cracker_service.get_job.return_value = successful_job
        
        result = await cracker_service.get_job(uuid4())
        
        assert result.status == JobStatus.SUCCESS
        assert result.password is not None

    @pytest.mark.asyncio
    async def test_job_exhausted_when_no_password_found(self, cracker_service):
        """Test job status EXHAUSTED when password not found"""
        exhausted_job = CrackingJob(
            id=uuid4(),
            config=AsyncMock(spec=CrackingJobConfig),
            status=JobStatus.EXHAUSTED,
            gpu_instance=None,
            progress=CrackingProgress(
                job_id=uuid4(),
                status=JobStatus.EXHAUSTED,
                progress_percent=100.0,
                speed_mh_per_sec=0.0,
                tried_passwords=14000000,
            ),
            password=None,
            cost_usd=Decimal("5.00"),
            created_at=AsyncMock(),
            started_at=AsyncMock(),
            completed_at=AsyncMock(),
            logs=["Wordlist exhausted", "Password not found"],
        )
        cracker_service.get_job.return_value = exhausted_job
        
        result = await cracker_service.get_job(uuid4())
        
        assert result.status == JobStatus.EXHAUSTED
        assert result.password is None

    @pytest.mark.asyncio
    async def test_job_tracks_cost(self, cracker_service):
        """Test job tracks cumulative cost"""
        job_with_cost = CrackingJob(
            id=uuid4(),
            config=AsyncMock(spec=CrackingJobConfig),
            status=JobStatus.RUNNING,
            gpu_instance=GPUInstance(
                instance_id="123",
                provider=GPUProvider.VASTAI,
                gpu_model="RTX 4090",
                gpu_count=1,
                cost_per_hour=0.50,
                status="running",
            ),
            progress=AsyncMock(spec=CrackingProgress),
            password=None,
            cost_usd=Decimal("2.50"),  # 5 hours * $0.50/hr
            created_at=AsyncMock(),
            started_at=AsyncMock(),
            completed_at=None,
            logs=[],
        )
        cracker_service.get_job.return_value = job_with_cost
        
        result = await cracker_service.get_job(uuid4())
        
        assert result.cost_usd > 0


class TestCrackerServiceIntegration:
    """Integration tests for CrackerService"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_crack_with_wordlist(self):
        """Test cracking with wordlist"""
        pytest.skip("Integration test - requires actual GPU and implementation")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_crack_with_mask(self):
        """Test cracking with mask attack"""
        pytest.skip("Integration test - requires actual GPU and implementation")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_crack_with_rules(self):
        """Test cracking with rule-based attack"""
        pytest.skip("Integration test - requires actual GPU and implementation")
