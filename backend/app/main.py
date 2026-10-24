import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.api.auth import router as auth_router
from app.core.config import settings
from app.services.llm_client import llm_client

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name)
app.include_router(auth_router)


class ChatRequest(BaseModel):
    session_id: str
    prompt: str


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    logger.info("Received chat request for session %s", request.session_id)
    try:
        response_text = await llm_client.generate(request.prompt)
        return ChatResponse(response=response_text)
    except Exception as exc:
        logger.exception("Error during LLM generation")
        raise HTTPException(
            status_code=502,
            detail="LLM generation failed",
        ) from exc
