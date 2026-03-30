"""认证 API 测试"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """测试用户注册"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass1234",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User created successfully"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """测试重复邮箱注册"""
    # 先创建一个用户
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "username": "user1",
            "password": "testpass1234",
        },
    )

    # 尝试用相同邮箱注册
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "username": "user2",
            "password": "testpass1234",
        },
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """测试登录成功"""
    # 先注册用户
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "testpass1234",
        },
    )

    # 登录
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpass1234",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """测试登录密码错误"""
    # 先注册用户
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@example.com",
            "username": "wronguser",
            "password": "testpass1234",
        },
    )

    # 尝试错误密码
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]
