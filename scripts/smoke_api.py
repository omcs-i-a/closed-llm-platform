import os

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def main() -> int:
    with httpx.Client(timeout=90.0) as client:
        health = client.get(f"{API_BASE_URL}/health")
        health.raise_for_status()
        print("health:", health.json())

        chat = client.post(
            f"{API_BASE_URL}/chat",
            json={"message": "Say hello in one short sentence."},
        )
        chat.raise_for_status()
        print("chat:", chat.json())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
