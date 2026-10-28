import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.rag import RAGService
from app.services.vector_store import SearchResult

@pytest.fixture
def mock_embedding_service():
    mock = MagicMock()
    mock.embed.return_value = [0.1] * 384  # Mock dimension
    return mock

@pytest.fixture
def mock_vector_store():
    mock = MagicMock()
    mock.query.return_value = [
        SearchResult(doc_id="1", text="The capital of France is Paris.", score=0.9),
        SearchResult(doc_id="2", text="Paris is known for the Eiffel Tower.", score=0.8),
    ]
    return mock

@pytest.fixture
def mock_llm_client():
    mock = AsyncMock()
    mock.generate.return_value = "The capital of France is Paris."
    return mock

@pytest.mark.asyncio
async def test_rag_query_success(mock_embedding_service, mock_vector_store, mock_llm_client):
    # Arrange
    service = RAGService(mock_embedding_service, mock_vector_store, mock_llm_client)
    prompt = "What is the capital of France?"
    session_id = "test_session_123"

    # Act
    result = await service.query(prompt, session_id)

    # Assert
    assert result == "The capital of France is Paris."
    mock_embedding_service.embed.assert_called_once_with(prompt)
    mock_vector_store.query.assert_called_once()
    mock_llm_client.generate.assert_called_once()

    # Verify prompt construction
    called_prompt = mock_llm_client.generate.call_args[0][0]
    assert "The capital of France is Paris." in called_prompt
    assert "Paris is known for the Eiffel Tower." in called_prompt
    assert "What is the capital of France?" in called_prompt

@pytest.mark.asyncio
async def test_rag_query_empty_results(mock_embedding_service, mock_vector_store, mock_llm_client):
    # Arrange
    mock_vector_store.query.return_value = []
    service = RAGService(mock_embedding_service, mock_vector_store, mock_llm_client)
    prompt = "What is the capital of Mars?"
    session_id = "test_session_456"

    # Act
    result = await service.query(prompt, session_id)

    # Assert
    assert result is not None
    mock_llm_client.generate.assert_called_once()
    called_prompt = mock_llm_client.generate.call_args[0][0]
    assert "Context:\n\n" in called_prompt # Empty context

@pytest.mark.asyncio
async def test_rag_query_failure(mock_embedding_service, mock_vector_store, mock_llm_client):
    # Arrange
    mock_llm_client.generate.side_effect = Exception("LLM failed")
    service = RAGService(mock_embedding_service, mock_vector_store, mock_llm_client)
    prompt = "Hello"
    session_id = "test_session_789"

    # Act
    with pytest.raises(RuntimeError) as excinfo:
        await service.query(prompt, session_id)

    # Assert
    assert "RAG pipeline failed: LLM failed" in str(excinfo.value)
