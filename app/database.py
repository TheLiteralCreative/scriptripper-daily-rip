from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.settings import settings

engine = create_async_engine(
    settings.database_async_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
