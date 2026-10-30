from collections.abc import Iterator
from datetime import datetime

import pytest
from app.crud import session as session_crud
from app.crud import user as user_crud
from app.db.session import Base
from app.models import AssistantSession, User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        yield db
    engine.dispose()


def test_user_and_session_crud(db_session: Session) -> None:
    user = user_crud.create_user(
        db_session,
        email="person@example.com",
        hashed_password="argon2-hash",
    )

    assert user_crud.get_user(db_session, user.id) is user
    assert user_crud.get_user_by_email(db_session, user.email) is user

    assistant_session = session_crud.create_session(db_session, user_id=user.id)
    assert isinstance(assistant_session.created_at, datetime)
    assert (
        session_crud.get_session(db_session, assistant_session.id) is assistant_session
    )
    assert session_crud.get_user_sessions(db_session, user.id) == [assistant_session]

    user_crud.update_user(db_session, user, email="updated@example.com")
    assert user_crud.get_user_by_email(db_session, "updated@example.com") is user

    session_crud.delete_session(db_session, assistant_session)
    assert session_crud.get_session(db_session, assistant_session.id) is None
    user_crud.delete_user(db_session, user)
    assert user_crud.get_user(db_session, user.id) is None
