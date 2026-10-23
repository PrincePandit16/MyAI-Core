from getpass import getpass

from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError

from app.crud.user import create_user
from app.db.session import SessionLocal


def main() -> None:
    email = input("Email: ").strip()
    password = getpass("Password: ")
    if not email or not password:
        raise ValueError("Email and password are required")

    hashed_password = PasswordHash.recommended().hash(password)
    with SessionLocal() as db:
        try:
            user = create_user(db, email=email, hashed_password=hashed_password)
        except IntegrityError as exc:
            db.rollback()
            raise ValueError(f"A user with email {email!r} may already exist") from exc

    print(f"Created user {user.id} ({user.email})")


if __name__ == "__main__":
    main()
