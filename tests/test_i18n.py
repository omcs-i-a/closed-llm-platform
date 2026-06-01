from closed_llm_platform.i18n import get_ui_text, supported_languages


def test_japanese_ui_text_is_available_by_default():
    text = get_ui_text()

    assert text.language_name == "日本語"
    assert text.page_title == "Closed Local LLM Platform"
    assert text.send_button == "送信"
    assert "日本語" in text.caption
    assert "監査イベントID" in text.audit_caption_label
    assert text.use_rag_label == "RAG を使用する"
    assert "引用" in text.citations_heading


def test_supported_languages_include_japanese_and_english():
    assert supported_languages() == {"ja": "日本語", "en": "English"}


def test_unknown_language_falls_back_to_japanese():
    assert get_ui_text("unknown").send_button == "送信"


def test_english_ui_text_remains_available():
    text = get_ui_text("en")

    assert text.language_name == "English"
    assert text.send_button == "Send"
    assert "audit event ID" in text.audit_caption_label
    assert text.use_rag_label == "Use RAG"
    assert text.citations_heading == "Citations"
