"""文章 Schema"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PostBase(BaseModel):
    """文章基础 Schema"""

    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: str = Field(..., min_length=1, description="文章内容")


class PostCreate(PostBase):
    """创建文章请求"""

    is_published: bool = Field(default=False, description="是否发布")


class PostUpdate(BaseModel):
    """更新文章请求"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    is_published: Optional[bool] = None


class PostResponse(PostBase):
    """文章响应"""

    id: int
    author_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostListResponse(BaseModel):
    """文章列表响应"""

    id: int
    title: str
    author_id: int
    is_published: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
