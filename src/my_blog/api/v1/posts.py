"""文章路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.my_blog.database import get_db
from src.my_blog.models.user import User
from src.my_blog.models.post import Post
from src.my_blog.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from src.my_blog.services.post_service import PostService
from src.my_blog.services.comment_service import CommentService
from src.my_blog.schemas.comment import CommentCreate, CommentResponse
from src.my_blog.api.deps import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostListResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """获取所有已发布的文章"""
    posts = await PostService.get_all(db, skip=skip, limit=limit)
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取单篇文章"""
    post = await PostService.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新文章"""
    post = await PostService.create(db, post_in, author_id=current_user.id)
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新文章（仅作者）"""
    post = await PostService.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    updated_post = await PostService.update(db, post_id, post_in)
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文章（仅作者）"""
    post = await PostService.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    await PostService.delete(db, post_id)


# 评论子路由
@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """获取文章的所有评论"""
    # 检查文章是否存在
    post = await PostService.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    comments = await CommentService.get_by_post(db, post_id, skip=skip, limit=limit)
    return comments


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加评论到文章"""
    # 检查文章是否存在
    post = await PostService.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    comment = await CommentService.create(
        db,
        post_id=post_id,
        author_id=current_user.id,
        content=comment_in.content,
    )
    return comment
