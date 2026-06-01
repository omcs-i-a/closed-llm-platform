from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen3:8b"
    audit_log_path: str = "outputs/audit/events.jsonl"
    sample_docs_path: str = "data/sample-docs"
    rag_index_path: str = "outputs/rag/index.json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
