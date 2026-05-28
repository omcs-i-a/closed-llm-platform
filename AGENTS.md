# AGENTS.md

This repository is the implementation repository for the Closed Local LLM Platform learning project.

The workbench-side guidance lives in:

```text
../hermes-agent-workbench/projects/closed-llm-platform.md
../hermes-agent-workbench/docs/execution-steps.md
../hermes-agent-workbench/prompts/portfolio-project-readme-template.md
```

## Project Purpose

Build this repository as a hands-on learning project with Hermes Agent to understand closed/local LLM platform design.

Do not frame the work mainly as a marketing portfolio artifact. Prefer learning-first language:

- what this helps us understand
- what trade-offs the implementation exposes
- what was verified
- what is intentionally not production-ready yet

## Current Phase

Current phase: M1 implementation.

The initial documentation files are:

```text
README.md
AGENTS.md
docs/architecture.md
docs/roadmap.md
docs/threat-model.md
```

Do not write application code until the user asks to begin M1 implementation.

## M1 Scope

M1 is the first runnable milestone:

- Streamlit UI skeleton
- FastAPI API skeleton
- `GET /health`
- uv Python project with `src/closed_llm_platform`
- Docker/Compose wiring via `compose.yml`
- VS Code devcontainer support
- Ollama connection path
- basic chat request/response path
- README with Mermaid architecture

Keep M1 small. The goal is a working local path, not a complete platform.

## Expected Future Repository Shape

```text
closed-llm-platform/
  README.md
  AGENTS.md
  compose.yml
  docs/
    architecture.md
    roadmap.md
    threat-model.md
    decisions/
  app/
    api/
    streamlit/
  src/
    closed_llm_platform/
  tests/
  scripts/
  data/
  model/
  notebook/
  outputs/
```

## Working Rules for Hermes Agent

1. Read `README.md`, `docs/architecture.md`, `docs/roadmap.md`, and `docs/threat-model.md` before changing architecture or milestone scope.
2. Keep implementation tasks milestone-bound. Do not jump ahead to M2/M3/M4 unless the user explicitly asks.
3. Before M1 implementation, write or update a concrete plan with exact files, commands, and verification steps.
4. Prefer small, reviewable changes.
5. Do not commit secrets, real personal data, API keys, or private documents.
6. Do not add real enterprise/internal documents. Use synthetic sample data only.
7. Keep local/closed-network assumptions explicit.
8. Document any new runtime prerequisite in README before relying on it.
9. Verify behavior with commands before reporting completion.
10. When changing docs, keep the README, architecture, roadmap, and threat model consistent.

## Security and Privacy Rules

- Treat prompts, uploaded documents, retrieved chunks, chat responses, and audit logs as sensitive by default.
- Do not log raw secrets or unnecessary PII.
- If sample data is needed, create synthetic examples under `data/sample-docs/`.
- Keep Ollama local by default. Do not expose it publicly without an explicit user request and a documented threat-model update.
- RBAC, audit logging, PII masking, and guardrails are not optional long-term topics; they are planned milestones. However, do not overbuild them in M1.

## Documentation Style

- Use concise Japanese or English, matching the surrounding file.
- Explain why a design choice was made, not just what was changed.
- Include limitations honestly.
- Prefer Mermaid diagrams for architecture in Markdown.
- Add verification commands whenever a document describes runnable behavior.

## M1 Implementation Guardrail

When the user asks to implement M1, first ensure the M1 plan matches the repository structure: uv, src-layout Python package under `src/closed_llm_platform`, executable apps under `app/api` and `app/streamlit`, root `tests/`, root `Dockerfile`, and `compose.yml`. The plan should include:

- exact file paths
- small tasks
- commands
- verification steps
- expected output
- commit points

Do not implement M2 features during M1. In particular, do not implement full RBAC, production authentication, a full vector database, or complex guardrail policy engines in the first milestone.
