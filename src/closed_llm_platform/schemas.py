from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    use_rag: bool = False


class ChatResponse(BaseModel):
    message: str
    model: str
    request_id: str
    guardrail_status: str
    guardrail_reasons: list[str]
    pii_masking_applied: bool
    audit_event_id: str
    rag_used: bool = False
    citations: list[str] = Field(default_factory=list)
    retrieved_document_ids: list[str] = Field(default_factory=list)
    retrieval_guardrail_status: str = "not_applicable"
    retrieval_guardrail_reasons: list[str] = Field(default_factory=list)


class DocumentIngestResponse(BaseModel):
    document_count: int
    chunk_count: int
    index_path: str
