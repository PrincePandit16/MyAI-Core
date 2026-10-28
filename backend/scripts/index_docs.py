import argparse
import sys
from pathlib import Path
from typing import Sequence

backend_path = str(Path(__file__).resolve().parents[1])
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.config import Settings
from app.services.embedding import EmbeddingService
from app.services.vector_store import VectorStore

CHUNK_SIZE = 1200


def _split_text(text: str) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        while len(paragraph) > CHUNK_SIZE:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(paragraph[:CHUNK_SIZE])
            paragraph = paragraph[CHUNK_SIZE:]

        candidate = f"{current}\n{paragraph}" if current else paragraph
        if len(candidate) > CHUNK_SIZE:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate

    if current:
        chunks.append(current)
    return chunks


def load_markdown_documents(directory: Path) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for path in sorted(directory.rglob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        relative_path = path.relative_to(directory).as_posix()
        chunks = _split_text(text)
        for index, chunk in enumerate(chunks, start=1):
            doc_id = (
                relative_path
                if len(chunks) == 1
                else f"{relative_path}#chunk-{index:04d}"
            )
            documents.append({"doc_id": doc_id, "text": chunk})
    return documents


def index_directory(
    directory: Path,
    embedding_service: EmbeddingService,
    vector_store: VectorStore,
) -> int:
    if not directory.is_dir():
        raise NotADirectoryError(f"Markdown directory does not exist: {directory}")

    documents = load_markdown_documents(directory)
    if not documents:
        raise ValueError(f"No non-empty Markdown files found in {directory}")

    embeddings = embedding_service.embed_many(
        [document["text"] for document in documents]
    )
    vector_store.create_collection(embedding_service.dimension)
    vector_store.upsert(documents, embeddings)
    return len(documents)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Embed Markdown files and upsert them into Milvus."
    )
    parser.add_argument("directory", type=Path, help="Directory to scan recursively")
    args = parser.parse_args(argv)

    settings = Settings(_env_file=Path(__file__).resolve().parents[1] / ".env")
    embedding_service = EmbeddingService(settings.embedding_model_name)
    vector_store = VectorStore(
        uri=settings.milvus_uri,
        collection_name=settings.milvus_collection_name,
        token=settings.milvus_token,
    )
    count = index_directory(args.directory, embedding_service, vector_store)
    print(f"Indexed {count} Markdown document chunk(s) into {settings.milvus_collection_name!r}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
