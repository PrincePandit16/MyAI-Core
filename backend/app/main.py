import logging

from app.api.auth import get_current_user
from app.api.auth import router as auth_router
from app.core.config import settings
from app.core.security.logging_utils import RedactingFormatter
from app.models.user import User
from app.services.llm_client import llm_client
from fastapi import Depends, FastAPI, HTTPException
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel

# Setup Logging with Redaction
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# Apply redacting formatter to all handlers
for handler in logging.root.handlers:
    handler.setFormatter(RedactingFormatter())

logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name)

# Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"],
)
LLM_RESPONSE_TIME = Histogram(
    "llm_response_seconds", "Time spent generating LLM response"
)

app.include_router(auth_router)

# Expose Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


class ChatRequest(BaseModel):
    session_id: str
    prompt: str


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, current_user: User = Depends(get_current_user)
) -> ChatResponse:
    logger.info("Received chat request for session %s", request.session_id)
    try:
        with LLM_RESPONSE_TIME.time():
            response_text = await llm_client.generate(request.prompt)
        HTTP_REQUESTS_TOTAL.labels(
            method="POST", endpoint="/api/chat", http_status="200"
        ).inc()
        return ChatResponse(response=response_text)
    except Exception as exc:
        logger.exception("Error during LLM generation")
        HTTP_REQUESTS_TOTAL.labels(
            method="POST", endpoint="/api/chat", http_status="502"
        ).inc()
        raise HTTPException(
            status_code=502,
            detail="LLM generation failed",
        ) from exc
