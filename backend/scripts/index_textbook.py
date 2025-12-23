"""
Textbook indexing script

Discovers all .md and .mdx files in ../docs, chunks them, generates embeddings,
and uploads to Qdrant vector database for RAG retrieval.

Usage:
    uv run python backend/scripts/index_textbook.py
"""
import asyncio
import re
import uuid
from pathlib import Path
from typing import List, Dict, Tuple
import tiktoken
from openai import OpenAI
from qdrant_client.models import PointStruct

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.services.qdrant_client import get_qdrant_client, ensure_collection_exists


# Constants
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"
CHUNK_MAX_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50


def discover_markdown_files(docs_dir: Path) -> List[Path]:
    """
    Recursively discover all .md and .mdx files in the docs directory

    Args:
        docs_dir: Path to docs directory

    Returns:
        List of Path objects for markdown files
    """
    markdown_files = []
    for pattern in ["**/*.md", "**/*.mdx"]:
        markdown_files.extend(docs_dir.glob(pattern))

    # Filter out node_modules and other build artifacts
    markdown_files = [
        f for f in markdown_files
        if "node_modules" not in str(f) and ".docusaurus" not in str(f)
    ]

    return sorted(markdown_files)


def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """
    Parse YAML frontmatter from markdown content

    Args:
        content: Full markdown file content

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    frontmatter = {}
    body = content

    # Check for frontmatter delimiters (---)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()

            # Parse YAML (simple key: value pairs)
            for line in frontmatter_text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, body


def extract_headings_and_sections(content: str) -> List[Tuple[str, str]]:
    """
    Extract headings and their content sections from markdown

    Args:
        content: Markdown content without frontmatter

    Returns:
        List of (heading, content) tuples
    """
    sections = []

    # Remove import statements (common in .mdx files)
    content = re.sub(r'^import\s+.*?;?\s*$', '', content, flags=re.MULTILINE)

    # Remove JSX/React components (like <ChapterActionsBar />)
    content = re.sub(r'<[A-Z][^>]*?/?>', '', content)

    # Split by headings (# or ##)
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    lines = content.split("\n")

    current_heading = "Introduction"
    current_content = []

    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            # Save previous section
            if current_content:
                sections.append((current_heading, "\n".join(current_content).strip()))

            # Start new section
            current_heading = match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    # Save final section
    if current_content:
        sections.append((current_heading, "\n".join(current_content).strip()))

    # Filter out empty sections
    sections = [(h, c) for h, c in sections if c.strip()]

    return sections


def chunk_text(text: str, max_tokens: int = CHUNK_MAX_TOKENS, overlap_tokens: int = CHUNK_OVERLAP_TOKENS) -> List[str]:
    """
    Split text into chunks with token-based sizing and overlap

    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Overlap between chunks

    Returns:
        List of text chunks
    """
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

        # Move start position with overlap
        start = end - overlap_tokens
        if start >= len(tokens):
            break

    return chunks


def generate_embedding(text: str, client: OpenAI, model: str) -> List[float]:
    """
    Generate embedding vector for text using OpenAI API

    Args:
        text: Text to embed
        client: OpenAI client
        model: Embedding model name

    Returns:
        Embedding vector (list of floats)
    """
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding


async def index_textbook():
    """
    Main indexing function

    Discovers all markdown files, chunks them, generates embeddings,
    and uploads to Qdrant.
    """
    settings = get_settings()
    logger = setup_logging(settings.LOG_LEVEL)

    logger.info("=" * 60)
    logger.info("Starting textbook indexing process")
    logger.info("=" * 60)

    # Initialize clients
    logger.info("Initializing OpenAI and Qdrant clients...")
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    qdrant_client = get_qdrant_client()

    # Ensure collection exists
    logger.info(f"Ensuring collection '{settings.QDRANT_COLLECTION}' exists...")
    ensure_collection_exists()

    # Discover markdown files
    logger.info(f"Discovering markdown files in {DOCS_DIR}...")
    markdown_files = discover_markdown_files(DOCS_DIR)
    logger.info(f"Found {len(markdown_files)} markdown files")

    if not markdown_files:
        logger.warning("No markdown files found. Exiting.")
        return

    # Process each file
    total_chunks = 0
    points_to_upload = []

    for file_idx, file_path in enumerate(markdown_files, 1):
        logger.info(f"\n[{file_idx}/{len(markdown_files)}] Processing: {file_path.relative_to(DOCS_DIR.parent)}")

        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")

            # Parse frontmatter
            frontmatter, body = parse_frontmatter(content)
            doc_title = frontmatter.get("title", file_path.stem)

            # Extract sections by heading
            sections = extract_headings_and_sections(body)
            logger.info(f"  Extracted {len(sections)} sections")

            # Process each section
            for heading, section_content in sections:
                if not section_content.strip():
                    continue

                # Chunk section content
                chunks = chunk_text(section_content, max_tokens=settings.RAG_CHUNK_MAX_TOKENS)
                logger.info(f"  Section '{heading}': {len(chunks)} chunks")

                # Generate embeddings and prepare points
                for chunk_idx, chunk in enumerate(chunks):
                    # Generate embedding
                    embedding = generate_embedding(
                        chunk,
                        openai_client,
                        settings.OPENAI_EMBEDDING_MODEL
                    )

                    # Create Qdrant point
                    point_id = str(uuid.uuid4())
                    doc_path = str(file_path.relative_to(DOCS_DIR.parent))

                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "doc_path": doc_path,
                            "doc_title": doc_title,
                            "heading": heading,
                            "chunk_text": chunk,
                            "chunk_index": chunk_idx,
                            "total_chunks_in_section": len(chunks)
                        }
                    )

                    points_to_upload.append(point)
                    total_chunks += 1

                    # Batch upload every 100 points
                    if len(points_to_upload) >= 100:
                        logger.info(f"  Uploading batch of {len(points_to_upload)} points...")
                        qdrant_client.upsert(
                            collection_name=settings.QDRANT_COLLECTION,
                            points=points_to_upload
                        )
                        points_to_upload = []

        except Exception as e:
            logger.error(f"  ❌ Error processing {file_path.name}: {e}")
            continue

    # Upload remaining points
    if points_to_upload:
        logger.info(f"\nUploading final batch of {len(points_to_upload)} points...")
        qdrant_client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points_to_upload
        )

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("✅ Indexing completed successfully!")
    logger.info(f"Total files processed: {len(markdown_files)}")
    logger.info(f"Total chunks indexed: {total_chunks}")
    logger.info(f"Collection: {settings.QDRANT_COLLECTION}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(index_textbook())
