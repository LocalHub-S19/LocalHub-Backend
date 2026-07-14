from __future__ import annotations

import math
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import (
    PostCreateRequest,
    PostDeleteRequest,
    PostDetailResponse,
    PostListItemResponse,
    PostListResponse,
    PostUpdateRequest,
)


class PostService:
    """익명 커뮤니티 게시글 비즈니스 로직을 담당한다."""

    def __init__(self, db: Session) -> None:
        """DB 세션을 저장한다."""

        self.db = db

    @staticmethod
    def _extract_tags(
        post: Post,
    ) -> list[str]:
        """PostTag 객체 목록에서 태그 문자열만 추출한다."""

        return [
            post_tag.tag
            for post_tag in post.tags
        ]

    @staticmethod
    def _to_list_item(
        post: Post,
    ) -> PostListItemResponse:
        """Post 모델을 게시글 목록 응답으로 변환한다."""

        return PostListItemResponse(
            id=post.id,
            category=post.category,
            title=post.title,
            tags=PostService._extract_tags(post),
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    @staticmethod
    def _to_detail_response(
        post: Post,
    ) -> PostDetailResponse:
        """Post 모델을 게시글 상세 응답으로 변환한다."""

        return PostDetailResponse(
            id=post.id,
            category=post.category,
            title=post.title,
            content=post.content,
            tags=PostService._extract_tags(post),
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    def get_posts(
        self,
        category: str | None = None,
        keyword: str | None = None,
        tag: str | None = None,
        page: int = 1,
        size: int = 20,
        sort: Literal["latest", "views"] = "latest",
    ) -> PostListResponse:
        """
        게시글 목록을 조회한다.

        지원 기능:
        - 카테고리 필터
        - 제목·내용·태그 통합 검색
        - 특정 태그 필터
        - 최신순·조회수순 정렬
        - 페이지네이션
        """

        posts, total = PostRepository.find_all(
            db=self.db,
            category=category,
            keyword=keyword,
            tag=tag,
            page=page,
            size=size,
            sort=sort,
        )

        items = [
            self._to_list_item(post)
            for post in posts
        ]

        total_pages = (
            math.ceil(total / size)
            if total > 0
            else 0
        )

        return PostListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

    def create_post(
        self,
        request: PostCreateRequest,
    ) -> PostDetailResponse:
        """익명 게시글과 태그를 생성한다."""

        post = PostRepository.create(
            db=self.db,
            category=request.category,
            title=request.title,
            content=request.content,
            password=request.password,
            tags=request.tags,
        )

        return self._to_detail_response(post)

    def get_post_detail(
        self,
        post_id: int,
    ) -> PostDetailResponse:
        """게시글 상세정보를 조회하고 조회수를 1 증가시킨다."""

        post = PostRepository.increase_view_count(
            db=self.db,
            post_id=post_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 게시글을 찾을 수 없습니다.",
            )

        return self._to_detail_response(post)

    def update_post(
        self,
        post_id: int,
        request: PostUpdateRequest,
    ) -> PostDetailResponse:
        """비밀번호 확인 후 게시글 내용과 태그를 수정한다."""

        post = PostRepository.find_by_id(
            db=self.db,
            post_id=post_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 게시글을 찾을 수 없습니다.",
            )

        # 의뢰서 요구사항에 따라 작성 시 등록한 비밀번호를
        # 평문 상태로 직접 비교한다.
        if post.edit_password != request.password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글 비밀번호가 일치하지 않습니다.",
            )

        updated_post = PostRepository.update(
            db=self.db,
            post=post,
            category=request.category,
            title=request.title,
            content=request.content,
            tags=request.tags,
        )

        return self._to_detail_response(
            updated_post
        )

    def delete_post(
        self,
        post_id: int,
        request: PostDeleteRequest,
    ) -> None:
        """비밀번호 확인 후 게시글과 연결된 태그를 삭제한다."""

        post = PostRepository.find_by_id(
            db=self.db,
            post_id=post_id,
        )

        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 게시글을 찾을 수 없습니다.",
            )

        if post.edit_password != request.password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게시글 비밀번호가 일치하지 않습니다.",
            )

        PostRepository.delete(
            db=self.db,
            post=post,
        )