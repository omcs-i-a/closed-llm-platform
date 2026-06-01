# M3 RAG with Citations Implementation Plan

> **For Hermes:** Use TDD for code changes and keep M3 small, local, and learning-first.

**Goal:** Add a minimal local RAG path with synthetic documents, reproducible ingestion, retrieval, citations, and indirect prompt-injection checks for retrieved text.

**Architecture:** Keep RAG dependency-light for M3: markdown sample documents are ingested into a local JSON index with deterministic chunk IDs and simple lexical scoring. FastAPI remains the control point and composes a separated prompt from system instructions, retrieved context, and user input. Retrieved text is treated as untrusted and inspected before prompt construction.

**Tech Stack:** Python 3.12, FastAPI, Streamlit, uv, pytest, ruff, local JSON files, Ollama.

---

## Requirement Reconciliation

- User asked to implement M3 now.
- `AGENTS.md` requires small milestone-bound changes and doc synchronization.
- `docs/roadmap.md` defines M3 as synthetic documents, ingestion, chunking, retrieval, citations, audit representation, bilingual injection corpus, indirect prompt-injection detection, and strong prompt separation.
- M4 RBAC, production auth, vector database, severity/policy engine, and durable DB are explicitly out of scope.

## Task 1: Add RAG data model and chunking tests

**Objective:** Define deterministic document/chunk data structures and chunk markdown sample documents.

**Files:**
- Create: `src/closed_llm_platform/rag.py`
- Create: `tests/test_rag.py`

**Steps:**
1. Write failing tests for markdown ingestion into chunks with source/title metadata.
2. Run `uv run pytest tests/test_rag.py::test_load_sample_documents_creates_chunks_with_citations -v` and confirm RED.
3. Implement dataclasses and markdown loader.
4. Run targeted test and full test suite.

## Task 2: Add retrieval and indirect injection checks

**Objective:** Retrieve relevant chunks and flag suspicious retrieved text without blocking the request.

**Files:**
- Modify: `src/closed_llm_platform/rag.py`
- Modify: `tests/test_rag.py`

**Steps:**
1. Write failing tests for lexical retrieval and Japanese/English indirect injection detection in retrieved chunks.
2. Implement simple token scoring and `inspect_retrieved_context()`.
3. Verify with targeted tests and full tests.

## Task 3: Add prompt construction separation

**Objective:** Construct the model prompt with explicit sections for system instructions, untrusted retrieved context, and user question.

**Files:**
- Modify: `src/closed_llm_platform/rag.py`
- Modify: `tests/test_rag.py`

**Steps:**
1. Write failing test that asserts prompt sections remain separate.
2. Implement `build_rag_prompt()`.
3. Verify targeted and full tests.

## Task 4: Integrate optional RAG into `/chat` and expose citations

**Objective:** Let `/chat` optionally use RAG and return citations/document IDs/retrieval guardrail metadata.

**Files:**
- Modify: `src/closed_llm_platform/schemas.py`
- Modify: `src/closed_llm_platform/ollama_client.py`
- Modify: `app/api/main.py`
- Modify: `tests/test_chat.py`

**Steps:**
1. Write failing API tests for `use_rag=true`, citations in response, separated prompt sent to Ollama, and indirect injection metadata.
2. Implement schema fields and API flow.
3. Verify targeted API tests and full tests.

## Task 5: Add reproducible ingestion script and endpoint

**Objective:** Provide `scripts/ingest_documents.py` and `POST /documents/ingest` for local sample document ingestion.

**Files:**
- Create: `scripts/ingest_documents.py`
- Modify: `app/api/main.py`
- Modify: `src/closed_llm_platform/schemas.py`
- Create/modify: tests for ingestion behavior

**Steps:**
1. Write failing tests for endpoint/script behavior where practical.
2. Implement script and endpoint using the same RAG module.
3. Verify command: `uv run python scripts/ingest_documents.py`.

## Task 6: Add synthetic sample documents and docs

**Objective:** Keep docs synchronized and document limitations honestly.

**Files:**
- Create: `data/sample-docs/*.md`
- Create: `docs/implementation_M3.md`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/threat-model.md`
- Modify: `docs/setup.md`
- Modify: `app/streamlit/main.py` and `src/closed_llm_platform/i18n.py` if citations need visible UI text.

**Verification:**
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run python scripts/ingest_documents.py`
- Optional API smoke with monkeypatched tests; Ollama end-to-end depends on local model availability.

## Commit Point

After verification, commit with:

```bash
git add .
git commit -m "feat: add M3 local RAG baseline"
```
