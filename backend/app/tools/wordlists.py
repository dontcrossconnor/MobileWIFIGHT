"""Wordlist management - REAL implementation with automatic downloads"""
import asyncio
import os
import gzip
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import httpx


class WordlistManager:
    """Manage wordlists with automatic downloads"""
    
    # Real wordlist sources
    WORDLISTS = {
        "rockyou": {
            "name": "RockYou",
            "filename": "rockyou.txt",
            "url": "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt",
            "size": "139 MB",
            "passwords": "14,344,391",
            "description": "Most popular wordlist from RockYou breach",
        },
        "common-passwords": {
            "name": "Common Passwords",
            "filename": "common-passwords.txt",
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt",
            "size": "8 MB",
            "passwords": "1,000,000",
            "description": "Top 1 million most common passwords",
        },
        "darkweb2017": {
            "name": "DarkWeb 2017",
            "filename": "darkweb2017-top10000.txt",
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/darkweb2017-top10000.txt",
            "size": "80 KB",
            "passwords": "10,000",
            "description": "Top 10k passwords from dark web leaks 2017",
        },
        "wifi-default": {
            "name": "WiFi Default Passwords",
            "filename": "wifi-default.txt",
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/WiFi-WPA/wifi-default.txt",
            "size": "5 KB",
            "passwords": "~500",
            "description": "Common default WiFi passwords from routers",
        },
        "probable-v2-wpa": {
            "name": "Probable WPA",
            "filename": "probable-v2-wpa-top4800.txt",
            "url": "https://raw.githubusercontent.com/berzerk0/Probable-Wordlists/master/Real-Passwords/WPA-Length/Top4800-probable-v2-wpa-length.txt",
            "size": "44 KB",
            "passwords": "4,800",
            "description": "WPA-length passwords (8-63 chars)",
        },
        "john": {
            "name": "John the Ripper",
            "filename": "john.txt",
            "url": "https://raw.githubusercontent.com/openwall/john/bleeding-jumbo/run/password.lst",
            "size": "3.4 KB",
            "passwords": "3,559",
            "description": "Default John the Ripper wordlist",
        },
        "rockyou-top100k": {
            "name": "RockYou Top 100k",
            "filename": "rockyou-top100k.txt",
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Leaked-Databases/rockyou-75.txt",
            "size": "616 KB",
            "passwords": "100,000",
            "description": "Top 100k from RockYou (faster testing)",
        },
        "seasons": {
            "name": "Seasons",
            "filename": "seasons.txt",
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Honeypot-Captures/multiplesources-passwords-fabian-fingerle.de.txt",
            "size": "120 KB",
            "passwords": "~15,000",
            "description": "Season-based and common patterns",
        },
        "names": {
            "name": "Common Names",
            "filename": "names.txt",
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/Names/names.txt",
            "size": "1.8 MB",
            "passwords": "~10,000",
            "description": "Common first and last names",
        },
        "digits": {
            "name": "Numeric",
            "filename": "numeric-0-99999.txt",
            "url": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt",
            "size": "112 KB",
            "passwords": "10,000",
            "description": "Common numeric passwords",
        },
    }
    
    def __init__(self, wordlist_dir: str = "/usr/share/wordlists"):
        self.wordlist_dir = Path(wordlist_dir)
        self.wordlist_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_wordlist(self, wordlist_key: str, force: bool = False) -> str:
        """Download a specific wordlist"""
        if wordlist_key not in self.WORDLISTS:
            raise ValueError(f"Unknown wordlist: {wordlist_key}")
        
        wordlist = self.WORDLISTS[wordlist_key]
        filepath = self.wordlist_dir / wordlist["filename"]
        
        # Skip if already exists
        if filepath.exists() and not force:
            return str(filepath)
        
        print(f"Downloading {wordlist['name']}...")
        
        async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
            response = await client.get(wordlist["url"])
            response.raise_for_status()
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(response.content)
        
        # Check if it's gzipped and extract
        if filepath.name.endswith('.gz'):
            print(f"Extracting {wordlist['name']}...")
            extracted = filepath.with_suffix('')
            with gzip.open(filepath, 'rb') as f_in:
                with open(extracted, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            filepath.unlink()  # Remove .gz file
            filepath = extracted
        
        print(f"✓ Downloaded {wordlist['name']} to {filepath}")
        return str(filepath)
    
    async def download_all(self, force: bool = False) -> Dict[str, str]:
        """Download all wordlists"""
        results = {}
        
        for key in self.WORDLISTS.keys():
            try:
                path = await self.download_wordlist(key, force=force)
                results[key] = path
            except Exception as e:
                print(f"✗ Failed to download {key}: {e}")
                results[key] = None
        
        return results
    
    async def download_essentials(self) -> Dict[str, str]:
        """Download essential wordlists only"""
        essentials = ["rockyou", "common-passwords", "wifi-default", "probable-v2-wpa"]
        results = {}
        
        for key in essentials:
            try:
                path = await self.download_wordlist(key)
                results[key] = path
            except Exception as e:
                print(f"✗ Failed to download {key}: {e}")
                results[key] = None
        
        return results
    
    def list_available(self) -> List[Dict]:
        """List all available wordlists with status"""
        wordlists = []
        
        for key, info in self.WORDLISTS.items():
            filepath = self.wordlist_dir / info["filename"]
            
            wordlists.append({
                "key": key,
                "name": info["name"],
                "filename": info["filename"],
                "description": info["description"],
                "size": info["size"],
                "passwords": info["passwords"],
                "downloaded": filepath.exists(),
                "path": str(filepath) if filepath.exists() else None,
            })
        
        return wordlists
    
    def get_wordlist_path(self, wordlist_key: str) -> Optional[str]:
        """Get path to wordlist if downloaded"""
        if wordlist_key not in self.WORDLISTS:
            return None
        
        filepath = self.wordlist_dir / self.WORDLISTS[wordlist_key]["filename"]
        
        if filepath.exists():
            return str(filepath)
        
        return None
    
    def get_default_wordlist(self) -> str:
        """Get default wordlist (rockyou)"""
        # Try rockyou first
        rockyou = self.get_wordlist_path("rockyou")
        if rockyou:
            return rockyou
        
        # Try common-passwords
        common = self.get_wordlist_path("common-passwords")
        if common:
            return common
        
        # Fall back to any available
        for key in self.WORDLISTS.keys():
            path = self.get_wordlist_path(key)
            if path:
                return path
        
        # Nothing available
        raise RuntimeError("No wordlists available. Run download first.")
