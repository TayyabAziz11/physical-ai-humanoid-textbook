"""Content chunking service with heading-aware and code dual-chunking strategy."""

import tiktoken
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.models.chunk import ContentChunk
from app.services.parser import MarkdownParser, MarkdownSection

logger = get_logger(__name__)


class ContentChunker:
    """
    Chunker implementing dual-chunking strategy for code blocks.

    Strategy (Option C - user's explicit choice):
    - Code blocks are included both:
      1. Within their surrounding text context (text_with_code chunks)
      2. As separate standalone chunks (code_only chunks)
    - This ensures code is findable both in context and isolation
    """

    def __init__(self, max_tokens: int | None = None):
        """
        Initialize the content chunker.

        Args:
            max_tokens: Maximum tokens per chunk (defaults to settings.RAG_CHUNK_MAX_TOKENS)
        """
        self.max_tokens = max_tokens or settings.RAG_CHUNK_MAX_TOKENS
        self.parser = MarkdownParser()

        # Initialize tiktoken encoder
        try:
            self.encoding = tiktoken.encoding_for_model(settings.OPENAI_EMBEDDING_MODEL)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

        self.logger = get_logger(__name__)

    def chunk_sections(self, sections: list[MarkdownSection]) -> list[ContentChunk]:
        """
        Chunk markdown sections into ContentChunk objects.

        Implements dual-chunking strategy:
        - Sections with code get two types of chunks:
          1. text_with_code: Full section content including code
          2. code_only: Extracted code blocks as separate chunks
        - Sections without code get only text_with_code chunks

        Args:
            sections: List of MarkdownSection objects from parser

        Returns:
            List of ContentChunk objects ready for embedding
        """
        all_chunks: list[ContentChunk] = []
        chunk_index = 0

        for section in sections:
            self.logger.debug(
                f"Chunking section: {section.heading} (level {section.level}, "
                f"{len(section.content)} chars)"
            )

            # Check if section has code blocks
            has_code = self.parser.has_code_blocks(section.content)

            if has_code:
                # Strategy: Dual-chunking for code blocks
                # 1. Create text_with_code chunks (section content including code)
                text_chunks = self._create_text_chunks(
                    section, chunk_index, chunk_type="text_with_code"
                )
                all_chunks.extend(text_chunks)
                chunk_index += len(text_chunks)

                # 2. Create code_only chunks (extracted code blocks)
                code_chunks = self._create_code_chunks(section, chunk_index)
                all_chunks.extend(code_chunks)
                chunk_index += len(code_chunks)
            else:
                # No code: just create text_with_code chunks
                text_chunks = self._create_text_chunks(
                    section, chunk_index, chunk_type="text_with_code"
                )
                all_chunks.extend(text_chunks)
                chunk_index += len(text_chunks)

        self.logger.info(f"Created {len(all_chunks)} total chunks from {len(sections)} sections")
        return all_chunks

    def _create_text_chunks(
        self,
        section: MarkdownSection,
        start_index: int,
        chunk_type: str = "text_with_code",
    ) -> list[ContentChunk]:
        """
        Create text chunks from a section, respecting token limits.

        Args:
            section: MarkdownSection to chunk
            start_index: Starting chunk index
            chunk_type: Type of chunk ('text_with_code' or 'code_only')

        Returns:
            List of ContentChunk objects
        """
        chunks: list[ContentChunk] = []
        content = section.content.strip()

        if not content:
            return chunks

        # Count tokens in full content
        tokens = self.encoding.encode(content)
        total_tokens = len(tokens)

        if total_tokens <= self.max_tokens:
            # Content fits in single chunk
            chunk = self._create_chunk(
                text=content,
                section=section,
                chunk_index=start_index,
                chunk_type=chunk_type,
            )
            chunks.append(chunk)
        else:
            # Split content into multiple chunks
            # Simple strategy: split by paragraphs and group until max_tokens
            paragraphs = content.split("\n\n")
            current_chunk_text = ""
            current_tokens = 0
            chunk_count = 0

            for para in paragraphs:
                para_tokens = len(self.encoding.encode(para))

                if current_tokens + para_tokens <= self.max_tokens:
                    # Add paragraph to current chunk
                    if current_chunk_text:
                        current_chunk_text += "\n\n" + para
                    else:
                        current_chunk_text = para
                    current_tokens += para_tokens
                else:
                    # Flush current chunk and start new one
                    if current_chunk_text:
                        chunk = self._create_chunk(
                            text=current_chunk_text,
                            section=section,
                            chunk_index=start_index + chunk_count,
                            chunk_type=chunk_type,
                        )
                        chunks.append(chunk)
                        chunk_count += 1

                    # Start new chunk with current paragraph
                    current_chunk_text = para
                    current_tokens = para_tokens

            # Flush final chunk
            if current_chunk_text:
                chunk = self._create_chunk(
                    text=current_chunk_text,
                    section=section,
                    chunk_index=start_index + chunk_count,
                    chunk_type=chunk_type,
                )
                chunks.append(chunk)

        return chunks

    def _create_code_chunks(
        self, section: MarkdownSection, start_index: int
    ) -> list[ContentChunk]:
        """
        Create code_only chunks from code blocks in a section.

        Args:
            section: MarkdownSection containing code blocks
            start_index: Starting chunk index

        Returns:
            List of ContentChunk objects with chunk_type='code_only'
        """
        chunks: list[ContentChunk] = []
        code_blocks = self.parser.extract_code_blocks(section.content)

        for i, code_block in enumerate(code_blocks):
            # Create metadata for code chunk
            metadata = self._build_metadata(section, start_index + i)
            metadata["language"] = code_block["language"]

            chunk = ContentChunk(
                text=code_block["code"],
                metadata=metadata,
                chunk_type="code_only",
                embedding=None,  # Will be populated by embedder
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        text: str,
        section: MarkdownSection,
        chunk_index: int,
        chunk_type: str,
    ) -> ContentChunk:
        """
        Create a single ContentChunk with metadata.

        Args:
            text: Chunk text content
            section: Source MarkdownSection
            chunk_index: Index of this chunk
            chunk_type: Type of chunk

        Returns:
            ContentChunk object
        """
        metadata = self._build_metadata(section, chunk_index)

        return ContentChunk(
            text=text,
            metadata=metadata,
            chunk_type=chunk_type,  # type: ignore
            embedding=None,  # Will be populated by embedder
        )

    def _build_metadata(self, section: MarkdownSection, chunk_index: int) -> dict[str, Any]:
        """
        Build metadata dictionary for a chunk.

        Args:
            section: Source MarkdownSection
            chunk_index: Index of this chunk

        Returns:
            Metadata dictionary
        """
        return {
            "source_file": section.source_file,
            "section_title": section.heading,
            "heading_hierarchy": section.heading_hierarchy,
            "chunk_index": chunk_index,
            "heading_level": section.level,
            "line_number": section.line_number,
        }

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Token count
        """
        return len(self.encoding.encode(text))
