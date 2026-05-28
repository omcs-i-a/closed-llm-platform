from uuid import uuid4

from fastapi import FastAPI

from closed_llm_platform.config import settings
from closed_llm_platform.ollama_client import generate_ollama_response
from closed_llm_platform.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Closed Local LLM Platform API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    message = await generate_ollama_response(request.message)
    return ChatResponse(
        message=message,
        model=settings.ollama_model,
        request_id=str(uuid4()),
    )
