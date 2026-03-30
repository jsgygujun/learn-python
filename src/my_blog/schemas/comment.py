"""评论 Schema"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CommentCreate(BaseModel):
    """创建评论请求"""

    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")


class CommentResponse(BaseModel):
    """评论响应"""

    id: int
    content: str
    author_id: int
    post_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
