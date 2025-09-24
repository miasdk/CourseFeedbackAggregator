import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = True
    canvas_token: str = os.getenv("CANVAS_API_TOKEN", "")
    canvas_base_url: str = os.getenv("CANVAS_BASE_URL", "")
    zoho_access_token: str = os.getenv("ZOHO_ACCESS_TOKEN", "")

    # Accept all the extra fields from .env file
    canvas_access_token: str = ""
    canvas_api_url: str = ""
    canvas_developer_key: str = ""
    canvas_account_id: str = ""
    zoho_client_id: str = ""
    zoho_client_secret: str = ""
    zoho_refresh_token: str = ""
    scope: str = ""
    api_domain: str = ""
    token_type: str = ""
    database_url: str = ""

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields

settings = Settings()