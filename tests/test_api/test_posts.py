"""文章 API 测试"""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_token(client: AsyncClient) -> str:
    """获取认证 token"""
    # 注册并登录
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "postuser@example.com",
            "username": "postuser",
            "password": "testpass1234",  # 至少 8 位
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "postuser@example.com",
            "password": "testpass1234",
        },
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_token: str):
    """测试创建文章"""
    response = await client.post(
        "/api/v1/posts/",
        json={
            "title": "Test Post",
            "content": "This is test content",
            "is_published": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "This is test content"


@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient, auth_token: str):
    """测试获取文章列表"""
    # 先创建一篇文章
    await client.post(
        "/api/v1/posts/",
        json={
            "title": "Post 1",
            "content": "Content 1",
            "is_published": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = await client.get("/api/v1/posts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_post(client: AsyncClient, auth_token: str):
    """测试获取单篇文章"""
    # 创建文章
    create_response = await client.post(
        "/api/v1/posts/",
        json={
            "title": "Single Post",
            "content": "Single content",
            "is_published": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Single Post"


@pytest.mark.asyncio
async def test_update_post(client: AsyncClient, auth_token: str):
    """测试更新文章"""
    # 创建文章
    create_response = await client.post(
        "/api/v1/posts/",
        json={
            "title": "Update Post",
            "content": "Original content",
            "is_published": False,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    # 更新文章
    response = await client.put(
        f"/api/v1/posts/{post_id}",
        json={"title": "Updated Post", "is_published": True},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Post"
    assert data["is_published"] == True


@pytest.mark.asyncio
async def test_delete_post(client: AsyncClient, auth_token: str):
    """测试删除文章"""
    # 创建文章
    create_response = await client.post(
        "/api/v1/posts/",
        json={
            "title": "Delete Post",
            "content": "To be deleted",
            "is_published": False,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    # 删除文章
    response = await client.delete(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 204

    # 验证已删除
    get_response = await client.get(f"/api/v1/posts/{post_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient, auth_token: str):
    """测试创建评论"""
    # 创建文章
    create_response = await client.post(
        "/api/v1/posts/",
        json={
            "title": "Comment Post",
            "content": "Post with comments",
            "is_published": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    # 创建评论
    response = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Great post!"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Great post!"


@pytest.mark.asyncio
async def test_list_comments(client: AsyncClient, auth_token: str):
    """测试获取评论列表"""
    # 创建文章
    create_response = await client.post(
        "/api/v1/posts/",
        json={
            "title": "Comments Post",
            "content": "Post with comments",
            "is_published": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    post_id = create_response.json()["id"]

    # 创建评论
    await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Comment 1"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Comment 2"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = await client.get(f"/api/v1/posts/{post_id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2
