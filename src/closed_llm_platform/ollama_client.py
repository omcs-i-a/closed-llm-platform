import httpx

from closed_llm_platform.config import settings


def extract_ollama_message(payload: dict) -> str:
    response = payload.get("response")
    if not isinstance(response, str):
        raise ValueError("Ollama response payload missing string 'response'")
    return response


async def generate_ollama_response(message: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": message,
                "stream": False,
            },
        )
        response.raise_for_status()
        return extract_ollama_message(response.json())
