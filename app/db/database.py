from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False,
    },
)


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(
    dbapi_connection,
    connection_record,
) -> None:
    """SQLite 외래키 제약조건을 활성화한다."""

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """요청별 DB 세션을 생성하고 종료한다."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """등록된 SQLAlchemy 모델을 기준으로 테이블을 생성한다."""

    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)