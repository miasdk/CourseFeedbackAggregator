import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database - From .env file
    database_url: str = os.getenv("DATABASE_URL")
    
    # Canvas API - From existing .env
    canvas_token: str = os.getenv("CANVAS_ACCESS_TOKEN")
    canvas_base_url: str = os.getenv("CANVAS_API_URL", "https://executiveeducation.instructure.com")
    canvas_account_id: str = os.getenv("CANVAS_ACCOUNT_ID")
    
    # Zoho API - From existing .env
    zoho_access_token: str = os.getenv("ZOHO_ACCESS_TOKEN")
    zoho_refresh_token: str = os.getenv("ZOHO_REFRESH_TOKEN") 
    zoho_client_id: str = os.getenv("ZOHO_CLIENT_ID")
    zoho_client_secret: str = os.getenv("ZOHO_CLIENT_SECRET")
    zoho_api_domain: str = os.getenv("API_DOMAIN", "https://www.zohoapis.com")
    
    # Application Settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()