from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        model: SentenceTransformer | None = None,
    ) -> None:
        self.model_name = model_name
        self._model = model

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def dimension(self) -> int:
        dimension = self.model.get_sentence_embedding_dimension()
        if dimension is None:
            raise RuntimeError(
                f"Embedding model {self.model_name!r} did not report its dimension"
            )
        return dimension

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        vectors = self.model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [[float(value) for value in vector] for vector in vectors]
