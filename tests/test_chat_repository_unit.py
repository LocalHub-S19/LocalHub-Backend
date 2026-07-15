"""챗봇 전용 읽기 Repository 단위 테스트."""

from __future__ import annotations

import unittest

from sqlalchemy import func, select

from app.db.models.location import Location
from app.db.models.post import Post
from app.repositories.chat_search_repository import ChatSearchRepository
from tests.chat_test_support import create_test_session, seed_chat_test_data


class ChatSearchRepositoryUnitTest(unittest.TestCase):
    """운영 DB와 분리된 메모리 SQLite에서 검색 기능을 확인한다."""

    def setUp(self) -> None:
        self.db, self.engine = create_test_session()
        seed_chat_test_data(self.db)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_search_locations_by_category_district_and_keyword(self) -> None:
        rows = ChatSearchRepository.search_locations(
            db=self.db,
            category="문화시설",
            district="종로구",
            keywords=["박물관"],
            limit=5,
        )

        self.assertEqual([row.content_id for row in rows], ["loc-museum-1"])

    def test_search_locations_uses_content_type_mapping(self) -> None:
        target = self.db.get(Location, "loc-museum-1")
        self.assertIsNotNone(target)
        target.category = "기타표기"
        self.db.commit()

        rows = ChatSearchRepository.search_locations(
            db=self.db,
            category="문화시설",
            district=None,
            keywords=["박물관"],
            limit=5,
        )

        self.assertEqual([row.content_id for row in rows], ["loc-museum-1"])

    def test_search_festivals_returns_only_festival_data(self) -> None:
        rows = ChatSearchRepository.search_festivals(
            db=self.db,
            district="영등포구",
            keywords=["한강"],
            limit=5,
        )

        self.assertEqual([row.content_id for row in rows], ["loc-festival-1"])
        self.assertTrue(all(row.content_type_id == "15" for row in rows))

    def test_search_model_restaurants_excludes_normal_restaurant(self) -> None:
        rows = ChatSearchRepository.search_model_restaurants(
            db=self.db,
            district="종로구",
            keywords=["한식"],
            limit=5,
        )

        ids = [row.content_id for row in rows]
        self.assertIn("loc-model-restaurant-1", ids)
        self.assertNotIn("loc-normal-restaurant-1", ids)

    def test_search_posts_by_title_content_tag_and_district(self) -> None:
        by_title = ChatSearchRepository.search_posts(
            db=self.db,
            category=None,
            district=None,
            keywords=["남산"],
            limit=5,
        )
        self.assertEqual(by_title[0].title, "남산 야경 방문 후기")

        by_tag = ChatSearchRepository.search_posts(
            db=self.db,
            category=None,
            district=None,
            keywords=["야경"],
            limit=5,
        )
        self.assertEqual(by_tag[0].title, "남산 야경 방문 후기")

        by_district = ChatSearchRepository.search_posts(
            db=self.db,
            category="문화시설",
            district="종로구",
            keywords=["아이"],
            limit=5,
        )
        self.assertEqual(by_district[0].title, "종로구 박물관 방문기")

    def test_like_special_characters_are_escaped(self) -> None:
        percent_rows = ChatSearchRepository.search_locations(
            db=self.db,
            category=None,
            district=None,
            keywords=["%"],
            limit=10,
        )
        underscore_rows = ChatSearchRepository.search_locations(
            db=self.db,
            category=None,
            district=None,
            keywords=["_체험"],
            limit=10,
        )

        self.assertEqual(
            [row.content_id for row in percent_rows],
            ["loc-special-character-1"],
        )
        self.assertEqual(
            [row.content_id for row in underscore_rows],
            ["loc-special-character-1"],
        )

    def test_search_is_read_only(self) -> None:
        before_locations = self.db.scalar(select(func.count()).select_from(Location))
        before_posts = self.db.scalar(select(func.count()).select_from(Post))

        ChatSearchRepository.search_locations(
            db=self.db,
            category=None,
            district=None,
            keywords=[],
            limit=5,
        )
        ChatSearchRepository.search_posts(
            db=self.db,
            category=None,
            district=None,
            keywords=[],
            limit=5,
        )

        after_locations = self.db.scalar(select(func.count()).select_from(Location))
        after_posts = self.db.scalar(select(func.count()).select_from(Post))

        self.assertEqual(before_locations, after_locations)
        self.assertEqual(before_posts, after_posts)

    def test_limit_is_clamped_to_ten(self) -> None:
        self.assertEqual(ChatSearchRepository._normalize_limit(-3), 1)
        self.assertEqual(ChatSearchRepository._normalize_limit(5), 5)
        self.assertEqual(ChatSearchRepository._normalize_limit(99), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
