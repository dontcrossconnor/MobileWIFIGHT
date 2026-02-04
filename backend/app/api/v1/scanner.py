"""Scanner API endpoints"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.models import ScanSession, ScanConfig, Network, Client
from app.services.scanner import ScannerService
from app.api.deps import get_scanner_service

router = APIRouter()


@router.post("", response_model=ScanSession)
async def start_scan(
    config: ScanConfig,
    service: ScannerService = Depends(get_scanner_service)
):
    """Start network scan"""
    try:
        return await service.start_scan(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def stop_scan(
    session_id: UUID,
    service: ScannerService = Depends(get_scanner_service)
):
    """Stop active scan"""
    try:
        await service.stop_scan(session_id)
        return {"success": True, "message": "Scan stopped"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=ScanSession)
async def get_session(
    session_id: UUID,
    service: ScannerService = Depends(get_scanner_service)
):
    """Get scan session details"""
    try:
        return await service.get_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/networks", response_model=List[Network])
async def get_networks(
    session_id: UUID,
    service: ScannerService = Depends(get_scanner_service)
):
    """Get discovered networks"""
    try:
        return await service.get_networks(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/networks/{bssid}", response_model=Network)
async def get_network(
    session_id: UUID,
    bssid: str,
    service: ScannerService = Depends(get_scanner_service)
):
    """Get specific network details"""
    try:
        return await service.get_network(session_id, bssid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/clients", response_model=List[Client])
async def get_clients(
    session_id: UUID,
    bssid: Optional[str] = None,
    service: ScannerService = Depends(get_scanner_service)
):
    """Get clients (optionally filtered by BSSID)"""
    try:
        return await service.get_clients(session_id, bssid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
