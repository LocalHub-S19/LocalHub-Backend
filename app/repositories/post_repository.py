from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session, selectinload

from app.db.models.post import Post
from app.db.models.post_tag import PostTag


class PostRepository:
    """익명 커뮤니티 게시글 데이터 접근을 담당한다."""

    @staticmethod
    def _build_filters(
        category: str | None = None,
        keyword: str | None = None,
        tag: str | None = None,
    ) -> list:
        """게시글 검색 조건을 생성한다."""

        filters = []

        if category:
            filters.append(Post.category == category.strip())

        if keyword and keyword.strip():
            search_keyword = f"%{keyword.strip()}%"

            filters.append(
                or_(
                    Post.title.ilike(search_keyword),
                    Post.content.ilike(search_keyword),
                    Post.tags.any(
                        PostTag.tag.ilike(search_keyword)
                    ),
                )
            )

        if tag and tag.strip():
            filters.append(
                Post.tags.any(
                    PostTag.tag == tag.strip()
                )
            )

        return filters

    @staticmethod
    def find_all(
        db: Session,
        category: str | None = None,
        keyword: str | None = None,
        tag: str | None = None,
        page: int = 1,
        size: int = 20,
        sort: str = "latest",
    ) -> tuple[list[Post], int]:
        """
        게시글 목록을 조회한다.

        sort:
            latest: 최신순
            views: 조회수순

        반환값:
            (게시글 목록, 전체 게시글 수)
        """

        filters = PostRepository._build_filters(
            category=category,
            keyword=keyword,
            tag=tag,
        )

        count_statement = (
            select(func.count(Post.id))
            .where(*filters)
        )

        total = db.scalar(count_statement) or 0

        if sort == "views":
            order_conditions = [
                Post.view_count.desc(),
                Post.created_at.desc(),
            ]
        else:
            order_conditions = [
                Post.created_at.desc(),
            ]

        offset = (page - 1) * size

        statement = (
            select(Post)
            .options(selectinload(Post.tags))
            .where(*filters)
            .order_by(*order_conditions)
            .offset(offset)
            .limit(size)
        )

        posts = list(db.scalars(statement).all())

        return posts, total

    @staticmethod
    def find_by_id(
        db: Session,
        post_id: int,
    ) -> Post | None:
        """게시글 ID로 게시글과 태그를 조회한다."""

        statement = (
            select(Post)
            .options(selectinload(Post.tags))
            .where(Post.id == post_id)
        )

        return db.scalar(statement)

    @staticmethod
    def create(
        db: Session,
        category: str,
        title: str,
        content: str,
        password: str,
        tags: list[str],
    ) -> Post:
        """게시글과 태그를 저장한다."""

        post = Post(
            category=category,
            title=title,
            content=content,
            edit_password=password,
            view_count=0,
        )

        post.tags = [
            PostTag(tag=tag)
            for tag in tags
        ]

        db.add(post)
        db.commit()
        db.refresh(post)

        created_post = PostRepository.find_by_id(
            db=db,
            post_id=post.id,
        )

        if created_post is None:
            raise RuntimeError("게시글 생성 후 조회에 실패했습니다.")

        return created_post

    @staticmethod
    def update(
        db: Session,
        post: Post,
        category: str,
        title: str,
        content: str,
        tags: list[str],
    ) -> Post:
        """게시글 내용과 태그를 수정한다."""

        post.category = category
        post.title = title
        post.content = content

        # 기존 태그를 삭제하고 새로운 태그로 교체한다.
        post.tags = [
            PostTag(tag=tag)
            for tag in tags
        ]

        db.commit()

        updated_post = PostRepository.find_by_id(
            db=db,
            post_id=post.id,
        )

        if updated_post is None:
            raise RuntimeError("게시글 수정 후 조회에 실패했습니다.")

        return updated_post

    @staticmethod
    def increase_view_count(
        db: Session,
        post_id: int,
    ) -> Post | None:
        """게시글 조회수를 1 증가시킨다."""

        statement = (
            update(Post)
            .where(Post.id == post_id)
            .values(view_count=Post.view_count + 1)
        )

        result = db.execute(statement)

        if result.rowcount == 0:
            db.rollback()
            return None

        db.commit()

        return PostRepository.find_by_id(
            db=db,
            post_id=post_id,
        )

    @staticmethod
    def delete(
        db: Session,
        post: Post,
    ) -> None:
        """게시글을 삭제한다."""

        db.delete(post)
        db.commit()