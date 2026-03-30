"""认证路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.my_blog.database import get_db
from src.my_blog.models.user import User
from src.my_blog.schemas.user import UserCreate, UserResponse
from src.my_blog.services.user_service import UserService
from src.my_blog.security import verify_password, create_access_token
from src.my_blog.config import settings
from src.my_blog.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """注册新用户"""
    # 检查邮箱是否已存在
    if await UserService.get_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 检查用户名是否已存在
    if await UserService.get_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # 创建用户
    await UserService.create(db, user_in)
    return {"message": "User created successfully"}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """登录获取 access token"""
    # 尝试通过邮箱或用户名查找用户
    user = await UserService.get_by_email(db, form_data.username)
    if not user:
        user = await UserService.get_by_username(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    access_token = create_access_token(
        data={"sub": user.id},
    )

    return {"access_token": access_token, "token_type": "bearer"}
