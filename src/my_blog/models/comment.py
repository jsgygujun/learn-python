"""评论模型"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User
    from .post import Post


class Comment(SQLModel, table=True):
    """评论数据库模型"""

    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(min_length=1, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 外键
    post_id: int = Field(foreign_key="posts.id", ondelete="CASCADE")
    author_id: int = Field(foreign_key="users.id", ondelete="CASCADE")

    # 关系
    post: Optional["Post"] = Relationship(back_populates="comments")
    author: Optional["User"] = Relationship(back_populates="comments")
