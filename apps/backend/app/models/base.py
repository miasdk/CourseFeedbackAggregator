"""Base model class and database configuration."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from ..config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Convert postgresql:// to postgresql+asyncpg:// for async support
if settings.database_url:
    if settings.database_url.startswith("postgresql://"):
        # Parse the URL and rebuild without sslmode parameters
        from urllib.parse import urlparse, parse_qs, urlunparse
        parsed = urlparse(settings.database_url)
        
        # Build asyncpg compatible URL
        database_url = f"postgresql+asyncpg://{parsed.netloc}{parsed.path}"
        
        # Add non-SSL query parameters if any (asyncpg handles SSL differently)
        if parsed.query:
            # Filter out SSL parameters that asyncpg doesn't support as query parameters
            excluded_params = {'sslmode', 'channel_binding', 'sslrootcert', 'sslcert', 'sslkey'}
            query_params = parse_qs(parsed.query)
            filtered_params = {k: v for k, v in query_params.items() if k not in excluded_params}
            
            if filtered_params:
                import urllib.parse
                query_string = urllib.parse.urlencode(filtered_params, doseq=True)
                database_url += f"?{query_string}"
    else:
        database_url = settings.database_url
else:
    database_url = "sqlite+aiosqlite:///./feedback.db"  # Fallback to SQLite

# Async database engine and session  
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300     # Recycle connections every 5 minutes
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_db():
    """Dependency for getting database session."""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()