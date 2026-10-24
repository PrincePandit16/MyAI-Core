import asyncio
import sys
from pathlib import Path

backend_path = str(Path(__file__).resolve().parents[1])
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.config import Settings
from app.services.llm_client import LLMClient

settings = Settings(_env_file=Path(backend_path) / ".env")
llm_client = LLMClient(settings)


async def test_llm_client() -> None:
    print(f"Testing LLMClient in mode: {settings.llm_mode}")

    test_prompt = "Hello, who are you?"
    try:
        print(f"Prompt: {test_prompt}")
        response = await llm_client.generate(test_prompt)
        print(f"Response: {response}")
        print("SUCCESS: LLMClient generated a response.")
    except Exception as exc:
        print(f"FAILURE: LLMClient failed with error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_llm_client())
