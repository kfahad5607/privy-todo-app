from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

# Create async engine for SQLAlchemy
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# DB Session dependency
async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Helper function to initialize database tables
async def init_db():
    """Initialize all defined database tables if they don't exist"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Helper function to close database connection
async def close_db():
    """Close database connection"""
    await engine.dispose()