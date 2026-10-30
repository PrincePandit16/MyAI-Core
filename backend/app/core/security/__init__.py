from datetime import datetime, timedelta, timezone

import jwt
from app.core.config import settings
from passlib.context import CryptContext
from pwdlib import PasswordHash

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_legacy_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Passwords must not exceed 72 UTF-8 bytes")
    return _password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("$argon2"):
        return _legacy_password_hash.verify(password, hashed_password)
    if len(password.encode("utf-8")) > 72:
        return False
    return _password_context.verify(password, hashed_password)


def create_access_token(*, subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expires_at},
        settings.jwt_secret_key,
        algorithm="HS256",
    )
