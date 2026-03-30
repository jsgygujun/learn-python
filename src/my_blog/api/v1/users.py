"""用户路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.my_blog.database import get_db
from src.my_blog.models.user import User
from src.my_blog.schemas.user import UserResponse
from src.my_blog.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息"""
    return current_user
