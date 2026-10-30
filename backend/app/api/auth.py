from collections import defaultdict
from threading import Lock
from time import monotonic
from typing import Annotated

import jwt
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)
_login_failures: dict[str, list[float]] = defaultdict(list)
_login_failures_lock = Lock()
_LOGIN_WINDOW_SECONDS = 15 * 60
_LOGIN_LIMIT = 5


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Passwords must not exceed 72 UTF-8 bytes")
        return password


class UserResponse(BaseModel):
    id: int
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(request: AuthRequest, db: Annotated[Session, Depends(get_db)]) -> User:
    email = str(request.email).lower()
    if user_crud.get_user_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    try:
        return user_crud.create_user(
            db,
            email=email,
            hashed_password=hash_password(request.password),
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(
    request: AuthRequest, response: Response, db: Annotated[Session, Depends(get_db)]
) -> TokenResponse:
    email = str(request.email).lower()
    now = monotonic()
    with _login_failures_lock:
        recent = [
            timestamp
            for timestamp in _login_failures[email]
            if now - timestamp < _LOGIN_WINDOW_SECONDS
        ]
        _login_failures[email] = recent
        if len(recent) >= _LOGIN_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts; try again later",
            )

    user = user_crud.get_user_by_email(db, email)
    if user is None or not verify_password(request.password, user.hashed_password):
        with _login_failures_lock:
            _login_failures[email].append(monotonic())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    with _login_failures_lock:
        _login_failures.pop(email, None)

    token = create_access_token(subject=str(user.id))
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )
    return TokenResponse(access_token=token)


def get_current_user(
    http_request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = (
        credentials.credentials
        if credentials is not None
        else http_request.cookies.get("access_token")
    )
    if token is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
        )
        subject = payload.get("sub")
        user_id = int(subject) if isinstance(subject, str) else None
    except (jwt.InvalidTokenError, ValueError):
        raise unauthorized from None

    if user_id is None:
        raise unauthorized

    user = user_crud.get_user(db, user_id)
    if user is None:
        raise unauthorized
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(
        "access_token", httponly=True, secure=settings.cookie_secure, samesite="lax"
    )
    return response


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
