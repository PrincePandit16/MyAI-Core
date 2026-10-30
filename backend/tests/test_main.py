from collections.abc import Iterator
from unittest.mock import AsyncMock, patch

import pytest
from app.api.auth import get_current_user
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def authenticated_chat_user() -> Iterator[None]:
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1, email="test@example.com"
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_calls_llm_client() -> None:
    with patch("app.main.llm_client.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "Mocked LLM Response"

        response = client.post(
            "/api/chat",
            json={"session_id": "test-session", "prompt": "Hello"},
        )

        assert response.status_code == 200
        assert response.json() == {"response": "Mocked LLM Response"}
        mock_generate.assert_called_once_with("Hello")


def test_chat_handles_llm_error() -> None:
    with patch("app.main.llm_client.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = RuntimeError("LLM Failed")

        response = client.post(
            "/api/chat",
            json={"session_id": "test-session", "prompt": "Hello"},
        )

        assert response.status_code == 502
        assert response.json() == {"detail": "LLM generation failed"}


def test_chat_requires_session_id_and_prompt() -> None:
    response = client.post("/api/chat", json={"prompt": "Hello"})

    assert response.status_code == 422
