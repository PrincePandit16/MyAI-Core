import asyncio
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from app.core.config import Settings
from app.services.llm_client import (
    LLMClient,
    LocalLlamaProvider,
    TGIHttpProvider,
)


class FakeAsyncClient:
    def __init__(self, responses: list[httpx.Response | Exception]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, url: str, *, json: dict[str, object]) -> httpx.Response:
        self.calls.append((url, json))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_tgi_posts_prompt_and_returns_generated_text(monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = "http://localhost:8080/generate"
    request = httpx.Request("POST", endpoint)
    client = FakeAsyncClient(
        [httpx.Response(200, json={"generated_text": "  Answer  "}, request=request)]
    )
    timeouts: list[float] = []

    def make_client(*, timeout: float) -> FakeAsyncClient:
        timeouts.append(timeout)
        return client

    monkeypatch.setattr("app.services.llm_client.httpx.AsyncClient", make_client)
    provider = TGIHttpProvider(
        endpoint,
        timeout=12.0,
        max_retries=2,
        max_new_tokens=256,
    )

    response = asyncio.run(provider.generate("Hello"))

    assert response == "Answer"
    assert client.calls == [
        (
            endpoint,
            {
                "inputs": "Hello",
                "parameters": {"max_new_tokens": 256},
            },
        )
    ]
    assert timeouts == [12.0]


def test_tgi_retries_transient_request_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    endpoint = "http://localhost:8080/generate"
    request = httpx.Request("POST", endpoint)
    client = FakeAsyncClient(
        [
            httpx.ConnectError("server unavailable", request=request),
            httpx.Response(
                200,
                json=[{"generated_text": "Ready"}],
                request=request,
            ),
        ]
    )
    sleep = AsyncMock()
    monkeypatch.setattr("app.services.llm_client.httpx.AsyncClient", lambda **_: client)
    monkeypatch.setattr("app.services.llm_client.asyncio.sleep", sleep)
    provider = TGIHttpProvider(
        endpoint,
        timeout=5.0,
        max_retries=2,
        max_new_tokens=128,
    )

    response = asyncio.run(provider.generate("Hello"))

    assert response == "Ready"
    assert len(client.calls) == 2
    sleep.assert_awaited_once_with(1)


def test_tgi_reports_timeout_after_configured_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    endpoint = "http://localhost:8080/generate"
    request = httpx.Request("POST", endpoint)
    client = FakeAsyncClient([httpx.ReadTimeout("request timed out", request=request)])
    monkeypatch.setattr("app.services.llm_client.httpx.AsyncClient", lambda **_: client)
    provider = TGIHttpProvider(
        endpoint,
        timeout=0.1,
        max_retries=1,
        max_new_tokens=128,
    )

    with pytest.raises(RuntimeError, match="TGI request failed"):
        asyncio.run(provider.generate("Hello"))

    assert len(client.calls) == 1


def test_local_llama_runs_binary_with_model_and_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = AsyncMock()
    process.communicate.return_value = (b"Local answer\n", b"")
    process.returncode = 0
    create_process = AsyncMock(return_value=process)
    monkeypatch.setattr(
        "app.services.llm_client.asyncio.create_subprocess_exec",
        create_process,
    )
    provider = LocalLlamaProvider(
        binary_path="llama-cli",
        model_path="models/model.gguf",
        timeout=20.0,
        max_new_tokens=128,
    )

    response = asyncio.run(provider.generate("Hello"))

    assert response == "Local answer"
    args = create_process.await_args.args
    assert args == (
        "llama-cli",
        "-m",
        "models/model.gguf",
        "--no-display-prompt",
        "--single-turn",
        "-n",
        "128",
        "-p",
        "Hello",
    )
    process.communicate.assert_awaited_once()


def test_local_llama_kills_process_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = AsyncMock()
    process.returncode = None
    process.kill = Mock()
    process.communicate.side_effect = [
        asyncio.TimeoutError(),
        (b"", b""),
    ]
    monkeypatch.setattr(
        "app.services.llm_client.asyncio.create_subprocess_exec",
        AsyncMock(return_value=process),
    )
    provider = LocalLlamaProvider(
        "llama-cli",
        "model.gguf",
        timeout=0.01,
        max_new_tokens=64,
    )

    with pytest.raises(RuntimeError, match="generation timed out"):
        asyncio.run(provider.generate("Hello"))

    process.kill.assert_called_once_with()
    assert process.communicate.await_count == 2


def test_local_llama_requires_a_model_path() -> None:
    provider = LocalLlamaProvider(
        "llama-cli",
        "",
        timeout=20.0,
        max_new_tokens=64,
    )

    with pytest.raises(RuntimeError, match="LLAMA_MODEL_PATH"):
        asyncio.run(provider.generate("Hello"))


def test_llm_client_selects_configured_provider() -> None:
    config = Settings(
        _env_file=None,
        llm_mode="http_tgi",
        tgi_endpoint="http://tgi:8080/generate",
        llm_timeout_seconds=15.0,
        llm_max_retries=4,
        llm_max_new_tokens=128,
    )

    client = LLMClient(config)

    assert isinstance(client.provider, TGIHttpProvider)
    assert client.provider.endpoint == "http://tgi:8080/generate"
    assert client.provider.timeout == 15.0
    assert client.provider.max_retries == 4
    assert client.provider.max_new_tokens == 128
