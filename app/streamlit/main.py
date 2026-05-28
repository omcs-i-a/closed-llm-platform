import os

import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Closed Local LLM Platform", page_icon="🔒")
st.title("Closed Local LLM Platform")
st.caption("M1: Streamlit UI -> FastAPI gateway -> local Ollama runtime")

st.info(
    "M1 intentionally implements only the basic chat path. "
    "Guardrails, PII masking, RAG, audit logging, and RBAC are planned later milestones."
)

message = st.text_area("Message", placeholder="Ask the local model a short question...")

if st.button("Send", type="primary", disabled=not message.strip()):
    with st.spinner("Calling FastAPI gateway..."):
        try:
            response = httpx.post(
                f"{API_BASE_URL}/chat",
                json={"message": message.strip()},
                timeout=90.0,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            st.error(f"API request failed: {exc}")
        else:
            st.subheader("Response")
            st.write(body["message"])
            st.caption(f"model: {body['model']} | request_id: {body['request_id']}")
