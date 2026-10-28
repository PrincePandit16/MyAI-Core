from unittest.mock import MagicMock

import pytest
from app.services.embedding import EmbeddingService


def test_embedding_service_initialization():
    service = EmbeddingService(model_name="test-model")
    assert service.model_name == "test-model"
    assert service._model is None


def test_embedding_service_embed_empty():
    service = EmbeddingService()
    # Mock the model to avoid downloading real weights
    service._model = MagicMock()
    service.model.encode.return_value = []

    assert service.embed_many([]) == []


def test_embedding_service_embed_single():
    service = EmbeddingService()
    mock_model = MagicMock()
    mock_model.get_sentence_embedding_dimension.return_value = 384
    mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
    service._model = mock_model

    assert service.dimension == 384
    assert service.embed("hello") == [0.1, 0.2, 0.3]


def test_embedding_service_embed_many():
    service = EmbeddingService()
    mock_model = MagicMock()
    mock_model.encode.return_value = [[0.1], [0.2]]
    service._model = mock_model

    assert service.embed_many(["a", "b"]) == [[0.1], [0.2]]
