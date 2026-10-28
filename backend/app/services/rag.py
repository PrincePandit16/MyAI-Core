from __future__ import annotations

import logging
from typing import Sequence

from app.services.embedding import EmbeddingService
from app.services.llm_client import LLMClient, llm_client
from app.services.vector_store import VectorStore, SearchResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        llm_client: LLMClient,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_client = llm_client

    async def query(
        self,
        prompt: str,
        session_id: str,
        top_k: int = 5
    ) -> str:
        """
        Performs a RAG query:
        1. Embeds the prompt.
        2. Retrieves relevant documents from the vector store.
        3. Constructs a prompt with context and query.
        4. Generates a response using the LLM.
        """
        logger.info("Processing RAG query for session %s", session_id)

        try:
            # 1. Retrieve relevant contexts
            query_embedding = self.embedding_service.embed(prompt)
            search_results: list[SearchResult] = self.vector_store.query(
                embedding=query_embedding,
                top_k=top_k
            )

            # 2. Build composed prompt
            context_text = "\n\n".join([res.text for res in search_results])

            composed_prompt = (
                "You are a helpful AI assistant. Use the following pieces of retrieved context "
                "to answer the user's question. If you don't know the answer based on the context, "
                "just say that you don't know, don't try to make up an answer. Keep the answer concise.\n\n"
                f"Context:\n{context_text}\n\n"
                f"User Question: {prompt}\n\n"
                "Answer:"
            )

            # 3. Generate final answer
            response = await self.llm_client.generate(composed_prompt)
            return response

        except Exception as e:
            logger.exception("Error in RAG pipeline for session %s", session_id)
            raise RuntimeError(f"RAG pipeline failed: {str(e)}") from e

# Dependencies for the singleton
def get_embedding_service():
    from app.services.embedding import EmbeddingService
    return EmbeddingService()

def get_vector_store():
    from app.services.vector_store import VectorStore
    return VectorStore()

# Singleton instance
def get_rag_service() -> RAGService:
    return RAGService(get_embedding_service(), get_vector_store(), llm_client)
