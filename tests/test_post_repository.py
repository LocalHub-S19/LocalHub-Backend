import pytest

from app.db.database import SessionLocal
from app.repositories.post_repository import PostRepository


@pytest.fixture
def db_session():
    """세션과 생성된 게시글 id 목록을 제공하고 종료 시 정리합니다."""
    db = SessionLocal()
    created_ids: list[int] = []
    try:
        yield db, created_ids
    finally:
        # 생성한 게시글 정리
        for pid in created_ids:
            p = PostRepository.find_by_id(db, pid)
            if p:
                PostRepository.delete(db, p)
        db.close()


def _create(db, created_ids, category, title, content="content", tags=None, password="pwd"):
    tags = tags or []
    post = PostRepository.create(db, category=category, title=title, content=content, password=password, tags=tags)
    created_ids.append(post.id)
    return post


def test_find_all_filters_and_pagination(db_session):
    db, created = db_session

    p1 = _create(db, created, category="test-cat", title="Alpha", tags=["y"])
    p2 = _create(db, created, category="test-cat", title="Beta", tags=["y"])
    p3 = _create(db, created, category="other", title="Gamma", tags=["z"])

    # category 필터
    posts, total = PostRepository.find_all(db, category="test-cat", page=1, size=10)
    assert total == 2
    assert all(p.category == "test-cat" for p in posts)

    # tag 필터
    posts, total = PostRepository.find_all(db, tag="y")
    assert total == 2
    assert any(p.id == p1.id for p in posts)

    # keyword (title) 필터
    posts, total = PostRepository.find_all(db, keyword="Alpha")
    assert total == 1
    assert posts[0].title == "Alpha"

    # 페이징: size=1으로 전체는 2, 반환은 1개
    posts, total = PostRepository.find_all(db, category="test-cat", page=1, size=1)
    assert total == 2
    assert len(posts) == 1


def test_find_all_sort_by_views(db_session):
    db, created = db_session

    p1 = _create(db, created, category="views-cat", title="MostViewed", tags=[])
    p2 = _create(db, created, category="views-cat", title="LessViewed", tags=[])

    # 조회수 증가: p1 두 번, p2 한 번
    PostRepository.increase_view_count(db, p1.id)
    PostRepository.increase_view_count(db, p1.id)
    PostRepository.increase_view_count(db, p2.id)

    posts, total = PostRepository.find_all(db, sort="views", page=1, size=10)
    assert total >= 2
    # 최상단이 가장 많이 본 게시글(p1)인지 확인
    assert posts[0].id == p1.id