import json

from closed_llm_platform.audit import AuditEvent, create_chat_audit_event, write_audit_event_jsonl
from closed_llm_platform.guardrails import GuardrailDecision
from closed_llm_platform.privacy import MaskingResult


def test_create_chat_audit_event_uses_hashes_and_redacted_summaries():
    event = create_chat_audit_event(
        request_id="req-123",
        model="qwen3:8b",
        prompt="email alice@example.com",
        response="call +1-415-555-1212",
        redacted_prompt=MaskingResult(text="email [REDACTED_EMAIL]", pii_types=["email"]),
        redacted_response=MaskingResult(text="call [REDACTED_PHONE]", pii_types=["phone"]),
        guardrail=GuardrailDecision(status="allowed", reasons=[], matched_patterns=[]),
        latency_ms=42,
        outcome="success",
    )

    assert isinstance(event, AuditEvent)
    assert event.request_id == "req-123"
    assert event.action == "chat"
    assert event.route == "/chat"
    assert event.prompt_hash
    assert event.response_hash
    assert event.redacted_prompt_summary == "email [REDACTED_EMAIL]"
    assert event.redacted_response_summary == "call [REDACTED_PHONE]"
    assert event.pii_masking_applied is True
    assert event.pii_types == ["email", "phone"]
    assert event.guardrail_decision == "allowed"
    assert event.outcome == "success"

    dumped = event.model_dump(mode="json")
    assert "alice@example.com" not in json.dumps(dumped)
    assert "+1-415-555-1212" not in json.dumps(dumped)


def test_write_audit_event_jsonl_appends_one_json_line(tmp_path):
    event = create_chat_audit_event(
        request_id="req-123",
        model="qwen3:8b",
        prompt="hello",
        response="world",
        redacted_prompt=MaskingResult(text="hello", pii_types=[]),
        redacted_response=MaskingResult(text="world", pii_types=[]),
        guardrail=GuardrailDecision(status="allowed", reasons=[], matched_patterns=[]),
        latency_ms=7,
        outcome="success",
    )
    path = tmp_path / "audit.jsonl"

    write_audit_event_jsonl(event, path)

    lines = path.read_text().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["request_id"] == "req-123"
    assert payload["redacted_prompt_summary"] == "hello"
