"""
Content indexing service for RAG chatbot.

Handles parsing, chunking, embedding, and uploading book content to Qdrant.
Implements atomic swap strategy for zero-downtime re-indexing.
"""

import asyncio
import time
import uuid
from pathlib import Path
from typing import List

from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.core.logging import get_logger
from app.db.qdrant import get_qdrant_client
from app.models.chunk import ContentChunk
from app.models.response import ReindexResponse
from app.services.chunker import ContentChunker
from app.services.embedder import EmbeddingService
from app.services.parser import MarkdownParser

logger = get_logger(__name__)


class IndexingService:
    """Service for indexing book content into Qdrant vector database."""

    def __init__(self):
        """Initialize the indexing service."""
        self.parser = MarkdownParser()
        self.chunker = ContentChunker()
        self.embedder = EmbeddingService()
        self.client = get_qdrant_client()
        self.logger = get_logger(__name__)

    async def index_documents(self, docs_dir: str) -> dict:
        """Index all markdown documents from a directory."""
        docs_path = Path(docs_dir)

        if not docs_path.exists():
            raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")

        self.logger.info(f"Scanning for markdown files in: {docs_dir}")

        md_files = list(docs_path.rglob("*.md"))
        self.logger.info(f"Found {len(md_files)} markdown files")

        all_chunks: List[ContentChunk] = []

        for file_path in md_files:
            try:
                self.logger.info(f"Processing file: {file_path}")
                metadata, sections = self.parser.parse_file(file_path)

                if not sections:
                    self.logger.warning(f"No sections found in {file_path}, skipping")
                    continue

                chunks = self.chunker.chunk_sections(sections)

                if chunks:
                    all_chunks.extend(chunks)
                    self.logger.info(f"Created {len(chunks)} chunks from {file_path}")

            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}", exc_info=True)
                continue

        if all_chunks:
            self.logger.info(f"Generating embeddings for {len(all_chunks)} chunks")
            embedded_chunks = await self.embedder.embed_chunks(all_chunks)
        else:
            self.logger.warning("No chunks created from any files")
            embedded_chunks = []

        summary = {
            "total_files": len(md_files),
            "total_chunks": len(embedded_chunks),
            "chunks": embedded_chunks,
        }

        self.logger.info(
            f"Indexing complete: {summary['total_files']} files, {summary['total_chunks']} chunks"
        )

        return summary

    async def upsert_chunks_to_qdrant(
        self, chunks: List[ContentChunk], collection_name: str
    ) -> None:
        """Upload chunks to Qdrant in batches."""
        if not chunks:
            self.logger.warning("No chunks to upload")
            return

        self.logger.info(f"Uploading {len(chunks)} chunks to collection: {collection_name}")

        batch_size = 100
        total_batches = (len(chunks) + batch_size - 1) // batch_size

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = (i // batch_size) + 1

            self.logger.info(f"Uploading batch {batch_num}/{total_batches}")

            points = []
            for chunk in batch:
                # Use UUID-safe chunk ID
                chunk_id = str(uuid.uuid4())
                try:
                    point = chunk.to_qdrant_point(chunk_id)
                    points.append(point)
                except ValueError as e:
                    self.logger.error(f"Skipping chunk {chunk_id}: {e}")
                    continue

            if points:
                self.client.upsert(collection_name=collection_name, points=points)
                self.logger.info(f"Uploaded batch {batch_num}/{total_batches} ({len(points)} points)")

        self.logger.info(f"Successfully uploaded all chunks to {collection_name}")

    async def reindex_full(self, docs_dir: str = "./docs") -> ReindexResponse:
        """Perform full re-indexing with safe atomic swap strategy."""
        start_time = time.time()

        try:
            timestamp = int(time.time())
            temp_collection = f"{settings.QDRANT_COLLECTION}_temp_{timestamp}"
            alias_name = settings.QDRANT_COLLECTION

            self.logger.info("=" * 80)
            self.logger.info("Starting full re-indexing with atomic swap strategy")
            self.logger.info(f"Documentation directory: {docs_dir}")
            self.logger.info(f"Temporary collection: {temp_collection}")
            self.logger.info(f"Alias name: {alias_name}")
            self.logger.info("=" * 80)

            # Step 1: Create temporary collection
            self.logger.info("[1/5] Creating temporary collection...")
            self.client.create_collection(
                collection_name=temp_collection,
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE,
                ),
            )
            self.logger.info(f"✓ Created collection: {temp_collection}")

            # Step 2: Index documents
            self.logger.info("[2/5] Indexing documents...")
            index_result = await self.index_documents(docs_dir)
            total_files = index_result["total_files"]
            total_chunks = index_result["total_chunks"]
            chunks = index_result["chunks"]
            self.logger.info(f"✓ Indexed {total_files} files into {total_chunks} chunks")

            # Step 3: Upload to temporary collection
            self.logger.info("[3/5] Uploading chunks to Qdrant...")
            await self.upsert_chunks_to_qdrant(chunks, temp_collection)
            self.logger.info(f"✓ Uploaded {total_chunks} chunks to {temp_collection}")

            # Step 4: Safe atomic swap
            self.logger.info("[4/5] Performing safe atomic swap...")

            # If a collection exists with the alias name, delete it first
            existing_collections = [col.name for col in self.client.get_collections().collections]
            if alias_name in existing_collections:
                self.logger.info(f"Found existing collection with alias name: {alias_name}")
                self.client.delete_collection(alias_name)
                self.logger.info(f"✓ Deleted old collection: {alias_name}")

            # Create alias pointing to the new temp collection
            self.client.update_collection_aliases(
                change_aliases_operations=[
                    {"create_alias": {"collection_name": temp_collection, "alias_name": alias_name}}
                ]
            )
            self.logger.info(f"✓ Alias '{alias_name}' now points to {temp_collection}")

            duration = time.time() - start_time
            self.logger.info("=" * 80)
            self.logger.info("Re-indexing completed successfully!")
            self.logger.info(f"Total files: {total_files}")
            self.logger.info(f"Total chunks: {total_chunks}")
            self.logger.info(f"Duration: {duration:.2f}s")
            self.logger.info("=" * 80)

            return ReindexResponse(
                status="completed",
                total_files=total_files,
                total_chunks=total_chunks,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Re-indexing failed: {e}", exc_info=True)

            return ReindexResponse(
                status="failed",
                total_files=0,
                total_chunks=0,
                duration_seconds=duration,
            )
