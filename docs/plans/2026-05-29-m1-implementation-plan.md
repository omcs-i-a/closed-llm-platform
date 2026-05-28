# M1 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build the smallest runnable closed/local LLM path: Streamlit UI -> FastAPI gateway -> Ollama -> response back to UI, using a src-layout Python repository with uv, Docker, and VS Code devcontainer support.

**Architecture:** M1 keeps the FastAPI gateway as the control point between the UI and Ollama. The repository uses `src/closed_llm_platform/` for reusable code, `app/` for executable app entrypoints, `scripts/` for developer automation, and root-level `tests/` for pytest. Ollama runs as a host prerequisite in M1; the API container connects to host Ollama via `host.docker.internal` on macOS. Later milestones can revisit Compose-managed Ollama.

**Tech Stack:** Python src layout, uv, FastAPI, Streamlit, Ollama, Docker/Compose, VS Code devcontainer, pytest.

---

## M1 Decisions

- Repository layout: src-layout Python project, not `apps/api` / `apps/web`.
- UI: Streamlit for M1. Next.js is deferred until a later UI milestone if needed.
- Executable app entrypoints live under `app/`:
  - `app/api/main.py` for FastAPI.
  - `app/streamlit/main.py` for Streamlit.
- Reusable code lives under `src/closed_llm_platform/`:
  - settings
  - schemas
  - Ollama client
  - API service functions
- Tests live under root `tests/`.
- Dependency management: uv with `pyproject.toml` and `uv.lock`.
- Compose file name: `compose.yml`.
- Root `Dockerfile` builds the Python app image.
- `.devcontainer/devcontainer.json` supports VS Code / Dev Containers.
- Ollama mode: host service prerequisite for M1.
- Default Ollama base URL from container: `http://host.docker.internal:11434`.
- Default Ollama model: configurable via `OLLAMA_MODEL`, initially `llama3.2`.
- API routes:
  - `GET /health`
  - `POST /chat`
- M1 request IDs: include a lightweight UUID request ID in `POST /chat` responses. This prepares for audit logging without implementing M2 audit storage.

## M1 Acceptance Criteria

- `uv sync` creates the local Python environment.
- `uv run pytest -q` passes.
- `uv run uvicorn app.api.main:app --reload` starts the API locally.
- `curl -i http://localhost:8000/health` returns HTTP 200.
- `uv run streamlit run app/streamlit/main.py` starts the Streamlit UI.
- Streamlit UI can submit a chat message to the API.
- `docker compose -f compose.yml up --build` starts API and Streamlit services.
- API calls host Ollama and returns a response.
- README and `docs/setup.md` document uv, devcontainer, Docker, Streamlit, Ollama prerequisites, and commands.
- No secrets, real personal data, production auth, RBAC, RAG, audit DB, or full guardrail engine are added.

## Target Repository Shape

```text
closed-llm-platform/
  .devcontainer/
    devcontainer.json
  .github/
    ISSUE_TEMPLATE/
      bug_report.yml
      feature_request.yml
    PULL_REQUEST_TEMPLATE.md
  .streamlit/
    config.toml
  app/
    api/
      main.py
    streamlit/
      main.py
  data/
    .gitkeep
  docs/
    architecture.md
    roadmap.md
    setup.md
    threat-model.md
    plans/
      2026-05-29-m1-implementation-plan.md
  model/
    .gitkeep
  notebook/
    .gitkeep
  outputs/
    .gitkeep
  scripts/
    smoke_api.py
  src/
    closed_llm_platform/
      __init__.py
      config.py
      schemas.py
      ollama_client.py
      chat_service.py
  tests/
    test_health.py
    test_chat.py
    test_ollama_client.py
  .env.example
  .gitignore
  AGENTS.md
  Dockerfile
  LICENSE
  README.md
  compose.yml
  pyproject.toml
  uv.lock
```

---

## Task 1: Create repository foundation files

**Objective:** Add the non-application foundation matching the requested project layout.

