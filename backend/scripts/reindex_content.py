#!/usr/bin/env python3
"""
CLI script for re-indexing book content into Qdrant vector database.

This script can be run directly from the command line to trigger a full re-index
of the documentation content.

Usage:
    python scripts/reindex_content.py --docs-dir ./docs
    python scripts/reindex_content.py --docs-dir /path/to/docs

The script uses the atomic swap strategy to ensure zero-downtime re-indexing:
1. Creates a new temporary collection
2. Indexes all documents into the temp collection
3. Swaps the alias to point to the new collection
4. Deletes the old collection
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path to allow imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.logging import get_logger
from app.services.indexer import IndexingService

logger = get_logger(__name__)


async def main():
    """Main entry point for the re-indexing CLI script."""
    parser = argparse.ArgumentParser(
        description="Re-index book content into Qdrant vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Re-index docs from default location
  python scripts/reindex_content.py --docs-dir ./docs

  # Re-index from custom location
  python scripts/reindex_content.py --docs-dir /path/to/documentation

  # Show help
  python scripts/reindex_content.py --help

This script uses the following configuration from environment variables:
  - QDRANT_URL: Qdrant server URL
  - QDRANT_API_KEY: Qdrant API key
  - QDRANT_COLLECTION: Collection name (used as alias)
  - OPENAI_API_KEY: OpenAI API key for embeddings
  - OPENAI_EMBEDDING_MODEL: OpenAI embedding model to use
        """,
    )

    parser.add_argument(
        "--docs-dir",
        type=str,
        default="./docs",
        help="Path to documentation directory (default: ./docs)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Validate docs directory
    docs_path = Path(args.docs_dir)
    if not docs_path.exists():
        logger.error(f"Documentation directory not found: {args.docs_dir}")
        print(f"❌ Error: Documentation directory not found: {args.docs_dir}")
        sys.exit(1)

    if not docs_path.is_dir():
        logger.error(f"Path is not a directory: {args.docs_dir}")
        print(f"❌ Error: Path is not a directory: {args.docs_dir}")
        sys.exit(1)

    # Print configuration
    print("=" * 80)
    print("RAG Chatbot Content Re-indexing")
    print("=" * 80)
    print(f"Documentation directory: {args.docs_dir}")
    print(f"Qdrant URL: {settings.QDRANT_URL}")
    print(f"Qdrant collection (alias): {settings.QDRANT_COLLECTION}")
    print(f"OpenAI embedding model: {settings.OPENAI_EMBEDDING_MODEL}")
    print(f"Verbose logging: {args.verbose}")
    print("=" * 80)
    print()

    # Create indexing service
    indexer = IndexingService()

    try:
        # Run re-indexing
        print("🔄 Starting re-indexing process...")
        print()

        result = await indexer.reindex_full(args.docs_dir)

        print()
        print("=" * 80)

        if result.status == "completed":
            print("✅ Re-indexing completed successfully!")
            print()
            print(f"📊 Summary:")
            print(f"  - Total files processed: {result.total_files}")
            print(f"  - Total chunks created: {result.total_chunks}")
            print(f"  - Duration: {result.duration_seconds:.2f} seconds")
            print()
            print(f"💡 The collection '{settings.QDRANT_COLLECTION}' is now ready for queries.")
            print("=" * 80)
            sys.exit(0)

        else:
            print("❌ Re-indexing failed!")
            print()
            print(f"Status: {result.status}")
            print(f"Duration: {result.duration_seconds:.2f} seconds")
            print()
            print("Please check the logs for more details.")
            print("=" * 80)
            sys.exit(1)

    except KeyboardInterrupt:
        print()
        print("⚠️  Re-indexing interrupted by user")
        print("=" * 80)
        sys.exit(130)

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Re-indexing failed with error: {e}")
        print("=" * 80)
        logger.error(f"Re-indexing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
