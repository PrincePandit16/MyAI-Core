from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping, Sequence

from app.core.config import settings

if TYPE_CHECKING:
    from pymilvus import MilvusClient


@dataclass(frozen=True)
class SearchResult:
    doc_id: str
    text: str
    score: float


class VectorStore:
    def __init__(
        self,
        uri: str = settings.milvus_uri,
        collection_name: str = settings.milvus_collection_name,
        token: str = settings.milvus_token,
        client: MilvusClient | None = None,
    ) -> None:
        if client is None:
            from pymilvus import MilvusClient

            client = MilvusClient(uri=uri, token=token or None)

        self.client = client
        self.collection_name = collection_name
        self._dimension: int | None = None

    def create_collection(self, dimension: int) -> None:
        if dimension <= 0:
            raise ValueError("Embedding dimension must be positive")

        if not self.client.has_collection(collection_name=self.collection_name):
            from pymilvus import DataType

            schema = self.client.create_schema(
                auto_id=False,
                enable_dynamic_field=False,
            )
            schema.add_field(
                field_name="doc_id",
                datatype=DataType.VARCHAR,
                is_primary=True,
                max_length=512,
            )
            schema.add_field(
                field_name="text",
                datatype=DataType.VARCHAR,
                max_length=65535,
            )
            schema.add_field(
                field_name="embedding",
                datatype=DataType.FLOAT_VECTOR,
                dim=dimension,
            )

            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="embedding",
                index_type="AUTOINDEX",
                metric_type="COSINE",
            )
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                index_params=index_params,
            )

        self.client.load_collection(collection_name=self.collection_name)
        self._dimension = dimension

    def upsert(
        self,
        documents: Sequence[Mapping[str, str]],
        embeddings: Sequence[Sequence[float]],
    ) -> None:
        if len(documents) != len(embeddings):
            raise ValueError("Each document must have exactly one embedding")
        if not documents:
            return

        data: list[dict[str, object]] = []
        for document, embedding in zip(documents, embeddings):
            doc_id = document["doc_id"]
            text = document["text"]
            if not doc_id:
                raise ValueError("Document IDs must not be empty")
            if len(doc_id.encode("utf-8")) > 512:
                raise ValueError("Document IDs must not exceed 512 UTF-8 bytes")
            if len(text.encode("utf-8")) > 65535:
                raise ValueError("Document text must not exceed 65535 UTF-8 bytes")
            if self._dimension is not None and len(embedding) != self._dimension:
                raise ValueError(
                    f"Expected {self._dimension}-dimensional embeddings, "
                    f"received {len(embedding)} dimensions"
                )

            data.append(
                {
                    "doc_id": doc_id,
                    "text": text,
                    "embedding": [float(value) for value in embedding],
                }
            )

        self.client.upsert(collection_name=self.collection_name, data=data)

    def query(
        self,
        embedding: Sequence[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if self._dimension is not None and len(embedding) != self._dimension:
            raise ValueError(
                f"Expected a {self._dimension}-dimensional query embedding, "
                f"received {len(embedding)} dimensions"
            )

        results = self.client.search(
            collection_name=self.collection_name,
            data=[[float(value) for value in embedding]],
            anns_field="embedding",
            limit=top_k,
            search_params={"metric_type": "COSINE", "params": {}},
            output_fields=["doc_id", "text"],
        )
        return [
            SearchResult(
                doc_id=hit["entity"]["doc_id"],
                text=hit["entity"]["text"],
                score=float(hit["distance"]),
            )
            for hit in results[0]
        ]
