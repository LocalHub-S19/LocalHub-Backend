from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.post import (
    PostCreateRequest,
    PostDetailResponse,
    PostListResponse,
    PostUpdateRequest,
    PostDeleteRequest,
)
from app.services.post_service import PostService


router = APIRouter(
    prefix="/posts",
    tags=["커뮤니티"],
)


@router.get(
    "",
    response_model=PostListResponse,
    summary="게시글 목록 조회 및 검색",
    description=(
        "익명 커뮤니티 게시글 목록을 조회합니다. "
        "제목, 내용, 태그 검색과 카테고리·태그 필터, "
        "페이지네이션 및 정렬을 지원합니다."
    ),
)
def get_posts(
    category: str | None = Query(
        default=None,
        max_length=50,
        description="게시글 카테고리",
        examples=["관광지"],
    ),
    keyword: str | None = Query(
        default=None,
        max_length=100,
        description="제목, 내용, 태그 통합 검색어",
        examples=["남산"],
    ),
    tag: str | None = Query(
        default=None,
        max_length=15,
        description="게시글 태그 필터",
        examples=["야경"],
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="페이지 번호",
    ),
    size: int = Query(
        default=20,
        ge=1,
        le=settings.max_page_size,
        description="페이지당 게시글 수",
    ),
    sort: Literal["latest", "views"] = Query(
        default="latest",
        description="정렬 기준: latest는 최신순, views는 조회수순",
    ),
    db: Session = Depends(get_db),
) -> PostListResponse:
    """게시글 목록을 조회하고 검색한다."""

    service = PostService(db)

    return service.get_posts(
        category=category,
        keyword=keyword,
        tag=tag,
        page=page,
        size=size,
        sort=sort,
    )


@router.post(
    "",
    response_model=PostDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성",
    description=(
        "제목, 내용, 수정·삭제용 비밀번호와 태그를 입력하여 "
        "익명 게시글을 작성합니다."
    ),
    responses={
        422: {
            "description": "입력값 검증 실패",
        },
    },
)
def create_post(
    request: PostCreateRequest,
    db: Session = Depends(get_db),
) -> PostDetailResponse:
    """익명 게시글과 태그를 생성한다."""

    service = PostService(db)

    return service.create_post(
        request=request,
    )


@router.get(
    "/{post_id}",
    response_model=PostDetailResponse,
    summary="게시글 상세 조회",
    description=(
        "게시글의 제목, 내용, 태그, 조회수, 작성일과 수정일을 조회합니다. "
        "정상적으로 상세조회된 경우 조회수가 1 증가합니다."
    ),
    responses={
        404: {
            "description": "해당 게시글을 찾을 수 없음",
        },
    },
)
def get_post_detail(
    post_id: int = Path(
        ...,
        ge=1,
        description="게시글 ID",
        examples=[1],
    ),
    db: Session = Depends(get_db),
) -> PostDetailResponse:
    """게시글 상세정보를 조회하고 조회수를 증가시킨다."""

    service = PostService(db)

    return service.get_post_detail(
        post_id=post_id,
    )


@router.put(
    "/{post_id}",
    response_model=PostDetailResponse,
    summary="게시글 수정",
    description=(
        "작성 시 등록한 비밀번호가 일치하면 "
        "게시글의 카테고리, 제목, 내용과 태그를 수정합니다."
    ),
    responses={
        403: {
            "description": "비밀번호 불일치",
        },
        404: {
            "description": "해당 게시글을 찾을 수 없음",
        },
        422: {
            "description": "입력값 검증 실패",
        },
    },
)
def update_post(
    request: PostUpdateRequest,
    post_id: int = Path(
        ...,
        ge=1,
        description="게시글 ID",
        examples=[1],
    ),
    db: Session = Depends(get_db),
) -> PostDetailResponse:
    """비밀번호 확인 후 게시글과 태그를 수정한다."""

    service = PostService(db)

    return service.update_post(
        post_id=post_id,
        request=request,
    )


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    summary="게시글 삭제",
    description=(
        "작성 시 등록한 비밀번호가 일치하면 "
        "게시글과 연결된 태그를 삭제합니다."
    ),
    responses={
        403: {
            "description": "비밀번호 불일치",
        },
        404: {
            "description": "해당 게시글을 찾을 수 없음",
        },
    },
)
def delete_post(
    request: PostDeleteRequest,
    post_id: int = Path(
        ...,
        ge=1,
        description="게시글 ID",
        examples=[1],
    ),
    db: Session = Depends(get_db),
) -> Response:
    """비밀번호 확인 후 게시글을 삭제한다."""

    service = PostService(db)

    service.delete_post(
        post_id=post_id,
        request=request,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )