"""文章服务"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.my_blog.models.post import Post
from src.my_blog.schemas.post import PostCreate, PostUpdate


class PostService:
    """文章服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
        """通过 ID 获取文章"""
        return await db.get(Post, post_id)

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        only_published: bool = True,
    ) -> List[Post]:
        """获取所有文章"""
        query = select(Post)
        if only_published:
            query = query.where(Post.is_published == True)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_author(
        db: AsyncSession,
        author_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Post]:
        """获取作者的所有文章"""
        query = select(Post).where(Post.author_id == author_id)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, post_in: PostCreate, author_id: int) -> Post:
        """创建文章"""
        post = Post(
            title=post_in.title,
            content=post_in.content,
            is_published=post_in.is_published,
            author_id=author_id,
        )
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def update(
        db: AsyncSession,
        post_id: int,
        post_in: PostUpdate,
    ) -> Optional[Post]:
        """更新文章"""
        post = await PostService.get_by_id(db, post_id)
        if not post:
            return None

        update_data = post_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(post, key, value)

        # 更新 updated_at 时间戳
        post.updated_at = datetime.utcnow()

        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post

    @staticmethod
    async def delete(db: AsyncSession, post_id: int) -> bool:
        """删除文章"""
        post = await PostService.get_by_id(db, post_id)
        if not post:
            return False
        await db.delete(post)
        await db.commit()
        return True
