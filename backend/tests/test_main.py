from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)


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
