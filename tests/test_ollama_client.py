import pytest

from closed_llm_platform.ollama_client import extract_ollama_message


def test_extract_ollama_message_from_generate_response():
    payload = {"response": "Local answer"}

    result = extract_ollama_message(payload)

    assert result == "Local answer"


def test_extract_ollama_message_rejects_missing_response():
    with pytest.raises(ValueError, match="response"):
        extract_ollama_message({})
