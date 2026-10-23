import logging

from fastapi import FastAPI
from pydantic import BaseModel

from app.api.auth import router as auth_router
from app.core.config import settings

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
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("Received chat request for session %s", request.session_id)
    return ChatResponse(response=request.prompt)
