from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"timeout": 5, "command_timeout": 60, "server_settings": {"timezone": "UTC"}},
)
SessionLocal = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
