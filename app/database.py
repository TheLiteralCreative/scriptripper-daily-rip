from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.settings import settings

# Managed Postgres (Neon) requires TLS. asyncpg takes SSL via connect_args, not
# the libpq ?sslmode= query param (which database_async_url strips). If a future
# local Postgres without SSL is used (no sslmode in the URL), pass no ssl arg.
_connect_args = {"ssl": True} if "sslmode" in settings.DATABASE_URL else {}

engine = create_async_engine(
    settings.database_async_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
