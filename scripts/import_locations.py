from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete
from sqlalchemy.orm import Session


# `python scripts/import_locations.py`로 실행해도
# 프로젝트 루트의 app 패키지를 찾을 수 있도록 경로를 추가한다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.db.database import SessionLocal, create_tables
from app.db.models.location import Location


# 💡 수정된 부분: 기본 데이터 디렉토리를 Render의 Secret Files 경로로 변경합니다.
DEFAULT_DATA_DIR = Path("data/raw")


CONTENT_TYPE_NAMES: dict[str, str] = {
    "12": "관광지",
    "14": "문화시설",
    "15": "축제공연행사",
    "25": "여행코스",
    "28": "레포츠",
    "32": "숙박",
    "38": "쇼핑",
    "39": "음식점",
}


def utc_now() -> datetime:
    """현재 UTC 시각을 반환한다."""

    return datetime.now(timezone.utc)


def empty_to_none(value: Any) -> str | None:
    """
    빈 문자열 또는 None을 None으로 변환한다.

    문자열이 아닌 값이 들어오면 문자열로 변환해서 저장한다.
    """

    if value is None:
        return None

    converted = str(value).strip()

    if converted == "":
        return None

    return converted


def parse_coordinate(value: Any) -> float | None:
    """
    TourAPI 좌표 문자열을 float로 변환한다.

    변환할 수 없거나 빈 값이면 None을 반환한다.
    """

    normalized = empty_to_none(value)

    if normalized is None:
        return None

    try:
        return float(normalized)
    except (TypeError, ValueError):
        return None


def load_json_file(file_path: Path) -> dict[str, Any]:
    """
    JSON 파일을 읽어 딕셔너리로 반환한다.

    utf-8-sig를 사용해 BOM이 포함된 UTF-8 파일도 처리한다.
    """

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"JSON 최상위 값이 객체가 아닙니다: {file_path.name}"
        )

    return data


def resolve_content_type_id(
    payload: dict[str, Any],
    item: dict[str, Any],
) -> str | None:
    """
    콘텐츠 유형 ID를 반환한다.

    장소별 contenttypeid를 우선 사용하고,
    값이 없으면 JSON 최상위 contentTypeId를 사용한다.
    """

    item_content_type_id = empty_to_none(
        item.get("contenttypeid")
    )

    if item_content_type_id is not None:
        return item_content_type_id

    return empty_to_none(
        payload.get("contentTypeId")
    )


def resolve_category(
    payload: dict[str, Any],
    content_type_id: str,
) -> str:
    """
    지역정보 카테고리 한글명을 반환한다.

    JSON 최상위 contentType이 있으면 해당 값을 사용하고,
    없으면 contentTypeId에 대응하는 한글명을 사용한다.
    """

    content_type = empty_to_none(
        payload.get("contentType")
    )

    if content_type is not None:
        return content_type

    return CONTENT_TYPE_NAMES.get(
        content_type_id,
        "기타",
    )


