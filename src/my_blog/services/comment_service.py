"""评论服务"""

from typing import Optional, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.my_blog.models.comment import Comment


class CommentService:
    """评论服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, comment_id: int) -> Optional[Comment]:
        """通过 ID 获取评论"""
        return await db.get(Comment, comment_id)

    @staticmethod
    async def get_by_post(
        db: AsyncSession,
        post_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Comment]:
        """获取文章的所有评论"""
        query = select(Comment).where(Comment.post_id == post_id)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(
        db: AsyncSession,
        post_id: int,
        author_id: int,
        content: str,
    ) -> Comment:
        """创建评论"""
        comment = Comment(
            content=content,
            post_id=post_id,
            author_id=author_id,
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    @staticmethod
    async def delete(db: AsyncSession, comment_id: int) -> bool:
        """删除评论"""
        comment = await CommentService.get_by_id(db, comment_id)
        if not comment:
            return False
        await db.delete(comment)
        await db.commit()
        return True