**Files:**
- Create: `.devcontainer/devcontainer.json`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.streamlit/config.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `docs/setup.md`
- Create `.gitkeep` files under generated-data directories

**Verification:**

```bash
find . -maxdepth 3 -type f | sort
```

Expected: foundation files are present. No app behavior yet.

---

## Task 2: Create uv Python project metadata

**Objective:** Define Python dependencies and src-layout packaging.

**Files:**
- Create: `pyproject.toml`
- Create: `src/closed_llm_platform/__init__.py`

**Dependencies:**

- fastapi
- uvicorn[standard]
- httpx
- pydantic-settings
- streamlit
- pytest
- pytest-asyncio
- ruff

**Verification:**

```bash
uv sync
uv run python -c "import closed_llm_platform; print(closed_llm_platform.__version__)"
uv run pytest -q
```

Expected initially: import works; pytest may report no tests until Task 3.

---

## Task 3: RED test for `GET /health`

**Objective:** Define expected health endpoint behavior before implementation.

**Files:**
- Create: `tests/test_health.py`

**Test:**

```python
from fastapi.testclient import TestClient

from app.api.main import app


def test_health_returns_ok_status():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Run RED:**

```bash
uv run pytest tests/test_health.py::test_health_returns_ok_status -v
```

Expected: FAIL because `app.api.main` does not exist yet.

---

## Task 4: GREEN implementation for `GET /health`

**Objective:** Implement the minimal FastAPI app and health route.

**Files:**
- Create: `app/api/main.py`
- Create: `app/api/__init__.py`
- Create: `app/__init__.py`

**Implementation:**

```python
from fastapi import FastAPI

