from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.session import AssistantSession


def create_session(db: Session, *, user_id: int) -> AssistantSession:
    assistant_session = AssistantSession(user_id=user_id)
    db.add(assistant_session)
    db.commit()
    db.refresh(assistant_session)
    return assistant_session


def get_session(db: Session, session_id: int) -> AssistantSession | None:
    return db.get(AssistantSession, session_id)


def get_user_sessions(
    db: Session,
    user_id: int,
    *,
    offset: int = 0,
    limit: int = 100,
) -> list[AssistantSession]:
    statement = (
        select(AssistantSession)
        .where(AssistantSession.user_id == user_id)
        .order_by(AssistantSession.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement))


def update_session(
    db: Session,
    assistant_session: AssistantSession,
    *,
    user_id: int | None = None,
) -> AssistantSession:
    if user_id is not None:
        assistant_session.user_id = user_id
    db.commit()
    db.refresh(assistant_session)
    return assistant_session


def delete_session(db: Session, assistant_session: AssistantSession) -> None:
    db.delete(assistant_session)
    db.commit()
