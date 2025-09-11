import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Find the .env file in the backend root directory
backend_root = Path(__file__).parent.parent.parent  # Go up to apps/backend/
env_file = backend_root / ".env"

class Settings(BaseSettings):
    # Database - From .env file
    database_url: Optional[str] = None
    
    # Canvas API - From existing .env
    canvas_access_token: Optional[str] = None
    canvas_api_url: str = "https://executiveeducation.instructure.com"
    canvas_base_url: str = "https://executiveeducation.instructure.com"
    canvas_developer_key: Optional[str] = None  
    canvas_account_id: Optional[str] = None
    
    # Zoho API - From existing .env
    zoho_client_id: Optional[str] = None
    zoho_client_secret: Optional[str] = None
    zoho_access_token: Optional[str] = None
    zoho_refresh_token: Optional[str] = None
    scope: Optional[str] = None
    api_domain: str = "https://www.zohoapis.com"
    zoho_api_domain: str = "https://www.zohoapis.com"
    token_type: Optional[str] = None
    
    # Application Settings
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    @property
    def canvas_token(self) -> Optional[str]:
        """Alias for canvas_access_token"""
        return self.canvas_access_token
    
    model_config = {
        "env_file": str(env_file),
        "case_sensitive": False,
        "extra": "allow"
    }

# Global settings instance
settings = Settings()