app = FastAPI(title="Closed Local LLM Platform API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

**Verify GREEN:**

```bash
uv run pytest tests/test_health.py::test_health_returns_ok_status -v
uv run pytest -q
```

Expected: PASS.

---

## Task 5: RED tests for chat request/response contract

**Objective:** Define the minimal `POST /chat` API contract before implementation.

**Files:**
- Create: `tests/test_chat.py`

**Test:**

```python
from fastapi.testclient import TestClient

from app.api.main import app


def test_chat_requires_non_empty_message():
    client = TestClient(app)

    response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_returns_model_response(monkeypatch):
    async def fake_generate(message: str) -> str:
        assert message == "Hello local model"
        return "Hello from Ollama"

    monkeypatch.setattr("app.api.main.generate_ollama_response", fake_generate)
    client = TestClient(app)

    response = client.post("/chat", json={"message": "Hello local model"})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Hello from Ollama"
    assert body["model"]
    assert body["request_id"]
```

**Run RED:**

```bash
uv run pytest tests/test_chat.py -v
```

Expected: FAIL because `/chat` does not exist yet.

---

## Task 6: GREEN schemas, config, and chat endpoint

**Objective:** Add minimal request/response schemas, settings, and chat route using src-layout reusable modules.

**Files:**
- Create: `src/closed_llm_platform/schemas.py`
- Create: `src/closed_llm_platform/config.py`
- Modify: `app/api/main.py`

**Schemas:**

```python
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


class ChatResponse(BaseModel):
    message: str
    model: str
    request_id: str
```

**Config:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.2"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

**Main app update:** import reusable schema/config from `closed_llm_platform` and add `POST /chat`.

**Verify:**

```bash
uv run pytest tests/test_chat.py -v
uv run pytest -q
```

Expected: tests still fail until `generate_ollama_response` exists. That failure becomes the RED state for Task 7.

---

## Task 7: RED/GREEN Ollama client behavior

**Objective:** Implement a minimal Ollama client with a testable boundary.

**Files:**
- Create: `src/closed_llm_platform/ollama_client.py`
- Create: `tests/test_ollama_client.py`

**Test:**

```python
import pytest

from closed_llm_platform.ollama_client import extract_ollama_message


def test_extract_ollama_message_from_generate_response():
    payload = {"response": "Local answer"}

    result = extract_ollama_message(payload)

    assert result == "Local answer"


def test_extract_ollama_message_rejects_missing_response():
    with pytest.raises(ValueError, match="response"):
        extract_ollama_message({})
```

**Implementation:**

```python
import httpx

from closed_llm_platform.config import settings


def extract_ollama_message(payload: dict) -> str:
    response = payload.get("response")
    if not isinstance(response, str):
        raise ValueError("Ollama response payload missing string 'response'")
    return response


async def generate_ollama_response(message: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": settings.ollama_model, "prompt": message, "stream": False},
        )
        response.raise_for_status()
        return extract_ollama_message(response.json())
```

**Verify:**

```bash
uv run pytest tests/test_ollama_client.py -v
uv run pytest -q
```

Expected: PASS.

---

## Task 8: Create Streamlit UI

**Objective:** Add a minimal Streamlit chat interface that calls the FastAPI gateway.

**Files:**
- Create: `app/streamlit/__init__.py`
- Create: `app/streamlit/main.py`

**Behavior:**

- Render project title and M1 limitation note.
- Provide text area for a message.
- POST to `${API_BASE_URL:-http://localhost:8000}/chat`.
- Display `message`, `model`, and `request_id`.
- Show API errors clearly.

**Verify:**

```bash
uv run streamlit run app/streamlit/main.py
```

Expected: Streamlit starts locally.

---

## Task 9: Add Dockerfile and compose.yml

**Objective:** Run API and Streamlit via Docker Compose.

**Files:**
- Create: `Dockerfile`
- Create: `compose.yml`

**Dockerfile requirements:**

- Use Python slim base image.
- Install uv.
- Copy `pyproject.toml` and `uv.lock`.
- Run `uv sync --frozen` if lock exists.
- Copy `app/` and `src/`.
- Default command can be overridden by Compose.

**Compose services:**

- `api`: runs `uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000`.
- `streamlit`: runs `uv run streamlit run app/streamlit/main.py --server.address 0.0.0.0 --server.port 8501`.
- Environment:
  - `OLLAMA_BASE_URL=http://host.docker.internal:11434`
  - `OLLAMA_MODEL=llama3.2`
  - `API_BASE_URL=http://api:8000` for Streamlit container
- Ports:
  - API: `8000:8000`
  - Streamlit: `8501:8501`

**Verify:**

```bash
docker compose -f compose.yml up --build
curl -i http://localhost:8000/health
```

Expected: services start and health check returns 200.

---

## Task 10: Add smoke script

**Objective:** Provide a simple developer verification script that calls health and chat.

**Files:**
- Create: `scripts/smoke_api.py`

**Behavior:**

- GET `/health`.
- POST `/chat` with a short prompt.
- Print response JSON.
- Exit non-zero on failure.

**Verify:**

```bash
uv run python scripts/smoke_api.py
```

Expected: health and chat calls succeed when API and Ollama are running.

---

## Task 11: Update README and docs for implemented M1

**Objective:** Align documentation with the actual uv/src-layout/Streamlit implementation.

**Files:**
- Modify: `README.md`
- Modify: `docs/setup.md`
- Modify if needed: `docs/architecture.md`
- Modify if needed: `docs/roadmap.md`
- Modify if needed: `docs/threat-model.md`
- Modify if needed: `AGENTS.md`

**README updates:**

- uv setup
- devcontainer option
- Ollama prerequisite
- `ollama pull llama3.2`
- `uv sync`
- API run command
- Streamlit run command
- Compose run command
- health curl
- chat curl
- current M1 limitations

---

## Final M1 Verification

```bash
uv sync
uv run pytest -q
uv run ruff check .
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000
curl -i http://localhost:8000/health
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Say hello in one short sentence."}'
uv run streamlit run app/streamlit/main.py
docker compose -f compose.yml up --build
```

M1 is done when:

- all acceptance criteria pass
- README quick start matches reality
- architecture docs match the implementation
- threat model limitations are updated
- `git status --short` is clean or only contains intentional uncommitted changes
