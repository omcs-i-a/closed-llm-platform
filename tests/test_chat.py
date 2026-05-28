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
