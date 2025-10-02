from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from .config import get_settings 

Base = declarative_base()

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_connection():
        """Test database connection"""
        print("\n" + "=" * 60)
        print("DATABASE CONNECTION TEST")
        print("=" * 60 + "\n")

        try:
            # Test connection
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"SUCCESS: Connected to Neon PostgreSQL")
                print(f"Version: {version[:50]}...\n")

            await engine.dispose()
            print("=" * 60)
            print("SUCCESS: Database test passed!")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"ERROR: {e}\n")
            print("Make sure DATABASE_URL is set in .env file")
            print("=" * 60 + "\n")
            raise

    asyncio.run(test_connection()) 