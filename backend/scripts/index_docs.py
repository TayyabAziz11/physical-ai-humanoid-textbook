"""
Document indexing script for RAG backend

Discovers markdown files, chunks content, generates embeddings, and uploads to Qdrant.

Usage:
    # Dry run (no API calls)
    uv run python -m scripts.index_docs --dry-run

    # Index first 5 docs only
    uv run python -m scripts.index_docs --limit 5

    # Index entire corpus
    uv run python -m scripts.index_docs
"""
import asyncio
import argparse
import re
import uuid
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import tiktoken

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.services.embeddings import embed_text
from app.services.qdrant import EmbeddingChunk, ensure_collection_exists, upsert_embeddings


# Constants
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"
CHUNK_MIN_TOKENS = 200
CHUNK_MAX_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50


def discover_markdown_files(docs_dir: Path) -> List[Path]:
    """
    Recursively discover all .md and .mdx files in docs directory

    Args:
        docs_dir: Path to docs directory

    Returns:
        List of Path objects for markdown files (sorted)
    """
    markdown_files = []

    # Glob for both .md and .mdx
    for pattern in ["**/*.md", "**/*.mdx"]:
        markdown_files.extend(docs_dir.glob(pattern))

    # Filter out build artifacts and node_modules
    markdown_files = [
        f for f in markdown_files
        if "node_modules" not in str(f)
        and ".docusaurus" not in str(f)
        and "build" not in str(f)
    ]

    return sorted(markdown_files)


