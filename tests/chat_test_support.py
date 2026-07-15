"""챗봇 단위 테스트에서 사용하는 격리된 SQLite 테스트 데이터."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.models.location import Location
from app.db.models.post import Post
from app.db.models.post_tag import PostTag


def create_test_session() -> tuple[Session, object]:
    """메모리 SQLite 세션과 엔진을 생성한다."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    return testing_session_local(), engine


def seed_chat_test_data(db: Session) -> None:
    """지역정보·축제·모범음식점·게시글 검색용 샘플을 적재한다."""

    locations = [
        Location(
            content_id="loc-museum-1",
            region="서울",
            content_type_id="14",
            category="문화시설",
            title="서울역사박물관",
            addr1="서울특별시 종로구 새문안로 55",
            addr2=None,
            tel="02-0000-0001",
            latitude=37.5704,
            longitude=126.9779,
            source_file="서울_문화시설.json",
        ),
        Location(
            content_id="loc-tour-1",
            region="서울",
            content_type_id="12",
            category="관광지",
            title="북촌한옥마을",
            addr1="서울특별시 종로구 계동길 37",
            addr2=None,
            tel="02-0000-0002",
            latitude=37.5826,
            longitude=126.9831,
            source_file="서울_관광지.json",
        ),
        Location(
            content_id="loc-festival-1",
            region="서울",
            content_type_id="15",
            category="축제공연행사",
            title="한강 여름 축제",
            addr1="서울특별시 영등포구 여의동로 330",
            addr2=None,
            tel="02-0000-0003",
            latitude=37.5284,
            longitude=126.9348,
            source_file="서울_축제공연행사.json",
        ),
        Location(
            content_id="loc-model-restaurant-1",
            region="서울",
            content_type_id="39",
            category="음식점",
            title="종로 모범 한식당",
            addr1="서울특별시 종로구 종로 1",
            addr2=None,
            tel="02-0000-0004",
            latitude=37.5700,
            longitude=126.9800,
            source_file="서울_모범음식점.json",
            class_system1="모범음식점",
        ),
        Location(
            content_id="loc-normal-restaurant-1",
            region="서울",
            content_type_id="39",
            category="음식점",
            title="종로 일반 식당",
            addr1="서울특별시 종로구 종로 2",
            addr2=None,
            tel="02-0000-0005",
            latitude=37.5710,
            longitude=126.9810,
            source_file="서울_음식점.json",
        ),
        Location(
            content_id="loc-special-character-1",
            region="서울",
            content_type_id="28",
            category="레포츠",
            title="100% 만족_체험관",
            addr1="서울특별시 마포구 월드컵로 1",
            addr2=None,
            source_file="서울_레포츠.json",
        ),
    ]

    db.add_all(locations)

    post1 = Post(
        category="관광지",
        title="남산 야경 방문 후기",
        content="평일 저녁에 남산에 다녀왔는데 야경이 좋았습니다.",
        edit_password="test-password-1",
        view_count=20,
        created_at=datetime(2026, 7, 15, 1, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 7, 15, 1, 0, tzinfo=timezone.utc),
    )
    post1.tags = [
        PostTag(tag="남산"),
        PostTag(tag="야경"),
    ]

    post2 = Post(
        category="문화시설",
        title="종로구 박물관 방문기",
        content="아이와 함께 박물관을 둘러본 경험을 정리했습니다.",
        edit_password="test-password-2",
        view_count=8,
        created_at=datetime(2026, 7, 14, 1, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 7, 14, 1, 0, tzinfo=timezone.utc),
    )
    post2.tags = [
        PostTag(tag="종로구"),
        PostTag(tag="박물관"),
    ]

    post3 = Post(
        category="쇼핑",
        title="망원시장 장보기 기록",
        content="주말에 시장을 둘러보고 먹거리를 구매했습니다.",
        edit_password="test-password-3",
        view_count=3,
        created_at=datetime(2026, 7, 13, 1, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 7, 13, 1, 0, tzinfo=timezone.utc),
    )
    post3.tags = [PostTag(tag="망원시장")]

    db.add_all([post1, post2, post3])
    db.commit()
