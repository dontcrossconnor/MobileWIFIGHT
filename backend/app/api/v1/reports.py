"""Report API endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models import Report, ReportFormat, Network, Attack, CrackingJob
from app.services.report import ReportService
from app.api.deps import get_report_service

router = APIRouter()


class GenerateReportRequest(BaseModel):
    networks: List[Network]
    attacks: List[Attack]
    jobs: List[CrackingJob]
    format: ReportFormat


@router.post("", response_model=Report)
async def generate_report(
    request: GenerateReportRequest,
    service: ReportService = Depends(get_report_service)
):
    """Generate penetration test report"""
    try:
        return await service.generate_report(
            networks=request.networks,
            attacks=request.attacks,
            jobs=request.jobs,
            format=request.format,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: UUID,
    service: ReportService = Depends(get_report_service)
):
    """Get generated report"""
    try:
        return await service.get_report(report_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
