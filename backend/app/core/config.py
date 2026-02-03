"""Application configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "WiFi Penetration Testing Platform API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Capture Storage
    capture_dir: str = "/tmp/wifi-pentester/captures"
    
    # Wordlists
    wordlist_dir: str = "/usr/share/wordlists"
    default_wordlist: str = "rockyou.txt"
    
    # Cloud GPU Providers
    vastai_api_key: str = ""
    lambda_api_key: str = ""
    runpod_api_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
