import asyncio
import logging
from typing import Protocol

import httpx
from app.core.config import Settings, settings

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    async def generate(self, prompt: str) -> str: ...


class LocalLlamaProvider:
    def __init__(
        self,
        binary_path: str,
        model_path: str,
        timeout: float,
        max_new_tokens: int,
    ):
        self.binary_path = binary_path
        self.model_path = model_path
        self.timeout = timeout
        self.max_new_tokens = max_new_tokens

    async def generate(self, prompt: str) -> str:
        if not self.model_path:
            raise RuntimeError("LLAMA_MODEL_PATH must be set when LLM_MODE=local_llama")

        process: asyncio.subprocess.Process | None = None
        try:
            process = await asyncio.create_subprocess_exec(
                self.binary_path,
                "-m",
                self.model_path,
                "--no-display-prompt",
                "--single-turn",
                "-n",
                str(self.max_new_tokens),
                "-p",
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout,
            )

            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(
                    "llama.cpp process failed with return code %s: %s",
                    process.returncode,
                    error_msg,
                )
                raise RuntimeError(f"llama.cpp failed: {error_msg}")

            return stdout.decode().strip()
        except asyncio.TimeoutError as exc:
            if process is not None and process.returncode is None:
                process.kill()
                await process.communicate()
            logger.error("llama.cpp process timed out after %s seconds", self.timeout)
            raise RuntimeError("llama.cpp generation timed out") from exc
        except asyncio.CancelledError:
            if process is not None and process.returncode is None:
                process.kill()
                await process.communicate()
            raise
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"llama.cpp binary not found: {self.binary_path}"
            ) from exc


class TGIHttpProvider:
    def __init__(
        self,
        endpoint: str,
        timeout: float,
        max_retries: int,
        max_new_tokens: int,
    ):
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_new_tokens = max_new_tokens

    async def generate(self, prompt: str) -> str:
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": self.max_new_tokens},
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.endpoint, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    if isinstance(data, list) and data:
                        data = data[0]
                    if isinstance(data, dict):
                        generated_text = data.get("generated_text")
                        if isinstance(generated_text, str):
                            return generated_text.strip()
                    raise RuntimeError("Unexpected TGI response format")
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if attempt == self.max_retries:
                    logger.error(
                        "TGI request failed after %s attempts: %s",
                        self.max_retries,
                        str(e),
                    )
                    raise RuntimeError(f"TGI request failed: {e}") from e
                logger.warning("TGI request attempt %s failed, retrying...", attempt)
                await asyncio.sleep(attempt)

        raise RuntimeError("TGI request failed")


class GroqProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.models_url = "https://api.groq.com/openai/v1/models"

    async def get_available_models(self) -> list[str]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.models_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return [model["id"] for model in data.get("data", [])]
        except Exception as e:
            logger.error("Failed to fetch available models from Groq: %s", str(e))
            return []

    async def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # First, try to find an available model from the account
        available = await self.get_available_models()

        model_to_use = None
        if available:
            # Try each available model until one works without requiring terms acceptance
            for model_name in available:
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                }
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            self.url, headers=headers, json=payload
                        )
                        if response.status_code == 200:
                            data = response.json()
                            return data["choices"][0]["message"]["content"].strip()
                        elif "model_terms_required" in response.text:
                            logger.warning(
                                "Model %s requires terms acceptance, skipping...",
                                model_name,
                            )
                            continue
                        else:
                            logger.warning(
                                "Model %s returned error %s, skipping...",
                                model_name,
                                response.status_code,
                            )
                            continue
                except Exception as e:
                    logger.warning("Error trying model %s: %s", model_name, str(e))
                    continue

        # Final fallback if no auto-detected models worked
        model_to_use = "llama-3.3-70b-versatile"
        logger.info("Trying final fallback model: %s", model_to_use)

        payload = {
            "model": model_to_use,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.url, headers=headers, json=payload)
                if response.status_code != 200:
                    raise RuntimeError(f"Final fallback failed: {response.text}")
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"All attempts failed. Final error: {str(e)}")


class LLMClient:
    def __init__(self, config: Settings | None = None):
        config = config or settings
        if config.llm_mode == "local_llama":
            self.provider: LLMProvider = LocalLlamaProvider(
                config.llama_binary_path,
                config.llama_model_path,
                config.llm_timeout_seconds,
                config.llm_max_new_tokens,
            )
        elif config.llm_mode == "http_tgi":
            self.provider = TGIHttpProvider(
                config.tgi_endpoint,
                config.llm_timeout_seconds,
                config.llm_max_retries,
                config.llm_max_new_tokens,
            )
        elif config.llm_mode == "groq":
            self.provider = GroqProvider(config.groq_api_key)
        else:
            raise ValueError(f"Unsupported LLM mode: {config.llm_mode}")

    async def generate(self, prompt: str) -> str:
        return await self.provider.generate(prompt)


# Singleton instance
llm_client = LLMClient()