def build_location_values(
    payload: dict[str, Any],
    item: dict[str, Any],
    source_file: str,
) -> dict[str, Any] | None:
    """
    JSON 장소 데이터를 Location 모델에 맞는 딕셔너리로 변환한다.

    contentid, contenttypeid, title이 없는 데이터는
    적재할 수 없으므로 None을 반환한다.
    """

    content_id = empty_to_none(
        item.get("contentid")
    )

    content_type_id = resolve_content_type_id(
        payload=payload,
        item=item,
    )

    title = empty_to_none(
        item.get("title")
    )

    if content_id is None:
        print(
            f"[건너뜀] contentid가 없습니다. "
            f"파일={source_file}"
        )
        return None

    if content_type_id is None:
        print(
            f"[건너뜀] contenttypeid가 없습니다. "
            f"파일={source_file}, contentid={content_id}"
        )
        return None

    if title is None:
        print(
            f"[건너뜀] title이 없습니다. "
            f"파일={source_file}, contentid={content_id}"
        )
        return None

    region = (
        empty_to_none(payload.get("region"))
        or "서울"
    )

    category = resolve_category(
        payload=payload,
        content_type_id=content_type_id,
    )

    return {
        "content_id": content_id,
        "region": region,
        "content_type_id": content_type_id,
        "category": category,
        "title": title,
        "addr1": empty_to_none(
            item.get("addr1")
        ),
        "addr2": empty_to_none(
            item.get("addr2")
        ),
        "zipcode": empty_to_none(
            item.get("zipcode")
        ),
        "tel": empty_to_none(
            item.get("tel")
        ),
        "longitude": parse_coordinate(
            item.get("mapx")
        ),
        "latitude": parse_coordinate(
            item.get("mapy")
        ),
        "map_level": empty_to_none(
            item.get("mlevel")
        ),
        "area_code": empty_to_none(
            item.get("areacode")
        ),
        "sigungu_code": empty_to_none(
            item.get("sigungucode")
        ),
        "legal_region_code": empty_to_none(
            item.get("lDongRegnCd")
        ),
        "legal_sigungu_code": empty_to_none(
            item.get("lDongSignguCd")
        ),
        "cat1": empty_to_none(
            item.get("cat1")
        ),
        "cat2": empty_to_none(
            item.get("cat2")
        ),
        "cat3": empty_to_none(
            item.get("cat3")
        ),
        "class_system1": empty_to_none(
            item.get("lclsSystm1")
        ),
        "class_system2": empty_to_none(
            item.get("lclsSystm2")
        ),
        "class_system3": empty_to_none(
            item.get("lclsSystm3")
        ),
        "first_image": empty_to_none(
            item.get("firstimage")
        ),
        "thumbnail_image": empty_to_none(
            item.get("firstimage2")
        ),
        "copyright_code": empty_to_none(
            item.get("cpyrhtDivCd")
        ),
        "source_created_at": empty_to_none(
            item.get("createdtime")
        ),
        "source_modified_at": empty_to_none(
            item.get("modifiedtime")
        ),
        "source_file": source_file,
        "imported_at": utc_now(),
    }


def update_location(
    location: Location,
    values: dict[str, Any],
) -> None:
    """
    기존 Location 객체를 새 JSON 값으로 갱신한다.
    """

    location.region = values["region"]
    location.content_type_id = values[
        "content_type_id"
    ]
    location.category = values["category"]
    location.title = values["title"]

    location.addr1 = values["addr1"]
    location.addr2 = values["addr2"]
    location.zipcode = values["zipcode"]
    location.tel = values["tel"]

    location.longitude = values["longitude"]
    location.latitude = values["latitude"]
    location.map_level = values["map_level"]

    location.area_code = values["area_code"]
    location.sigungu_code = values[
        "sigungu_code"
    ]

    location.legal_region_code = values[
        "legal_region_code"
    ]
    location.legal_sigungu_code = values[
        "legal_sigungu_code"
    ]

    location.cat1 = values["cat1"]
    location.cat2 = values["cat2"]
    location.cat3 = values["cat3"]

    location.class_system1 = values[
        "class_system1"
    ]
    location.class_system2 = values[
        "class_system2"
    ]
    location.class_system3 = values[
        "class_system3"
    ]

    location.first_image = values[
        "first_image"
    ]
    location.thumbnail_image = values[
        "thumbnail_image"
    ]
    location.copyright_code = values[
        "copyright_code"
    ]

    location.source_created_at = values[
        "source_created_at"
    ]
    location.source_modified_at = values[
        "source_modified_at"
    ]
    location.source_file = values[
        "source_file"
    ]
    location.imported_at = values[
        "imported_at"
    ]


def import_json_file(
    db: Session,
    file_path: Path,
) -> tuple[int, int, int]:
    """
    JSON 파일 하나를 locations 테이블에 적재한다.

    반환값:
        inserted_count: 새로 등록한 데이터 수
        updated_count: 기존 데이터를 갱신한 수
        skipped_count: 필수값 누락 등으로 건너뛴 수
    """

    payload = load_json_file(file_path)

    items = payload.get("items")

    if not isinstance(items, list):
        raise ValueError(
            f"items가 배열이 아닙니다: {file_path.name}"
        )

    inserted_count = 0
    updated_count = 0
    skipped_count = 0

    seen_content_ids: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            skipped_count += 1

            print(
                f"[건너뜀] 장소 데이터가 객체가 아닙니다. "
                f"파일={file_path.name}"
            )
            continue

        values = build_location_values(
            payload=payload,
            item=item,
            source_file=file_path.name,
        )

        if values is None:
            skipped_count += 1
            continue

        content_id = values["content_id"]

        if content_id in seen_content_ids:
            skipped_count += 1

            print(
                f"[건너뜀] 같은 파일 안의 중복 contentid입니다. "
                f"파일={file_path.name}, "
                f"contentid={content_id}"
            )
            continue

        seen_content_ids.add(content_id)

        existing_location = db.get(
            Location,
            content_id,
        )

        if existing_location is None:
            new_location = Location(**values)

            db.add(new_location)

            inserted_count += 1
        else:
            update_location(
                location=existing_location,
                values=values,
            )

            updated_count += 1

    return (
        inserted_count,
        updated_count,
        skipped_count,
    )


