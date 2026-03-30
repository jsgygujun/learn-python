"""文章模型"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User
    from .comment import Comment


class Post(SQLModel, table=True):
    """文章数据库模型"""

    __tablename__ = "posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200, index=True)
    content: str = Field(min_length=1)
    is_published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 外键
    author_id: int = Field(foreign_key="users.id", ondelete="CASCADE")

    # 关系
    author: Optional["User"] = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
