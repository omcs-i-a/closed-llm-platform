from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    message: str
    model: str
    request_id: str
    guardrail_status: str
    guardrail_reasons: list[str]
    pii_masking_applied: bool
    audit_event_id: str
