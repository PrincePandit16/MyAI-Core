from unittest.mock import MagicMock

import pytest
from app.services.vector_store import SearchResult, VectorStore


def test_vector_store_initialization():
    mock_client = MagicMock()
    store = VectorStore(client=mock_client)
    assert store.client == mock_client


def test_vector_store_create_collection_invalid_dim():
    mock_client = MagicMock()
    store = VectorStore(client=mock_client)
    with pytest.raises(ValueError, match="Embedding dimension must be positive"):
        store.create_collection(dimension=0)


def test_vector_store_upsert_mismatch():
    mock_client = MagicMock()
    store = VectorStore(client=mock_client)
    with pytest.raises(
        ValueError, match="Each document must have exactly one embedding"
    ):
        store.upsert(documents=[{"doc_id": "1", "text": "t1"}], embeddings=[])


def test_vector_store_upsert_empty_id():
    mock_client = MagicMock()
    store = VectorStore(client=mock_client)
    with pytest.raises(ValueError, match="Document IDs must not be empty"):
        store.upsert(documents=[{"doc_id": "", "text": "t1"}], embeddings=[[0.1]])


def test_vector_store_query_invalid_top_k():
    mock_client = MagicMock()
    store = VectorStore(client=mock_client)
    with pytest.raises(ValueError, match="top_k must be positive"):
        store.query(embedding=[0.1], top_k=0)
