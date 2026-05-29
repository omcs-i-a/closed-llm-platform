from closed_llm_platform.privacy import mask_pii


def test_mask_pii_redacts_email_phone_api_key_and_credit_card():
    text = (
        "Contact alice@example.com or +1-415-555-1212. "
        "Use sk-test_1234567890abcdef and card 4242 4242 4242 4242."
    )

    result = mask_pii(text)

    assert "alice@example.com" not in result.text
    assert "+1-415-555-1212" not in result.text
    assert "sk-test_1234567890abcdef" not in result.text
    assert "4242 4242 4242 4242" not in result.text
    assert result.text.count("[REDACTED_EMAIL]") == 1
    assert "email" in result.pii_types
    assert "phone" in result.pii_types
    assert "api_key" in result.pii_types
    assert "credit_card" in result.pii_types
    assert result.applied is True


def test_mask_pii_reports_no_change_for_plain_text():
    result = mask_pii("Hello local model")

    assert result.text == "Hello local model"
    assert result.pii_types == []
    assert result.applied is False
