from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_echoes_prompt() -> None:
    response = client.post(
        "/api/chat",
        json={"session_id": "test-session", "prompt": "Hello"},
    )

    assert response.status_code == 200
    assert response.json() == {"response": "Hello"}


def test_chat_requires_session_id_and_prompt() -> None:
    response = client.post("/api/chat", json={"prompt": "Hello"})

    assert response.status_code == 422