def find_json_files(
    data_dir: Path,
) -> list[Path]:
    """
    지정한 폴더 아래의 모든 JSON 파일을 찾는다.
    """

    if not data_dir.exists():
        return []

    if not data_dir.is_dir():
        return []

    return sorted(
        file_path
        for file_path in data_dir.rglob("*.json")
        if file_path.is_file()
    )


def reset_locations(
    db: Session,
) -> int:
    """
    locations 테이블의 기존 데이터를 모두 삭제한다.

    반환값:
        삭제된 데이터 수
    """

    existing_count = db.query(Location).count()

    db.execute(
        delete(Location)
    )

    db.commit()

    return existing_count


def parse_arguments() -> argparse.Namespace:
    """
    명령행 인수를 정의하고 반환한다.
    """

    parser = argparse.ArgumentParser(
        description=(
            "한국관광공사 서울 지역정보 JSON 파일을 "
            "SQLite locations 테이블에 적재합니다."
        )
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=(
            "JSON 파일이 들어 있는 폴더 경로 "
            f"(기본값: {DEFAULT_DATA_DIR})"
        ),
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help=(
            "적재 전에 locations 테이블의 "
            "기존 데이터를 모두 삭제합니다."
        ),
    )

    return parser.parse_args()


def main() -> int:
    """
    지역정보 데이터 적재 스크립트의 진입점이다.
    """

    args = parse_arguments()

    data_dir: Path = args.data_dir.resolve()

    json_files = find_json_files(
        data_dir=data_dir,
    )

    if not json_files:
        print(
            "[실패] JSON 파일을 찾을 수 없습니다."
        )
        print(
            f"확인한 폴더: {data_dir}"
        )
        print(
            "서울 JSON 파일을 설정된 폴더에 넣어주세요."
        )

        return 1

    print(
        f"[시작] JSON 파일 {len(json_files)}개를 "
        "확인했습니다."
    )
    print(
        f"데이터 폴더: {data_dir}"
    )

    create_tables()

    total_inserted = 0
    total_updated = 0
    total_skipped = 0

    db = SessionLocal()

    try:
        if args.reset:
            deleted_count = reset_locations(
                db=db,
            )

            print(
                f"[초기화] 기존 지역정보 "
                f"{deleted_count}건을 삭제했습니다."
            )

        for file_path in json_files:
            print()
            print(
                f"[처리 중] {file_path.name}"
            )

            try:
                (
                    inserted_count,
                    updated_count,
                    skipped_count,
                ) = import_json_file(
                    db=db,
                    file_path=file_path,
                )

                db.commit()

                total_inserted += inserted_count
                total_updated += updated_count
                total_skipped += skipped_count

                print(
                    f"[완료] {file_path.name}"
                )
                print(
                    f"  신규: {inserted_count}건"
                )
                print(
                    f"  갱신: {updated_count}건"
                )
                print(
                    f"  건너뜀: {skipped_count}건"
                )

            except (
                json.JSONDecodeError,
                OSError,
                ValueError,
            ) as error:
                db.rollback()

                print(
                    f"[파일 실패] {file_path.name}"
                )
                print(
                    f"원인: {error}"
                )

                total_skipped += 1

        final_count = db.query(Location).count()

        print()
        print("=" * 50)
        print("[전체 적재 결과]")
        print(
            f"신규 등록: {total_inserted}건"
        )
        print(
            f"기존 갱신: {total_updated}건"
        )
        print(
            f"건너뜀: {total_skipped}건"
        )
        print(
            f"DB 전체 지역정보: {final_count}건"
        )
        print("=" * 50)

        return 0

    except Exception as error:
        db.rollback()

        print()
        print(
            "[실패] 데이터 적재 중 "
            "예상하지 못한 오류가 발생했습니다."
        )
        print(
            f"오류 내용: {error}"
        )

        return 1

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())