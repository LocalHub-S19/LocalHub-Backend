from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.post import Post


class PostTag(Base):
    """게시글에 연결되는 자유 태그 모델."""

    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "posts.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    tag: Mapped[str] = mapped_column(
        String(15),
        primary_key=True,
    )

    post: Mapped[Post] = relationship(
        "Post",
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return (
            f"PostTag(post_id={self.post_id!r}, "
            f"tag={self.tag!r})"
        )