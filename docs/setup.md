# Setup

This document describes the intended local development setup for the Closed Local LLM Platform.

Current status: M3 has a verified FastAPI health/chat path, Streamlit UI, uv project setup, Dockerfile, compose.yml, prompt injection heuristic baseline, PII masking baseline, local JSONL audit logging, and a local RAG ingestion/retrieval baseline with citations. Docker/Ollama end-to-end verification requires local Docker and Ollama services to be running.

For detailed implementation maps, including file responsibilities, function/class connections, and Mermaid flow diagrams, see `docs/implementation_M1.md`, `docs/implementation_M2.md`, and `docs/implementation_M3.md`.

## Required Tools

- uv for Python dependency management
- Docker / Docker Compose
- Ollama for local LLM inference
- VS Code with Dev Containers extension, optional but supported

Verified on the current machine:

```text
uv 0.10.0
Docker 29.2.0
```

## Repository Layout

This project uses a Python src layout:

```text
src/closed_llm_platform/   reusable package code
app/api/                   FastAPI application entrypoint
app/streamlit/             Streamlit UI entrypoint
scripts/                   developer scripts and smoke checks
tests/                     pytest tests
data/                      local/sample data, not real private data
model/                     local model artifacts, generally ignored
outputs/                   generated outputs, generally ignored
notebook/                  exploratory notebooks
```

## Environment Variables

Copy the example environment file before local development:

```bash
cp .env.example .env
```

Important variables:

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
API_BASE_URL=http://localhost:8000
UI_LANGUAGE=ja
AUDIT_LOG_PATH=outputs/audit/events.jsonl
SAMPLE_DOCS_PATH=data/sample-docs
RAG_INDEX_PATH=outputs/rag/index.json
```

In Docker Compose, the API uses:

```text
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Ollama Prerequisite

M1/M2/M3 assumes Ollama runs on the host machine.

```bash
ollama serve
ollama pull qwen3:8b
curl -s http://localhost:11434/api/tags
```

## Local Python Setup

```bash
uv sync
uv run pytest -q
```

## Ingest RAG Sample Documents

```bash
uv run python scripts/ingest_documents.py
```

This creates `outputs/rag/index.json` from synthetic markdown documents in `data/sample-docs/`.

## Run API Locally

```bash
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
curl -i http://localhost:8000/health
```

## Run Streamlit Locally

```bash
uv run streamlit run app/streamlit/main.py
```

## Run with Docker Compose

```bash
docker compose -f compose.yml up --build
```

Expected local ports after M3 implementation:

- FastAPI: http://localhost:8000
- Streamlit: http://localhost:8501
- Ollama host service: http://localhost:11434

## Devcontainer

The `.devcontainer/devcontainer.json` file should open the repository in a Python-focused container with uv available. It should mount the workspace and allow running the same commands:

```bash
uv sync
uv run pytest -q
```
