#!/usr/bin/env python3
"""Standalone wordlist downloader"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.tools.wordlists import WordlistManager


async def main():
    """Download wordlists"""
    print("=" * 60)
    print("WiFi Pentester - Wordlist Downloader")
    print("=" * 60)
    print()
    
    manager = WordlistManager("/usr/share/wordlists")
    
    # List available
    print("Available Wordlists:")
    print()
    
    available = manager.list_available()
    for wl in available:
        status = "✓ Downloaded" if wl["downloaded"] else "  Not downloaded"
        print(f"{status} - {wl['name']}")
        print(f"           {wl['description']}")
        print(f"           Size: {wl['size']}, Passwords: {wl['passwords']}")
        print()
    
    # Ask what to download
    print()
    print("Options:")
    print("  1) Download essentials (RockYou, Common, WiFi, WPA)")
    print("  2) Download all wordlists")
    print("  3) Exit")
    print()
    
    choice = input("Choose option [1]: ").strip() or "1"
    
    if choice == "1":
        print("\nDownloading essential wordlists...")
        results = await manager.download_essentials()
        success = sum(1 for v in results.values() if v)
        print(f"\n✓ Downloaded {success}/{len(results)} wordlists")
    
    elif choice == "2":
        print("\nDownloading all wordlists...")
        results = await manager.download_all()
        success = sum(1 for v in results.values() if v)
        print(f"\n✓ Downloaded {success}/{len(results)} wordlists")
    
    elif choice == "3":
        print("Exiting...")
        return
    
    else:
        print("Invalid option")
        return
    
    print()
    print("=" * 60)
    print("Wordlists ready at: /usr/share/wordlists")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
