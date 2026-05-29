import hashlib
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from closed_llm_platform.guardrails import GuardrailDecision
from closed_llm_platform.privacy import MaskingResult


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor_id: str = "anonymous"
    role: str = "user"
    action: str
    route: str
    model: str
    prompt_hash: str
    redacted_prompt_summary: str
    response_hash: str | None = None
    redacted_response_summary: str | None = None
    guardrail_decision: str
    guardrail_reasons: list[str]
    pii_masking_applied: bool
    pii_types: list[str]
    outcome: str
    latency_ms: int


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _summary(text: str, max_length: int = 240) -> str:
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 1]}…"


def create_chat_audit_event(
    *,
    request_id: str,
    model: str,
    prompt: str,
    response: str | None,
    redacted_prompt: MaskingResult,
    redacted_response: MaskingResult | None,
    guardrail: GuardrailDecision,
    latency_ms: int,
    outcome: str,
) -> AuditEvent:
    response_pii_types = redacted_response.pii_types if redacted_response else []
    pii_types = list(dict.fromkeys(redacted_prompt.pii_types + response_pii_types))
    return AuditEvent(
        request_id=request_id,
        action="chat",
        route="/chat",
        model=model,
        prompt_hash=_hash_text(prompt),
        redacted_prompt_summary=_summary(redacted_prompt.text),
        response_hash=_hash_text(response) if response is not None else None,
        redacted_response_summary=_summary(redacted_response.text) if redacted_response else None,
        guardrail_decision=guardrail.status,
        guardrail_reasons=guardrail.reasons,
        pii_masking_applied=bool(pii_types),
        pii_types=pii_types,
        outcome=outcome,
        latency_ms=latency_ms,
    )


def write_audit_event_jsonl(event: AuditEvent, path: str | Path) -> None:
    audit_path = Path(path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(event.model_dump_json() + "\n")
