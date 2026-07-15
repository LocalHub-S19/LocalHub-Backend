"""운영 SQLite에 경량 RAG 검색 대상 데이터가 있는지 점검한다."""

from __future__ import annotations

from sqlalchemy import func, inspect, or_, select

from app.db.database import SessionLocal, engine
from app.db.models.location import Location
from app.db.models.post import Post


def print_sample(title: str, rows: list[object]) -> None:
    print(f"\n[{title}]")
    if not rows:
        print("- 데이터 없음")
        return

    for row in rows:
        print(f"- {row}")


def main() -> int:
    inspector = inspect(engine)

    if not inspector.has_table("locations") or not inspector.has_table("posts"):
        print("[실패] localhub.db에 locations/posts 테이블이 없습니다.")
        print("서버를 한 번 실행하거나 python scripts/create_tables.py 를 실행하세요.")
        return 1

    db = SessionLocal()

    try:
        location_count = db.scalar(select(func.count()).select_from(Location)) or 0
        post_count = db.scalar(select(func.count()).select_from(Post)) or 0

        festival_count = db.scalar(
            select(func.count())
            .select_from(Location)
            .where(
                or_(
                    Location.content_type_id == "15",
                    Location.category == "축제공연행사",
                )
            )
        ) or 0

        model_restaurant_count = db.scalar(
            select(func.count())
            .select_from(Location)
            .where(
                or_(
                    Location.category.ilike("%모범%"),
                    Location.title.ilike("%모범%"),
                    Location.source_file.ilike("%모범%"),
                    Location.class_system1.ilike("%모범%"),
                    Location.class_system2.ilike("%모범%"),
                    Location.class_system3.ilike("%모범%"),
                )
            )
        ) or 0

        print("[LocalHub 챗봇 RAG 데이터 점검]")
        print(f"지역정보 전체: {location_count}건")
        print(f"커뮤니티 게시글: {post_count}건")
        print(f"축제·공연·행사: {festival_count}건")
        print(f"'모범' 표시 장소: {model_restaurant_count}건")

        category_rows = db.execute(
            select(Location.category, func.count())
            .group_by(Location.category)
            .order_by(Location.category)
        ).all()
        print_sample("카테고리별 지역정보", category_rows)

        location_samples = db.execute(
            select(Location.content_id, Location.category, Location.title, Location.addr1)
            .order_by(Location.title)
            .limit(5)
        ).all()
        print_sample("지역정보 샘플 5건", location_samples)

        post_samples = db.execute(
            select(Post.id, Post.category, Post.title)
            .order_by(Post.created_at.desc())
            .limit(5)
        ).all()
        print_sample("게시글 샘플 5건", post_samples)

        model_samples = db.execute(
            select(Location.title, Location.addr1, Location.source_file)
            .where(
                or_(
                    Location.category.ilike("%모범%"),
                    Location.title.ilike("%모범%"),
                    Location.source_file.ilike("%모범%"),
                    Location.class_system1.ilike("%모범%"),
                    Location.class_system2.ilike("%모범%"),
                    Location.class_system3.ilike("%모범%"),
                )
            )
            .limit(5)
        ).all()
        print_sample("모범음식점 판별 가능 샘플", model_samples)

        if location_count == 0:
            print("\n[실패] locations 테이블이 비어 있습니다.")
            print("먼저 python scripts/import_locations.py 를 실행하세요.")
            return 1

        if post_count == 0:
            print("\n[주의] 게시글이 없어 post_search 결과는 항상 비게 됩니다.")

        if festival_count == 0:
            print("[주의] 축제 데이터가 없어 festival_search 결과는 비게 됩니다.")

        if model_restaurant_count == 0:
            print("[주의] '모범' 구분값이 없어 모범음식점 검색 결과는 비게 됩니다.")

        print("\n[완료] 데이터 점검이 끝났습니다.")
        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
