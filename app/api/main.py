from time import perf_counter
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException

from closed_llm_platform.audit import create_chat_audit_event, write_audit_event_jsonl
from closed_llm_platform.config import settings
from closed_llm_platform.guardrails import inspect_prompt
from closed_llm_platform.ollama_client import generate_ollama_response
from closed_llm_platform.privacy import mask_pii
from closed_llm_platform.rag import (
    build_rag_prompt,
    inspect_retrieved_context,
    read_rag_index,
    retrieve_chunks,
    write_rag_index,
)
from closed_llm_platform.schemas import ChatRequest, ChatResponse, DocumentIngestResponse

app = FastAPI(title="Closed Local LLM Platform API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents/ingest", response_model=DocumentIngestResponse)
def ingest_documents() -> DocumentIngestResponse:
    chunks = write_rag_index(settings.sample_docs_path, settings.rag_index_path)
    document_count = len({chunk.document_id for chunk in chunks})
    return DocumentIngestResponse(
        document_count=document_count,
        chunk_count=len(chunks),
        index_path=settings.rag_index_path,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    started = perf_counter()
    request_id = str(uuid4())
    guardrail = inspect_prompt(request.message)
    redacted_prompt = mask_pii(request.message)
    rag_used = request.use_rag
    citations: list[str] = []
    retrieved_document_ids: list[str] = []
    retrieval_guardrail_status = "not_applicable"
    retrieval_guardrail_reasons: list[str] = []
    model_prompt = request.message

    if request.use_rag:
        chunks = read_rag_index(settings.rag_index_path)
        retrieval_results = retrieve_chunks(request.message, chunks)
        retrieved_chunks = [result.chunk for result in retrieval_results]
        retrieval_guardrail = inspect_retrieved_context(retrieved_chunks)
        citations = [chunk.citation for chunk in retrieved_chunks]
        retrieved_document_ids = list(
            dict.fromkeys(chunk.document_id for chunk in retrieved_chunks)
        )
        retrieval_guardrail_status = retrieval_guardrail.status
        retrieval_guardrail_reasons = retrieval_guardrail.reasons
        model_prompt = build_rag_prompt(request.message, retrieved_chunks)

    try:
        message = await generate_ollama_response(model_prompt)
    except httpx.HTTPError as exc:
        latency_ms = int((perf_counter() - started) * 1000)
        audit_event = create_chat_audit_event(
            request_id=request_id,
            model=settings.ollama_model,
            prompt=request.message,
            response=None,
            redacted_prompt=redacted_prompt,
            redacted_response=None,
            guardrail=guardrail,
            latency_ms=latency_ms,
            outcome="ollama_error",
            rag_used=rag_used,
            retrieved_document_ids=retrieved_document_ids,
            citations=citations,
            retrieval_guardrail_decision=retrieval_guardrail_status,
            retrieval_guardrail_reasons=retrieval_guardrail_reasons,
        )
        write_audit_event_jsonl(audit_event, settings.audit_log_path)
        raise HTTPException(
            status_code=502,
            detail="Ollama request failed; check OLLAMA_BASE_URL and OLLAMA_MODEL.",
        ) from exc

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
        rag_used=rag_used,
        retrieved_document_ids=retrieved_document_ids,
        citations=citations,
        retrieval_guardrail_decision=retrieval_guardrail_status,
        retrieval_guardrail_reasons=retrieval_guardrail_reasons,
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
        rag_used=rag_used,
        citations=citations,
        retrieved_document_ids=retrieved_document_ids,
        retrieval_guardrail_status=retrieval_guardrail_status,
        retrieval_guardrail_reasons=retrieval_guardrail_reasons,
    )
