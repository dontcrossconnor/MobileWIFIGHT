"""Attack API endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.models import Attack, AttackConfig
from app.services.attack import AttackService
from app.api.deps import get_attack_service

router = APIRouter()


@router.post("", response_model=Attack)
async def create_attack(
    config: AttackConfig,
    service: AttackService = Depends(get_attack_service)
):
    """Create and queue attack"""
    try:
        return await service.create_attack(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{attack_id}", response_model=Attack)
async def get_attack(
    attack_id: UUID,
    service: AttackService = Depends(get_attack_service)
):
    """Get attack details"""
    try:
        return await service.get_attack(attack_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{attack_id}/start", response_model=Attack)
async def start_attack(
    attack_id: UUID,
    service: AttackService = Depends(get_attack_service)
):
    """Start queued attack"""
    try:
        return await service.start_attack(attack_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{attack_id}", response_model=Attack)
async def stop_attack(
    attack_id: UUID,
    service: AttackService = Depends(get_attack_service)
):
    """Stop running attack"""
    try:
        return await service.stop_attack(attack_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Attack])
async def get_active_attacks(
    service: AttackService = Depends(get_attack_service)
):
    """Get all active attacks"""
    try:
        return await service.get_active_attacks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
