"""Adapter API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.models import Adapter, AdapterConfig
from app.services.adapter import AdapterService
from app.api.deps import get_adapter_service

router = APIRouter()


@router.post("/detect", response_model=List[Adapter])
async def detect_adapters(
    service: AdapterService = Depends(get_adapter_service)
):
    """Detect all available WiFi adapters"""
    try:
        return await service.detect_adapters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interface}", response_model=Adapter)
async def get_adapter(
    interface: str,
    service: AdapterService = Depends(get_adapter_service)
):
    """Get specific adapter information"""
    try:
        return await service.get_adapter(interface)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interface}/monitor-mode", response_model=Adapter)
async def set_monitor_mode(
    interface: str,
    enable: bool,
    service: AdapterService = Depends(get_adapter_service)
):
    """Enable or disable monitor mode"""
    try:
        return await service.set_monitor_mode(interface, enable)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interface}/channel")
async def set_channel(
    interface: str,
    channel: int,
    service: AdapterService = Depends(get_adapter_service)
):
    """Set WiFi channel"""
    try:
        await service.set_channel(interface, channel)
        return {"success": True, "message": f"Channel set to {channel}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interface}/tx-power")
async def set_tx_power(
    interface: str,
    power_dbm: int,
    service: AdapterService = Depends(get_adapter_service)
):
    """Set transmission power"""
    try:
        await service.set_tx_power(interface, power_dbm)
        return {"success": True, "message": f"TX power set to {power_dbm} dBm"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interface}/validate-alfa")
async def validate_alfa(
    interface: str,
    service: AdapterService = Depends(get_adapter_service)
):
    """Validate if adapter is Alfa AWUS036ACH"""
    try:
        is_valid = await service.validate_alfa_adapter(interface)
        return {
            "valid": is_valid,
            "message": "Alfa AWUS036ACH detected" if is_valid else "Not an Alfa AWUS036ACH adapter"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
