"""API v1 routes"""
from fastapi import APIRouter

from . import adapter, scanner, attacks, cracking, captures, reports, wordlists

api_router = APIRouter()

api_router.include_router(adapter.router, prefix="/adapter", tags=["adapter"])
api_router.include_router(scanner.router, prefix="/scan", tags=["scanner"])
api_router.include_router(attacks.router, prefix="/attacks", tags=["attacks"])
api_router.include_router(cracking.router, prefix="/cracking", tags=["cracking"])
api_router.include_router(captures.router, prefix="/captures", tags=["captures"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(wordlists.router, prefix="/wordlists", tags=["wordlists"])
