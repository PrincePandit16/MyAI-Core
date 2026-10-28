import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Sequence

import pytest

from app.services.embedding import EmbeddingService
from app.services.vector_store import SearchResult, VectorStore
from scripts.index_docs import index_directory, load_markdown_documents


class FakeEmbeddingModel:
    def __init__(self) -> None:
        self.encoded_texts: list[str] = []

    def get_sentence_embedding_dimension(self) -> int:
        return 2

    def encode(
        self,
        texts: list[str],
        *,
        convert_to_numpy: bool,
        normalize_embeddings: bool,
        show_progress_bar: bool,
    ) -> list[list[float]]:
        assert convert_to_numpy
        assert normalize_embeddings
        assert not show_progress_bar
        self.encoded_texts.extend(texts)
        return [[0.6, 0.8] for _ in texts]


class FakeSchema:
    def __init__(self) -> None:
        self.fields: list[dict[str, object]] = []

    def add_field(self, **field: object) -> None:
        self.fields.append(field)


class FakeIndexParams:
    def __init__(self) -> None:
        self.indexes: list[dict[str, object]] = []

    def add_index(self, **index: object) -> None:
        self.indexes.append(index)


class FakeMilvusClient:
    def __init__(self) -> None:
        self.schema = FakeSchema()
        self.index_params = FakeIndexParams()
        self.created_collection: str | None = None
        self.loaded_collection: str | None = None
        self.upserted: list[dict[str, object]] = []
        self.search_arguments: dict[str, object] | None = None

    def has_collection(self, *, collection_name: str) -> bool:
        return False

    def create_schema(self, **_: object) -> FakeSchema:
        return self.schema

    def prepare_index_params(self) -> FakeIndexParams:
        return self.index_params

    def create_collection(
        self,
        *,
        collection_name: str,
        schema: FakeSchema,
        index_params: FakeIndexParams,
    ) -> None:
        self.created_collection = collection_name

    def load_collection(self, *, collection_name: str) -> None:
        self.loaded_collection = collection_name

    def upsert(
        self,
        *,
        collection_name: str,
        data: list[dict[str, object]],
    ) -> None:
        self.upserted = data

    def search(self, **arguments: object) -> list[list[dict[str, object]]]:
        self.search_arguments = arguments
        return [
            [
                {
                    "distance": 0.93,
                    "entity": {
                        "doc_id": "guide.md",
                        "text": "Relevant guidance",
                    },
                }
            ]
        ]


def test_embedding_service_returns_normalized_vectors() -> None:
    model = FakeEmbeddingModel()
    service = EmbeddingService(model=model)  # type: ignore[arg-type]

    assert service.dimension == 2
    assert service.embed("query") == [0.6, 0.8]
    assert service.embed_many(["first", "second"]) == [[0.6, 0.8], [0.6, 0.8]]
    assert model.encoded_texts == ["query", "first", "second"]


def test_vector_store_creates_collection_upserts_and_queries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pymilvus = ModuleType("pymilvus")
    setattr(
        pymilvus,
        "DataType",
        SimpleNamespace(VARCHAR="VARCHAR", FLOAT_VECTOR="FLOAT_VECTOR"),
    )
    monkeypatch.setitem(sys.modules, "pymilvus", pymilvus)
    client = FakeMilvusClient()
    store = VectorStore(collection_name="knowledge", client=client)  # type: ignore[arg-type]

    store.create_collection(dimension=2)
    store.upsert(
        [{"doc_id": "guide.md", "text": "Relevant guidance"}],
        [[0.6, 0.8]],
    )
    results = store.query([0.6, 0.8], top_k=3)

    assert client.created_collection == "knowledge"
    assert client.loaded_collection == "knowledge"
    assert [field["field_name"] for field in client.schema.fields] == [
        "doc_id",
        "text",
        "embedding",
    ]
    assert client.upserted == [
        {
            "doc_id": "guide.md",
            "text": "Relevant guidance",
            "embedding": [0.6, 0.8],
        }
    ]
    assert results == [SearchResult("guide.md", "Relevant guidance", 0.93)]
    assert client.search_arguments is not None
    assert client.search_arguments["limit"] == 3
    assert client.search_arguments["output_fields"] == ["doc_id", "text"]


def test_vector_store_rejects_mismatched_embeddings() -> None:
    store = VectorStore(client=FakeMilvusClient())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="exactly one embedding"):
        store.upsert([{"doc_id": "guide.md", "text": "Text"}], [])


def test_index_directory_loads_and_chunks_markdown(tmp_path: Path) -> None:
    source = tmp_path / "docs"
    source.mkdir()
    (source / "short.md").write_text("# Short\nContent", encoding="utf-8")
    nested = source / "nested"
    nested.mkdir()
    (nested / "long.md").write_text("x" * 1300, encoding="utf-8")

    documents = load_markdown_documents(source)

    assert documents[0] == {"doc_id": "nested/long.md#chunk-0001", "text": "x" * 1200}
    assert documents[1] == {"doc_id": "nested/long.md#chunk-0002", "text": "x" * 100}
    assert documents[2] == {"doc_id": "short.md", "text": "# Short\nContent"}

    class FakeEmbeddingService:
        dimension = 2

        def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
            return [[0.6, 0.8] for _ in texts]

    class FakeVectorStore:
        def __init__(self) -> None:
            self.created_dimension: int | None = None
            self.documents: Sequence[dict[str, str]] = []

        def create_collection(self, dimension: int) -> None:
            self.created_dimension = dimension

        def upsert(
            self,
            indexed_documents: Sequence[dict[str, str]],
            embeddings: Sequence[Sequence[float]],
        ) -> None:
            self.documents = indexed_documents
            assert len(indexed_documents) == len(embeddings)

    store = FakeVectorStore()
    count = index_directory(
        source,
        FakeEmbeddingService(),  # type: ignore[arg-type]
        store,  # type: ignore[arg-type]
    )

    assert count == 3
    assert store.created_dimension == 2
    assert len(store.documents) == 3
