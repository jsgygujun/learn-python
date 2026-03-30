"""依赖注入"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.my_blog.database import get_db
from src.my_blog.security import get_current_user
from src.my_blog.models.user import User


async def get_current_user_id(
    current_user: User = Depends(get_current_user),
) -> int:
    """获取当前用户 ID"""
    return current_user.id
