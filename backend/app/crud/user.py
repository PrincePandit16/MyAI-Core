from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_user(db: Session, *, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def update_user(
    db: Session,
    user: User,
    *,
    email: str | None = None,
    hashed_password: str | None = None,
) -> User:
    if email is not None:
        user.email = email
    if hashed_password is not None:
        user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
