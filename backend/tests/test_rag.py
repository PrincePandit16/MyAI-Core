from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.rag import RAGService


@pytest.mark.asyncio
async def test_rag_service_query_success():
    mock_embedding = MagicMock()
    mock_embedding.embed.return_value = [0.1, 0.2]

    mock_vector_store = MagicMock()
    mock_vector_store.query.return_value = [
        MagicMock(text="Relevant doc 1"),
        MagicMock(text="Relevant doc 2"),
    ]

    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "The answer is 42"

    rag = RAGService(mock_embedding, mock_vector_store, mock_llm)

    result = await rag.query("What is the answer?", "session_123")

    assert result == "The answer is 42"
    mock_embedding.embed.assert_called_once_with("What is the answer?")
    mock_vector_store.query.assert_called_once()
    mock_llm.generate.assert_called_once()


@pytest.mark.asyncio
async def test_rag_service_query_failure():
    mock_embedding = MagicMock()
    mock_embedding.embed.side_effect = Exception("Embedding failed")

    mock_vector_store = MagicMock()
    mock_llm = AsyncMock()

    rag = RAGService(mock_embedding, mock_vector_store, mock_llm)

    with pytest.raises(RuntimeError, match="RAG pipeline failed: Embedding failed"):
        await rag.query("Query", "session_123")
