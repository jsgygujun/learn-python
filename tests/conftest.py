"""pytest 配置"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.my_blog.main import app
from src.my_blog.database import get_db


# 测试数据库 URL (每个测试使用独立的内存数据库)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # 创建表
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # 创建一个共享会话用于整个测试
    shared_session = test_async_session_factory()

    yield shared_session

    # 清理
    await shared_session.close()
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as ac:
        yield ac

    app.dependency_overrides.clear()
