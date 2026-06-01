from closed_llm_platform.config import settings
from closed_llm_platform.rag import write_rag_index


def main() -> None:
    chunks = write_rag_index(settings.sample_docs_path, settings.rag_index_path)
    document_count = len({chunk.document_id for chunk in chunks})
    print(
        f"Ingested {document_count} document(s) into {len(chunks)} chunk(s): "
        f"{settings.rag_index_path}"
    )


if __name__ == "__main__":
    main()
