"""数据库连接"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import settings

# 异步引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 同步引擎（用于初始化表）
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    echo=settings.DEBUG,
    future=True,
)


def create_db_and_tables():
    """创建数据库和表"""
    SQLModel.metadata.create_all(sync_engine)


async def get_db() -> AsyncSession:
    """获取数据库会话（依赖注入）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
