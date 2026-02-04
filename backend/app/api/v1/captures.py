"""Capture API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.capture import CaptureService
from app.api.deps import get_capture_service

router = APIRouter()


class VerifyRequest(BaseModel):
    file: str
    bssid: str


class ConvertRequest(BaseModel):
    file: str
    format: str


@router.post("/verify")
async def verify_handshake(
    request: VerifyRequest,
    service: CaptureService = Depends(get_capture_service)
):
    """Verify handshake in capture file"""
    try:
        valid = await service.verify_handshake(request.file, request.bssid)
        return {
            "valid": valid,
            "message": "Valid handshake found" if valid else "No valid handshake"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-pmkid")
async def extract_pmkid(
    file: str,
    service: CaptureService = Depends(get_capture_service)
):
    """Extract PMKID from capture"""
    try:
        pmkid = await service.extract_pmkid(file)
        return {
            "pmkid": pmkid,
            "found": pmkid is not None
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/convert")
async def convert_capture(
    request: ConvertRequest,
    service: CaptureService = Depends(get_capture_service)
):
    """Convert capture file format"""
    try:
        output_file = await service.convert_capture(request.file, request.format)
        return {
            "output_file": output_file,
            "format": request.format
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file}/info")
async def get_capture_info(
    file: str,
    service: CaptureService = Depends(get_capture_service)
):
    """Get capture file information"""
    try:
        return await service.get_capture_info(file)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
