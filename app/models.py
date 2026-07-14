from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Location(Base):
    __tablename__ = "locations"

    content_id = Column(String, primary_key=True, index=True)       # 원본 JSON: contentid (TourAPI 콘텐츠 고유 ID)
    region = Column(String, nullable=False)                         # 최상위 region (수집 지역, 현재는 서울)
    content_type_id = Column(String, nullable=False)                # 원본: contenttypeid (콘텐츠 유형 코드)
    category = Column(String, nullable=False)                       # 최상위 contentType (관광지·문화시설 등 한글 유형)
    title = Column(String, nullable=False, index=True)              # 원본: title (장소명)
    addr1 = Column(String, nullable=True)                           # 원본: addr1 (기본 주소)
    addr2 = Column(String, nullable=True)                           # 원본: addr2 (상세 주소)
    zipcode = Column(String, nullable=True)                         # 원본: zipcode (우편번호)
    tel = Column(String, nullable=True)                             # 원본: tel (전화번호)
    longitude = Column(Float, nullable=True)                        # 원본: mapx (경도)
    latitude = Column(Float, nullable=True)                         # 원본: mapy (위도)
    map_level = Column(String, nullable=True)                       # 원본: mlevel (지도 레벨)
    area_code = Column(String, nullable=True)                       # 원본: areacode (지역 코드)
    sigungu_code = Column(String, nullable=True)                    # 원본: sigungucode (시군구 코드)
    legal_region_code = Column(String, nullable=True)               # 원본: lDongRegnCd (법정동 지역 코드)
    legal_sigungu_code = Column(String, nullable=True)              # 원본: lDongSignguCd (법정동 시군구 코드)
    cat1 = Column(String, nullable=True)                            # 원본: cat1 (대분류 코드)
    cat2 = Column(String, nullable=True)                            # 원본: cat2 (중분류 코드)
    cat3 = Column(String, nullable=True)                            # 원본: cat3 (소분류 코드)
    class_system1 = Column(String, nullable=True)                   # 원본: lclsSystm1 (분류 체계 1)
    class_system2 = Column(String, nullable=True)                   # 원본: lclsSystm2 (분류 체계 2)
    class_system3 = Column(String, nullable=True)                   # 원본: lclsSystm3 (분류 체계 3)
    first_image = Column(String, nullable=True)                     # 원본: firstimage (대표 이미지 URL)
    thumbnail_image = Column(String, nullable=True)                 # 원본: firstimage2 (썸네일 이미지 URL)
    copyright_code = Column(String, nullable=True)                  # 원본: cpyrhtDivCd (저작권 구분 코드)
    source_created_at = Column(String, nullable=True)               # 원본: createdtime (원본 최초 등록 시각, TEXT)
    source_modified_at = Column(String, nullable=True)              # 원본: modifiedtime (원본 최종 수정 시각, TEXT)
    source_file = Column(String, nullable=True)                     # 파일명적재 출처 JSON 파일명
    imported_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # SQLite 적재 시각


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)                       # 관광지·문화시설·자유 등
    title = Column(String, nullable=False)                          # 게시글 제목
    content = Column(Text, nullable=False)                          # 게시글 본문
    edit_password = Column(String, nullable=False)                  # 수정·삭제용 비밀번호
    view_count = Column(Integer, nullable=False, default=0)         # 조회수
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)                     # 작성 시각
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)  # 수정 시각

class PostTag(Base):
    __tablename__ = "post_tags"

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag = Column(Text, primary_key=True)

    post = relationship("Post", back_populates="tags")