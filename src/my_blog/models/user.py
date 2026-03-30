"""用户模型"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .post import Post
    from .comment import Comment


class User(SQLModel, table=True):
    """用户数据库模型"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(min_length=3, max_length=50)
    hashed_password: str = Field(default="", min_length=1)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    posts: list["Post"] = Relationship(back_populates="author", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    comments: list["Comment"] = Relationship(back_populates="author", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
