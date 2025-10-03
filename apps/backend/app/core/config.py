from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
    CANVAS_BASE_URL: str = "https://executiveeducation.instructure.com"
    CANVAS_API_TOKEN: str
    CANVAS_ACCOUNT_ID: int = 1  # Executive Education account ID
    CANVAS_API_TIMEOUT: int = 30
    CANVAS_RATE_LIMIT: int = 3
    CANVAS_PER_PAGE: int = 100  

    #Database Configuration 
    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 5  
    DB_MAX_OVERFLOW: int = 10

    # Application Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    API_TITLE: str = "Course Feedback Aggregator API"
    API_DESCRIPTION: str = "Intelligent course feedback prioritization system"
    CORS_ORIGINS: list[str] = ["*"]
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def canvas_headers(self) -> dict[str, str]: 
        """Canvas API headers"""
        return {
            "Authorization": f"Bearer {self.CANVAS_API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    @property
    def api_prefix(self) -> str: 
        """API prefix"""
        return f"/api/{self.API_VERSION}"
    
    @property
    def is_development(self) -> bool:
        """Check if development environment"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if production environment"""
        return self.ENVIRONMENT == "production"

    @property
    def async_database_url(self) -> Optional[str]:
        """
        Convert DATABASE_URL to async format (postgresql+asyncpg://).

        Neon provides DATABASE_URL as postgresql://, but async SQLAlchemy
        needs postgresql+asyncpg:// to use the asyncpg driver.

        Also removes psycopg2-specific SSL parameters and adds asyncpg equivalents.
        """
        if not self.DATABASE_URL:
            return None

        url = self.DATABASE_URL

        # Replace postgresql:// with postgresql+asyncpg://
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Remove psycopg2-specific parameters that asyncpg doesn't support
        # asyncpg uses `ssl` parameter instead of `sslmode`
        url = url.replace("sslmode=require&", "")
        url = url.replace("&sslmode=require", "")
        url = url.replace("sslmode=require", "")
        url = url.replace("channel_binding=require&", "")
        url = url.replace("&channel_binding=require", "")
        url = url.replace("channel_binding=require", "")

        # Clean up any trailing ? or &
        url = url.rstrip("?&")

        # Add asyncpg's ssl parameter for Neon (asyncpg uses `ssl` not `sslmode`)
        if "?" in url:
            url = url + "&ssl=require"
        else:
            url = url + "?ssl=require"

        return url


# Singleton pattern - create settings once, cache forever
@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings singleton.

    This function is decorated with @lru_cache() to ensure
    we only create Settings() once and reuse it everywhere.

    Usage in FastAPI:
        from fastapi import Depends

        @app.get("/courses")
        async def get_courses(settings: Settings = Depends(get_settings)):
            # settings automatically injected
            ...
    """
    return Settings()


# Module-level settings instance for convenience
settings = get_settings()


# Testing and validation
if __name__ == "__main__":
    """
    Test configuration loading.

    Run with: python -m app.core.config
    """
    print("\n" + "=" * 70)
    print("CONFIGURATION MODULE TEST")
    print("=" * 70 + "\n")

    try:
        config = get_settings()

        print("SUCCESS: Configuration loaded successfully!\n")

        # Canvas Configuration
        print("Canvas Configuration:")
        print(f"  Base URL: {config.CANVAS_BASE_URL}")
        token_preview = f"{'*' * 40}...{config.CANVAS_API_TOKEN[-8:]}"
        print(f"  API Token: {token_preview}")
        print(f"  Timeout: {config.CANVAS_API_TIMEOUT} seconds")
        print(f"  Rate Limit: {config.CANVAS_RATE_LIMIT} requests/second")
        print(f"  Per Page: {config.CANVAS_PER_PAGE} items")

        # Database Configuration
        print(f"\nDatabase Configuration:")
        if config.DATABASE_URL:
            # Mask password in connection string
            db_parts = config.DATABASE_URL.split("@")
            if len(db_parts) > 1:
                db_url_safe = f"***@{db_parts[-1]}"
            else:
                db_url_safe = "***"
            print(f"  URL: {db_url_safe}")
        else:
            print("  URL: Not configured")
        print(f"  Pool Size: {config.DB_POOL_SIZE}")
        print(f"  Max Overflow: {config.DB_MAX_OVERFLOW}")

        # Application Configuration
        print(f"\nApplication Configuration:")
        print(f"  Environment: {config.ENVIRONMENT}")
        print(f"  Debug Mode: {config.DEBUG}")
        print(f"  API Version: {config.API_VERSION}")
        print(f"  API Title: {config.API_TITLE}")
        print(f"  Log Level: {config.LOG_LEVEL}")

        # Computed Properties
        print(f"\nComputed Properties:")
        print(f"  API Prefix: {config.api_prefix}")
        print(f"  Is Development: {config.is_development}")
        print(f"  Is Production: {config.is_production}")
        print(f"  Canvas Headers: Authorization: Bearer ***{config.CANVAS_API_TOKEN[-8:]}")

        print("\n" + "=" * 70)
        print("SUCCESS: All configuration tests passed!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"ERROR: Configuration failed to load\n")
        print(f"Details: {e}\n")
        print("Troubleshooting:")
        print("  1. Create .env file in apps/backend/ directory")
        print("  2. Add: CANVAS_API_TOKEN=your_token_here")
        print("  3. Add: DATABASE_URL=postgresql+asyncpg://user:pass@host/db")
        print("  4. Ensure all required variables are set")
        print("\n" + "=" * 70 + "\n")
        raise
