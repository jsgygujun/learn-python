"""用户 Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    """用户基础 Schema"""

    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")


class UserCreate(UserBase):
    """创建用户请求"""

    password: str = Field(..., min_length=8, description="密码（至少 8 位）")


class UserLogin(BaseModel):
    """用户登录请求"""

    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应"""

    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """数据库中的用户（包含敏感字段）"""

    hashed_password: str
