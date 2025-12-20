"""Embedding service for generating vector embeddings using OpenAI API."""

import asyncio
from typing import List

from openai import AsyncOpenAI, OpenAIError, RateLimitError

from app.core.config import settings
from app.core.logging import get_logger
from app.models.chunk import ContentChunk

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI's embedding API."""

    def __init__(self, batch_size: int = 100, max_retries: int = 3):
        """
        Initialize the embedding service.

        Args:
            batch_size: Number of texts to embed in a single API call (max 100 for OpenAI)
            max_retries: Maximum number of retry attempts for failed API calls
        """
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.batch_size = min(batch_size, 100)  # OpenAI max is 100
        self.max_retries = max_retries
        self.logger = get_logger(__name__)

    async def embed_chunks(self, chunks: list[ContentChunk]) -> list[ContentChunk]:
        """
        Generate embeddings for a list of ContentChunk objects.

        Processes chunks in batches and updates each chunk's embedding field.

        Args:
            chunks: List of ContentChunk objects to embed

        Returns:
            List of ContentChunk objects with embeddings populated

        Raises:
            OpenAIError: If API calls fail after all retries
        """
        if not chunks:
            return []

        self.logger.info(f"Generating embeddings for {len(chunks)} chunks")

        # Process chunks in batches
        embedded_chunks: list[ContentChunk] = []

        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(chunks) + self.batch_size - 1) // self.batch_size

            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")

            # Extract texts from batch
            texts = [chunk.text for chunk in batch]

            # Generate embeddings with retries
            embeddings = await self._embed_texts_with_retry(texts)

            # Update chunks with embeddings
            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding
                embedded_chunks.append(chunk)

        self.logger.info(f"Successfully embedded {len(embedded_chunks)} chunks")
        return embedded_chunks

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats

        Raises:
            OpenAIError: If API call fails after all retries
        """
        embeddings = await self._embed_texts_with_retry([text])
        return embeddings[0]

    async def _embed_texts_with_retry(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts with retry logic.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors

        Raises:
            OpenAIError: If API call fails after all retries
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                )

                # Extract embeddings from response
                embeddings = [item.embedding for item in response.data]
                return embeddings

            except RateLimitError as e:
                if attempt < self.max_retries:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2**attempt
                    self.logger.warning(
                        f"Rate limit hit (attempt {attempt}/{self.max_retries}). "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(
                        f"Rate limit exceeded after {self.max_retries} attempts"
                    )
                    raise

            except OpenAIError as e:
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    self.logger.warning(
                        f"OpenAI API error (attempt {attempt}/{self.max_retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(
                        f"OpenAI API error after {self.max_retries} attempts: {e}"
                    )
                    raise

            except Exception as e:
                self.logger.error(f"Unexpected error during embedding: {e}")
                raise

        # Should never reach here due to raise in retry loops
        raise OpenAIError("Failed to generate embeddings after all retries")

    async def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for the configured model.

        Returns:
            Embedding dimension (1536 for text-embedding-3-small)
        """
        # For text-embedding-3-small, dimension is 1536
        # For text-embedding-3-large, dimension is 3072
        if "small" in self.model:
            return 1536
        elif "large" in self.model:
            return 3072
        else:
            # Default fallback
            return 1536
