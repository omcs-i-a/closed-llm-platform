from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI

from closed_llm_platform.audit import create_chat_audit_event, write_audit_event_jsonl
from closed_llm_platform.config import settings
from closed_llm_platform.guardrails import inspect_prompt
from closed_llm_platform.ollama_client import generate_ollama_response
from closed_llm_platform.privacy import mask_pii
from closed_llm_platform.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Closed Local LLM Platform API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    started = perf_counter()
    request_id = str(uuid4())
    guardrail = inspect_prompt(request.message)
    redacted_prompt = mask_pii(request.message)

    message = await generate_ollama_response(request.message)
    redacted_response = mask_pii(message)
    latency_ms = int((perf_counter() - started) * 1000)
    audit_event = create_chat_audit_event(
        request_id=request_id,
        model=settings.ollama_model,
        prompt=request.message,
        response=message,
        redacted_prompt=redacted_prompt,
        redacted_response=redacted_response,
        guardrail=guardrail,
        latency_ms=latency_ms,
        outcome="success",
    )
    write_audit_event_jsonl(audit_event, settings.audit_log_path)

    return ChatResponse(
        message=message,
        model=settings.ollama_model,
        request_id=request_id,
        guardrail_status=guardrail.status,
        guardrail_reasons=guardrail.reasons,
        pii_masking_applied=audit_event.pii_masking_applied,
        audit_event_id=audit_event.event_id,
    )
