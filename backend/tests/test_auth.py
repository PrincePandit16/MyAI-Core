from collections.abc import Iterator

import pytest
from app.api.auth import get_current_user
from app.core.security import verify_password
from app.db.session import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides.pop(get_current_user, None)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session_factory = sessionmaker(bind=engine)

    def override_get_db() -> Iterator[Session]:
        with test_session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_register_and_login(client: TestClient) -> None:
    registration = client.post(
        "/auth/register",
        json={"email": "person@example.com", "password": "correct-horse"},
    )

    assert registration.status_code == 201
    assert registration.json()["email"] == "person@example.com"
    assert "hashed_password" not in registration.json()

    login = client.post(
        "/auth/login",
        json={"email": "person@example.com", "password": "correct-horse"},
    )

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    assert login.json()["access_token"]

    current_user = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert current_user.status_code == 200
    assert current_user.json() == registration.json()


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    registration_data = {"email": "person@example.com", "password": "correct-horse"}
    assert client.post("/auth/register", json=registration_data).status_code == 201

    response = client.post("/auth/register", json=registration_data)

    assert response.status_code == 409


def test_login_rejects_incorrect_password(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "person@example.com", "password": "correct-horse"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "person@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_current_user_requires_a_valid_token(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_verify_password_accepts_existing_argon2_hash() -> None:
    password = "correct-horse"
    legacy_hash = PasswordHash.recommended().hash(password)

    assert verify_password(password, legacy_hash)
    assert not verify_password("wrong-password", legacy_hash)
