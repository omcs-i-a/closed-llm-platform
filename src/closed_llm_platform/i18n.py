from dataclasses import dataclass


@dataclass(frozen=True)
class UIText:
    language_name: str
    page_title: str
    caption: str
    info: str
    message_label: str
    message_placeholder: str
    send_button: str
    spinner: str
    request_failed_prefix: str
    response_heading: str
    audit_caption_label: str
    guardrail_caption_label: str
    no_guardrail_reasons: str
    use_rag_label: str
    citations_heading: str
    no_citations: str


_UI_TEXTS: dict[str, UIText] = {
    "ja": UIText(
        language_name="日本語",
        page_title="Closed Local LLM Platform",
        caption=(
            "M3: 日本語対応 UI -> FastAPI gateway -> "
            "guardrails/PII/audit -> local RAG -> local Ollama runtime"
        ),
        info=(
            "M3 では prompt injection の簡易検出、監査メタデータ用の PII masking、"
            "local JSONL audit event に加えて、synthetic documents を使った local RAG、"
            "citations、retrieved context の indirect prompt injection metadata を追加しています。"
            "RBAC は後続 milestone です。"
        ),
        message_label="メッセージ",
        message_placeholder="ローカルモデルに短い質問を入力してください...",
        send_button="送信",
        spinner="FastAPI gateway を呼び出しています...",
        request_failed_prefix="API リクエストに失敗しました",
        response_heading="応答",
        audit_caption_label="モデル / リクエストID / 監査イベントID",
        guardrail_caption_label="ガードレール / PII masking",
        no_guardrail_reasons="理由なし",
        use_rag_label="RAG を使用する",
        citations_heading="引用 / Retrieved context",
        no_citations="引用はありません",
    ),
    "en": UIText(
        language_name="English",
        page_title="Closed Local LLM Platform",
        caption=(
            "M3: Streamlit UI -> FastAPI gateway -> "
            "guardrails/PII/audit -> local RAG -> local Ollama runtime"
        ),
        info=(
            "M3 adds visible prompt-injection heuristics, basic PII masking for audit metadata, "
            "local JSONL audit events, local RAG over synthetic documents, citations, "
            "and indirect prompt-injection metadata for retrieved context. "
            "RBAC is still planned later."
        ),
        message_label="Message",
        message_placeholder="Ask the local model a short question...",
        send_button="Send",
        spinner="Calling FastAPI gateway...",
        request_failed_prefix="API request failed",
        response_heading="Response",
        audit_caption_label="model / request ID / audit event ID",
        guardrail_caption_label="guardrail / PII masking",
        no_guardrail_reasons="no reasons",
        use_rag_label="Use RAG",
        citations_heading="Citations",
        no_citations="No citations",
    ),
}


def supported_languages() -> dict[str, str]:
    return {code: text.language_name for code, text in _UI_TEXTS.items()}


def get_ui_text(language: str = "ja") -> UIText:
    return _UI_TEXTS.get(language, _UI_TEXTS["ja"])