def strip_yaml_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """
    Strip YAML frontmatter from markdown content

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


def extract_module_id(doc_path: Path, docs_root: Path) -> Optional[str]:
    """
    Extract module ID from document path

    Args:
        doc_path: Path to markdown file
        docs_root: Root docs directory

    Returns:
        Module ID (e.g., "module-1-ros2") or None
    """
    relative_path = doc_path.relative_to(docs_root)
    parts = relative_path.parts

    # Look for module-N-* pattern
    for part in parts:
        if part.startswith("module-"):
            return part

    return None


def clean_markdown_content(content: str) -> str:
    """
    Clean markdown content by removing JSX/React components and import statements

    Args:
        content: Markdown content

    Returns:
        Cleaned content
    """
    # Remove import statements
    content = re.sub(r'^import\s+.*?;?\s*$', '', content, flags=re.MULTILINE)

    # Remove JSX/React components (like <ChapterActionsBar />)
    content = re.sub(r'<[A-Z][^>]*?/?>', '', content)

    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    return content.strip()


def extract_headings_and_content(content: str) -> List[Tuple[str, str]]:
    """
    Extract headings and their content sections from markdown

    Args:
        content: Markdown content without frontmatter

    Returns:
        List of (heading, content) tuples
    """
    sections = []

    # Clean content first
    content = clean_markdown_content(content)

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
                section_text = "\n".join(current_content).strip()
                if section_text:
                    sections.append((current_heading, section_text))

            # Start new section
            current_heading = match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    # Save final section
    if current_content:
        section_text = "\n".join(current_content).strip()
        if section_text:
            sections.append((current_heading, section_text))

    return sections


def chunk_text_by_tokens(
    text: str,
    min_tokens: int = CHUNK_MIN_TOKENS,
    max_tokens: int = CHUNK_MAX_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS
) -> List[str]:
    """
    Chunk text into pieces based on token count

    Args:
        text: Text to chunk
        min_tokens: Minimum tokens per chunk
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Overlap between chunks

    Returns:
        List of text chunks
    """
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)

    # If text is already small enough, return as single chunk
    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    start = 0

    while start < len(tokens):
        # Determine end position
        end = min(start + max_tokens, len(tokens))

        # Extract chunk tokens
        chunk_tokens = tokens[start:end]

        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

        # Move start position with overlap
        if end >= len(tokens):
            break

        start = end - overlap_tokens

    return chunks


async def process_document(
    file_path: Path,
    docs_root: Path,
    dry_run: bool = False
) -> List[EmbeddingChunk]:
    """
    Process a single document: parse, chunk, and prepare for embedding

    Args:
        file_path: Path to markdown file
        docs_root: Root docs directory
        dry_run: If True, skip actual embedding generation

    Returns:
        List of EmbeddingChunk objects
    """
    logger = get_logger(__name__)

    # Read file
    content = file_path.read_text(encoding="utf-8")

    # Strip frontmatter
    frontmatter, body = strip_yaml_frontmatter(content)
    doc_title = frontmatter.get("title", file_path.stem)

    # Extract metadata
    relative_path = file_path.relative_to(docs_root.parent)
    doc_path = str(relative_path).replace("\\", "/")  # Normalize path separators
    module_id = extract_module_id(file_path, docs_root)

    # Extract sections by heading
    sections = extract_headings_and_content(body)

    if not sections:
        logger.warning(f"No content sections found in {file_path.name}")
        return []

    logger.debug(f"Extracted {len(sections)} sections from {file_path.name}")

    # Process each section
    all_chunks = []

    for heading, section_content in sections:
        # Chunk section content
        text_chunks = chunk_text_by_tokens(section_content, CHUNK_MIN_TOKENS, CHUNK_MAX_TOKENS)

        logger.debug(f"  Section '{heading}': {len(text_chunks)} chunks")

        for chunk_index, chunk_text in enumerate(text_chunks):
            # Generate embedding (skip if dry run)
            if dry_run:
                # Use dummy vector for dry run
                vector = [0.0] * 1536
            else:
                vector = await embed_text(chunk_text)

            # Create EmbeddingChunk
            chunk = EmbeddingChunk(
                id=str(uuid.uuid4()),
                vector=vector,
                doc_path=doc_path,
                module_id=module_id,
                heading=heading,
                chunk_text=chunk_text,
                chunk_index=chunk_index,
                total_chunks=len(text_chunks)
            )

            all_chunks.append(chunk)

    return all_chunks


async def main(dry_run: bool = False, limit: Optional[int] = None):
    """
    Main indexing function

    Args:
        dry_run: If True, parse and print summary without API calls
        limit: If set, index only first N documents
    """
    settings = get_settings()
    logger = setup_logging(settings.LOG_LEVEL)

    logger.info("=" * 70)
    logger.info("Document Indexing Script")
    logger.info("=" * 70)

    if dry_run:
        logger.info("🔍 DRY RUN MODE - No API calls will be made")

    # Discover markdown files
    logger.info(f"Discovering markdown files in {DOCS_DIR}...")
    markdown_files = discover_markdown_files(DOCS_DIR)

    if not markdown_files:
        logger.error(f"No markdown files found in {DOCS_DIR}")
        return

    logger.info(f"Found {len(markdown_files)} markdown files")

    # Apply limit if specified
    if limit:
        markdown_files = markdown_files[:limit]
        logger.info(f"Limiting to first {limit} files")

    # Ensure collection exists (skip if dry run)
    if not dry_run:
        logger.info(f"Ensuring Qdrant collection '{settings.QDRANT_COLLECTION}' exists...")
        try:
            ensure_collection_exists()
            logger.info("✅ Collection ready")
        except Exception as e:
            logger.error(f"❌ Failed to ensure collection exists: {e}")
            logger.error("Make sure QDRANT_URL and QDRANT_API_KEY are configured")
            return

    # Process each file
    total_chunks = 0
    all_chunks_to_upload = []

    for file_idx, file_path in enumerate(markdown_files, 1):
        logger.info(f"\n[{file_idx}/{len(markdown_files)}] Processing: {file_path.relative_to(DOCS_DIR.parent)}")

        try:
            # Process document
            chunks = await process_document(file_path, DOCS_DIR, dry_run=dry_run)

            logger.info(f"  Generated {len(chunks)} chunks")
            total_chunks += len(chunks)

            all_chunks_to_upload.extend(chunks)

            # Batch upload every 100 chunks (skip if dry run)
            if not dry_run and len(all_chunks_to_upload) >= 100:
                logger.info(f"  Uploading batch of {len(all_chunks_to_upload)} chunks...")
                try:
                    upsert_embeddings(all_chunks_to_upload)
                    logger.info("  ✅ Batch uploaded successfully")
                    all_chunks_to_upload = []
                except Exception as e:
                    logger.error(f"  ❌ Failed to upload batch: {e}")
                    # Continue processing other files

        except Exception as e:
            logger.error(f"  ❌ Error processing {file_path.name}: {e}")
            continue

    # Upload remaining chunks (skip if dry run)
    if not dry_run and all_chunks_to_upload:
        logger.info(f"\nUploading final batch of {len(all_chunks_to_upload)} chunks...")
        try:
            upsert_embeddings(all_chunks_to_upload)
            logger.info("✅ Final batch uploaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to upload final batch: {e}")

    # Summary
    logger.info("\n" + "=" * 70)
    if dry_run:
        logger.info("✅ DRY RUN COMPLETE")
    else:
        logger.info("✅ INDEXING COMPLETE")
    logger.info(f"Files processed: {len(markdown_files)}")
    logger.info(f"Total chunks generated: {total_chunks}")
    if not dry_run:
        logger.info(f"Collection: {settings.QDRANT_COLLECTION}")
    logger.info("=" * 70)


def cli():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Index markdown documents for RAG backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (parse only, no API calls)
  uv run python -m scripts.index_docs --dry-run

  # Index first 5 documents
  uv run python -m scripts.index_docs --limit 5

  # Index entire corpus
  uv run python -m scripts.index_docs
        """
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and print summary without making API calls"
    )

    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="Index only first N documents (for testing)"
    )

    args = parser.parse_args()

    # Run async main
    asyncio.run(main(dry_run=args.dry_run, limit=args.limit))


if __name__ == "__main__":
    cli()
