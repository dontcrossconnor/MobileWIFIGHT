"""Cracking API endpoints"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.models import CrackingJob, CrackingJobConfig, CrackingProgress
from app.services.cracker import CrackerService
from app.api.deps import get_cracker_service

router = APIRouter()


@router.post("/jobs", response_model=CrackingJob)
async def create_job(
    config: CrackingJobConfig,
    service: CrackerService = Depends(get_cracker_service)
):
    """Create cracking job"""
    try:
        return await service.create_job(config)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=CrackingJob)
async def get_job(
    job_id: UUID,
    service: CrackerService = Depends(get_cracker_service)
):
    """Get job details"""
    try:
        return await service.get_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/start", response_model=CrackingJob)
async def start_job(
    job_id: UUID,
    service: CrackerService = Depends(get_cracker_service)
):
    """Start cracking job"""
    try:
        return await service.start_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/jobs/{job_id}", response_model=CrackingJob)
async def stop_job(
    job_id: UUID,
    service: CrackerService = Depends(get_cracker_service)
):
    """Stop running job"""
    try:
        return await service.stop_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}/progress", response_model=CrackingProgress)
async def get_progress(
    job_id: UUID,
    service: CrackerService = Depends(get_cracker_service)
):
    """Get real-time progress"""
    try:
        return await service.get_progress(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
