from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings management using Pydantic Settings
    Automatically loads from environment variables
    """

    # Database Configuration
    database_url: Optional[str] = None

    # Canvas LMS Configuration
    canvas_api_token: str = "15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY"
    canvas_base_url: str = "https://executiveeducation.instructure.com"
    canvas_api_version: str = "v1"
    canvas_rate_limit_requests: int = 3000  # Canvas default: 3000 requests/hour
    canvas_rate_limit_window: int = 3600    # 1 hour in seconds

    # Zoho Configuration (for webhook validation)
    zoho_client_id: Optional[str] = "1000.LFJC5W9CC2VV5A0VBHZBI8HFY0OWYH"
    zoho_client_secret: Optional[str] = None
    zoho_refresh_token: Optional[str] = None

    # Application Configuration
    debug: bool = False
    log_level: str = "INFO"

    # API Configuration
    api_title: str = "Course Feedback Aggregator API"
    api_version: str = "1.0.0"
    api_description: str = "Intelligent course feedback prioritization system"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def canvas_api_base_url(self) -> str:
        """Complete Canvas API base URL"""
        return f"{self.canvas_base_url}/api/{self.canvas_api_version}"

    @property
    def canvas_headers(self) -> dict:
        """Standard headers for Canvas API requests"""
        return {
            "Authorization": f"Bearer {self.canvas_api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }


# Global settings instance
settings = Settings()