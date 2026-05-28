# Architecture

This document describes the intended architecture for the Closed Local LLM Platform before M1 implementation.

The architecture is intentionally staged. M1 creates the smallest runnable path. Later milestones add security, retrieval, auditability, and access control.

## Goals

- Understand how to place a FastAPI gateway between a UI and a local LLM runtime.
- Keep model inference local or closed-network by default.
- Establish a clean place for future guardrails, PII masking, RAG, audit logging, and RBAC.
- Keep the first implementation small enough to run and verify locally.
- Document design trade-offs as the system evolves.

## Non-Goals for M1

M1 will not implement:

- production authentication
- full RBAC
- full RAG ingestion/retrieval
- durable audit log storage
- advanced prompt injection detection
- production-grade PII detection
- model evaluation framework
- external deployment

Those are intentionally deferred so the basic UI/API/Ollama path can work first.

## M1 Logical Architecture

```mermaid
flowchart LR
  Browser[Browser] --> UI[Streamlit UI]
  UI -->|HTTP JSON| API[FastAPI Gateway]
  API -->|GET /health| Health[Health Handler]
  API -->|POST /chat| Chat[Chat Handler]
  Chat -->|HTTP API| Ollama[Ollama Local Runtime]
  Ollama -->|LLM response| Chat
  Chat -->|JSON response| UI
```

M1 uses Streamlit for the UI entrypoint. Next.js can be revisited in a later UI milestone if a richer frontend is useful.

## M1 Container / Runtime View

Exact ports may change during implementation, but the intended local development shape is:

```mermaid
flowchart TB
  subgraph DevMachine[Developer machine]
    Browser[Browser]

    subgraph Compose[Docker Compose project]
      StreamlitContainer[streamlit\nStreamlit UI]
      ApiContainer[api\nFastAPI]
    end

    OllamaRuntime[Ollama\nhost service for M1]
  end

  Browser -->|localhost:8501| StreamlitContainer
  StreamlitContainer -->|API_BASE_URL| ApiContainer
  ApiContainer -->|Ollama API| OllamaRuntime
```

Implementation decision to make in M1:

- Option A: run Ollama on the host and document it as a prerequisite.
- Option B: include Ollama in `docker-compose.yml`.

M1 can choose either, but the README must clearly document the chosen path.

## Component Responsibilities

### Streamlit UI

M1 responsibility:

- Render a minimal chat interface.
- Send a prompt to the FastAPI gateway.
- Display the response, model name, request ID, or error state.

Later responsibility:

- Show citations for RAG answers.
- Show role-aware controls if needed.
- Surface trace/audit IDs for debugging.

Next.js was part of the initial sketch, but M1 now uses Streamlit to match the requested Python/uv/src-layout project structure.

### FastAPI Gateway

M1 responsibility:

- Expose `GET /health`.
- Expose a basic chat endpoint.
- Call Ollama using a configured base URL and model name.
- Return structured JSON responses.

Later responsibility:

- Enforce authentication and RBAC.
- Apply prompt injection checks.
- Mask or redact PII before persistence and possibly before model calls.
- Orchestrate RAG retrieval and citation formatting.
- Write audit events.
- Add request IDs and observability hooks.

### Ollama Runtime

M1 responsibility:

- Provide local LLM inference.
- Be reachable from the API process.

Later responsibility:

- Support model configuration experiments.
- Provide a stable local inference target for regression prompts.

Ollama should not be exposed as the main user-facing API. The FastAPI gateway is the control point.

### Future Guardrails Package

Planned responsibility:

- Detect obvious prompt injection patterns.
- Separate user instructions from retrieved document content.
- Produce inspectable guardrail decisions.

This should be simple and explainable first. Avoid an opaque policy engine until the project needs it.

### Future RAG Package

Planned responsibility:

- Ingest synthetic sample documents.
- Chunk documents.
- Store embeddings or searchable representations.
- Retrieve relevant chunks.
- Return citations with answers.

RAG should integrate with RBAC later, so retrieval must eventually consider document permissions.

### Future Audit Store

Planned responsibility:

- Record request metadata, actor, role, action, model, timestamps, guardrail decisions, document IDs, and outcome.
- Avoid storing raw secrets or unnecessary PII.
- Support auditor/admin review.

## Data Flow: M1 Chat

```mermaid
sequenceDiagram
  participant U as User
  participant W as Next.js UI
  participant A as FastAPI Gateway
  participant O as Ollama

  U->>W: Type message
  W->>A: POST /chat {message}
  A->>A: Validate minimal request shape
  A->>O: Generate response
  O-->>A: Model output
  A-->>W: {message, model, request_id?}
  W-->>U: Display response
```

## Data Flow: Later Secured/RAG Chat

```mermaid
sequenceDiagram
  participant U as User
  participant W as Next.js UI
  participant A as FastAPI Gateway
  participant R as RBAC
  participant G as Guardrails/PII
  participant V as Retriever
  participant O as Ollama
  participant L as Audit Log

  U->>W: Ask question
  W->>A: POST /chat with identity/session
  A->>R: Check role and permissions
  R-->>A: Allowed scope
  A->>G: Inspect prompt and mask sensitive fields
  A->>V: Retrieve allowed context
  V-->>A: Chunks + citations
  A->>O: Prompt with allowed context
  O-->>A: Answer
  A->>G: Inspect response
  A->>L: Write audit event
  A-->>W: Answer + citations + audit/request id
```

## Configuration Principles

Use explicit environment variables for runtime choices:

- API host/port
- web API base URL
- Ollama base URL
- Ollama model name
- log level
- future database URL

Do not hard-code machine-specific paths or private values.

## Security Boundaries

Primary boundary:

- Users interact with the UI/API, not directly with Ollama.

Future boundaries:

- user/admin/auditor roles
- document-level access for RAG
- audit log read restrictions
- local-only Ollama access
- sanitized logs

## M1 Acceptance Criteria Mapping

| Requirement | Architecture implication |
|-------------|--------------------------|
| Streamlit UI skeleton | `app/streamlit` executable UI entrypoint |
| FastAPI API skeleton | `app/api` executable API entrypoint |
| Reusable Python code | `src/closed_llm_platform` package |
| `/health` endpoint | API health handler |
| Docker Compose wiring | `compose.yml` with local reproducible streamlit + api services |
| Ollama connection path | API can reach configured host Ollama endpoint |
| basic chat path | Streamlit -> API -> Ollama -> API -> Streamlit |
| README with Mermaid architecture | README diagram stays aligned with this file |

## Open Decisions for M1

- Ollama runs as host service for M1; Compose-managed Ollama is deferred.
- Exact route shape for `POST /chat`.
- uv and src-layout are the Python project standard.
- Streamlit is the M1 UI; Next.js is deferred.
- Minimal test framework setup in M1.

These should be resolved in the M1 implementation plan before application code is written.
