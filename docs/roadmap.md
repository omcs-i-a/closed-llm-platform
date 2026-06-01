# Roadmap

This roadmap keeps the project milestone-bound. The first goal is not to build a complete platform, but to create a small runnable system that makes later security and RAG work concrete.

## Current State

Status: M3 implemented and locally verified.

Created design targets:

- `README.md`
- `AGENTS.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/threat-model.md`

M1 includes a runnable FastAPI gateway, Streamlit UI, Docker/Compose wiring,
and a host-Ollama chat path. M2 adds prompt injection heuristics, PII masking for audit summaries, and local JSONL audit events. M3 adds synthetic sample documents, local JSON RAG ingestion/retrieval, citations, and indirect prompt-injection metadata for retrieved text. The current verified model for local smoke testing is
`qwen3:8b`; change `OLLAMA_MODEL` if your local Ollama runtime uses another model.

## Milestone Principles

- Keep each milestone runnable and verifiable.
- Add security controls in understandable layers.
- Prefer synthetic sample data.
- Avoid jumping to production complexity before the basic path works.
- Keep README and architecture docs synchronized with implementation.

## M1: Smallest Runnable Local System

### Learning Goal

Understand the basic closed/local LLM application path:

```text
Streamlit UI -> FastAPI gateway -> Ollama local runtime -> response back to UI
```

M1 uses a Python src-layout repository with uv, `app/` executable entrypoints, root `tests/`, Docker/Compose, and VS Code devcontainer support.

### Scope

- Streamlit UI skeleton
- FastAPI API skeleton
- `GET /health`
- uv project setup with `pyproject.toml` and `uv.lock`
- Docker/Compose wiring with `compose.yml`
- VS Code devcontainer support
- Ollama connection path
- basic chat request/response path
- README with Mermaid architecture

### Expected Files / Areas

Likely files to create during M1:

```text
.devcontainer/
  devcontainer.json
.github/
  ISSUE_TEMPLATE/
  PULL_REQUEST_TEMPLATE.md
.streamlit/
  config.toml
app/
  api/
    main.py
  streamlit/
    main.py
src/
  closed_llm_platform/
    config.py
    schemas.py
    ollama_client.py
    chat_service.py
tests/
  test_health.py
  test_chat.py
  test_ollama_client.py
scripts/
  smoke_api.py
data/
model/
notebook/
outputs/
Dockerfile
compose.yml
pyproject.toml
uv.lock
.env.example
.gitignore
```

Exact paths should be confirmed in the M1 implementation plan.

### Acceptance Criteria

- [x] `docker compose -f compose.yml up --build` starts the local services.
- [x] FastAPI `GET /health` returns HTTP 200.
- [x] UI can send a chat request to the API.
- [x] API can call Ollama, with Ollama documented as a host service prerequisite.
- [x] README explains why local/closed LLM design matters.
- [x] No secrets or real personal data are committed.

### Suggested Verification Commands

```bash
# Python setup and tests
uv sync
uv run pytest -q

# Start API
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Health check
curl -i http://localhost:8000/health

# Start Streamlit UI
uv run streamlit run app/streamlit/main.py

# Compose smoke test
docker compose -f compose.yml up --build
```

### M1 Implementation Plan

Before writing code, create a concrete M1 plan with:

- exact files
- small tasks
- commands
- expected outputs
- verification steps
- commit points

A good M1 plan should choose:

- Ollama host vs Compose service
- Python dependency management approach
- frontend package manager
- API route schemas
- minimal test strategy

## M2: Guardrails, PII Masking, and Audit Logging Baseline

### Learning Goal

Understand how a gateway can become a policy and accountability layer instead of a thin model proxy.

### Scope

- Prompt injection heuristic baseline
- Japanese and English prompt injection heuristic baseline
- PII masking/redaction baseline
- Audit log schema
- Request/response metadata logging
- Clear handling rules for what must not be logged

### Possible Components

```text
src/closed_llm_platform/audit.py
src/closed_llm_platform/privacy.py
src/closed_llm_platform/guardrails.py
```

### Acceptance Criteria

- [x] Chat request passes through a visible guardrail decision step.
- [x] Obvious injection examples are flagged or annotated.
- [x] Obvious Japanese and English injection examples are covered by tests.
- [x] Basic PII examples are masked before audit persistence.
- [x] Audit event schema is documented.
- [x] Logs avoid raw secrets and unnecessary PII.

### Example Audit Fields

- event_id
- request_id
- timestamp
- actor_id or anonymous/session placeholder
- role
- action
- model
- prompt_hash or redacted prompt summary
- guardrail_decision
- pii_masking_applied
- document_ids, later for RAG
- outcome
- latency_ms

## M3: RAG with Citations

### Learning Goal

Understand how retrieval changes the safety, permissions, and answer-quality problem.

### Scope

- Synthetic sample documents
- Ingestion script
- Chunking strategy
- Retrieval path
- Answer citations
- Clear representation of retrieved context in audit logs
- Japanese and English injection corpus for user prompts and retrieved text
- Indirect prompt injection detection for retrieved RAG text
- Strong prompt construction separation between system instructions, user input, and retrieved context

### Acceptance Criteria

- [x] Sample documents can be ingested reproducibly.
- [x] Chat can optionally answer using retrieved context.
- [x] Response includes citations or document references.
- [x] Prompt construction separates user instructions from retrieved content.
- [x] Retrieved text is treated as untrusted data and checked for indirect prompt injection signals.
- [x] Japanese and English injection corpus examples are included in RAG safety tests.
- [x] Threat model is updated for RAG-specific risks.

## M4: RBAC and Observability

### Learning Goal

Understand how access control and operational visibility affect LLM platform design.

### Scope

- Basic roles: `user`, `admin`, `auditor`
- Role-aware API behavior
- Document-level access boundary for RAG
- Local observability/tracing experiment
- Audit review path
- Severity levels for guardrail decisions
- Block / warn / annotate policy for guardrail outcomes
- Rule-based classifier plus optional LLM-based classifier comparison

### Acceptance Criteria

- Role is represented in request context.
- User/admin/auditor capabilities are documented and enforced in at least one endpoint.
- RAG retrieval respects document access metadata.
- Audit events can be inspected by the appropriate role.
- Guardrail decisions expose severity and policy action.
- Block / warn / annotate behavior is documented and tested for representative Japanese and English cases.
- README documents operational limitations.

## Later Ideas

Only consider after M1-M4 are working and documented.

- Regression prompt suite
- Offline evaluation examples
- Better prompt injection benchmark cases beyond the initial Japanese/English corpus
- Langfuse or local tracing integration
- Model comparison via multiple Ollama models
- Admin UI for audit and settings
- CI checks for backend and frontend
- More realistic document permission model

## Quality Bar Before Sharing

Before the repository is considered ready to share:

- README quick start works from a fresh checkout.
- Architecture diagram matches the implementation.
- At least one backend verification command exists.
- At least one frontend verification command exists.
- Docker Compose path is reproducible.
- Threat model is specific to this project.
- Audit log fields are documented.
- Limitations are honest.
