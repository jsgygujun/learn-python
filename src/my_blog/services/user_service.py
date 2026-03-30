"""用户服务"""

from typing import Optional, List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.my_blog.models.user import User
from src.my_blog.schemas.user import UserCreate
from src.my_blog.security import get_password_hash


class UserService:
    """用户服务类"""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """通过 ID 获取用户"""
        return await db.get(User, user_id)

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        result = await db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """创建用户"""
        user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
