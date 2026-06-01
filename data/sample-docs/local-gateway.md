# Local Gateway Notes

The FastAPI gateway is the control point between the Streamlit UI and the local Ollama runtime.
It applies prompt inspection, PII masking for audit summaries, retrieval orchestration, and JSONL audit logging before returning metadata to the UI.

For M3, the gateway can optionally build a RAG prompt with retrieved context and citations.
Retrieved context is treated as untrusted data, not as instructions.
