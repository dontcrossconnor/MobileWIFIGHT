"""Wordlist API endpoints"""
from typing import List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.tools.wordlists import WordlistManager

router = APIRouter()

wordlist_manager = WordlistManager()


class WordlistInfo(BaseModel):
    key: str
    name: str
    filename: str
    description: str
    size: str
    passwords: str
    downloaded: bool
    path: str | None


@router.get("", response_model=List[WordlistInfo])
async def list_wordlists():
    """List all available wordlists"""
    return wordlist_manager.list_available()


@router.post("/download/{wordlist_key}")
async def download_wordlist(wordlist_key: str, force: bool = False):
    """Download a specific wordlist"""
    try:
        path = await wordlist_manager.download_wordlist(wordlist_key, force=force)
        return {
            "success": True,
            "wordlist": wordlist_key,
            "path": path,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download-all")
async def download_all_wordlists(force: bool = False):
    """Download all wordlists"""
    try:
        results = await wordlist_manager.download_all(force=force)
        success_count = sum(1 for v in results.values() if v)
        return {
            "success": True,
            "downloaded": success_count,
            "total": len(results),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download-essentials")
async def download_essentials():
    """Download essential wordlists only"""
    try:
        results = await wordlist_manager.download_essentials()
        success_count = sum(1 for v in results.values() if v)
        return {
            "success": True,
            "downloaded": success_count,
            "total": len(results),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/default")
async def get_default_wordlist():
    """Get default wordlist path"""
    try:
        path = wordlist_manager.get_default_wordlist()
        return {
            "path": path,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
