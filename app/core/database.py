from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
import ssl
from .config import settings

# Railway gives postgresql:// but asyncpg needs postgresql+asyncpg://
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

if database_url.startswith("postgresql+asyncpg"):
    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "timeout": 5,
        "command_timeout": 10,
        "server_settings": {"jit": "off"},
    }
    if "supabase.com" in database_url:
        connect_args["ssl"] = ssl.create_default_context()
elif database_url.startswith("postgresql+psycopg"):
    connect_args = {
        "prepare_threshold": None,
    }
else:
    connect_args = {}

engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
Base = declarative_base()
_db_connection_logged = False


async def get_db():
    global _db_connection_logged
    async with AsyncSessionLocal() as session:
        try:
            if not _db_connection_logged:
                await session.execute(text("SELECT 1"))
                print("Database connection successful")
                _db_connection_logged = True
            yield session
        finally:
            await session.close()