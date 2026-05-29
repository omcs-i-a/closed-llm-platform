import os

import httpx
import streamlit as st

from closed_llm_platform.i18n import get_ui_text, supported_languages

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DEFAULT_UI_LANGUAGE = os.getenv("UI_LANGUAGE", "ja")

initial_text = get_ui_text(DEFAULT_UI_LANGUAGE)
st.set_page_config(page_title=initial_text.page_title, page_icon="🔒")

language_options = supported_languages()
selected_language = st.sidebar.selectbox(
    "表示言語 / Display language",
    options=list(language_options.keys()),
    format_func=language_options.__getitem__,
    index=list(language_options.keys()).index(DEFAULT_UI_LANGUAGE)
    if DEFAULT_UI_LANGUAGE in language_options
    else 0,
)
text = get_ui_text(selected_language)

st.title(text.page_title)
st.caption(text.caption)

st.info(text.info)

message = st.text_area(text.message_label, placeholder=text.message_placeholder)

if st.button(text.send_button, type="primary", disabled=not message.strip()):
    with st.spinner(text.spinner):
        try:
            response = httpx.post(
                f"{API_BASE_URL}/chat",
                json={"message": message.strip()},
                timeout=90.0,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            st.error(f"{text.request_failed_prefix}: {exc}")
        else:
            st.subheader(text.response_heading)
            st.write(body["message"])
            st.caption(
                f"{text.audit_caption_label}: "
                f"model={body['model']} | request_id={body['request_id']} | "
                f"audit_event_id={body['audit_event_id']}"
            )
            guardrail_reasons = ", ".join(body["guardrail_reasons"]) or text.no_guardrail_reasons
            st.caption(
                f"{text.guardrail_caption_label}: "
                f"guardrail={body['guardrail_status']} ({guardrail_reasons}) | "
                f"pii_masking_applied={body['pii_masking_applied']}"
            )
