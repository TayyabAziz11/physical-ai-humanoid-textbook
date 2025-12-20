"""Markdown parser for extracting structured content from documentation files."""

import re
from pathlib import Path
from typing import Any

import frontmatter

from app.core.logging import get_logger

logger = get_logger(__name__)


class MarkdownSection:
    """Represents a section of markdown content with heading hierarchy."""

    def __init__(
        self,
        heading: str,
        level: int,
        content: str,
        heading_hierarchy: list[str],
        source_file: str,
        line_number: int,
    ):
        """
        Initialize a markdown section.

        Args:
            heading: The heading text (without # markers)
            level: Heading level (1-6)
            content: The content under this heading (until next heading)
            heading_hierarchy: List of parent headings leading to this section
            source_file: Path to the source markdown file
            line_number: Line number where this section starts
        """
        self.heading = heading
        self.level = level
        self.content = content
        self.heading_hierarchy = heading_hierarchy
        self.source_file = source_file
        self.line_number = line_number

    def __repr__(self) -> str:
        return f"MarkdownSection(heading='{self.heading}', level={self.level}, line={self.line_number})"


class MarkdownParser:
    """Parser for extracting structured content from markdown files."""

    # Regex pattern for markdown headings
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    # Regex pattern for code blocks
    CODE_BLOCK_PATTERN = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

    def __init__(self):
        """Initialize the markdown parser."""
        self.logger = get_logger(__name__)

    def parse_file(self, file_path: str | Path) -> tuple[dict[str, Any], list[MarkdownSection]]:
        """
        Parse a markdown file into frontmatter metadata and sections.

        Args:
            file_path: Path to the markdown file

        Returns:
            Tuple of (frontmatter_metadata, list_of_sections)

        Raises:
            FileNotFoundError: If the file doesn't exist
            UnicodeDecodeError: If the file encoding is invalid
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.info(f"Parsing markdown file: {file_path}")

        # Parse frontmatter and content
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        metadata = post.metadata
        content = post.content

        # Extract sections with heading hierarchy
        sections = self._extract_sections(content, str(file_path))

        self.logger.info(f"Extracted {len(sections)} sections from {file_path}")
        return metadata, sections

    def _extract_sections(self, content: str, source_file: str) -> list[MarkdownSection]:
        """
        Extract sections from markdown content based on headings.

        Args:
            content: Markdown content string
            source_file: Path to source file for metadata

        Returns:
            List of MarkdownSection objects
        """
        sections: list[MarkdownSection] = []
        lines = content.split("\n")

        # Find all heading positions
        heading_matches = []
        for match in self.HEADING_PATTERN.finditer(content):
            line_number = content[:match.start()].count("\n") + 1
            level = len(match.group(1))  # Number of # characters
            heading_text = match.group(2).strip()
            heading_matches.append((line_number, level, heading_text, match.start()))

        # Build heading hierarchy stack
        hierarchy_stack: list[tuple[int, str]] = []  # [(level, heading), ...]

        for i, (line_num, level, heading_text, start_pos) in enumerate(heading_matches):
            # Update hierarchy stack based on current level
            # Remove headings at same or deeper level
            while hierarchy_stack and hierarchy_stack[-1][0] >= level:
                hierarchy_stack.pop()

            # Add current heading to stack
            hierarchy_stack.append((level, heading_text))

            # Build heading hierarchy list (excludes current heading)
            heading_hierarchy = [h for _, h in hierarchy_stack[:-1]]

            # Extract content from this heading to next heading (or end)
            if i + 1 < len(heading_matches):
                next_start = heading_matches[i + 1][3]
                section_content = content[start_pos:next_start]
            else:
                section_content = content[start_pos:]

            # Remove the heading line itself from content
            section_lines = section_content.split("\n", 1)
            if len(section_lines) > 1:
                section_content = section_lines[1].strip()
            else:
                section_content = ""

            # Create section object
            section = MarkdownSection(
                heading=heading_text,
                level=level,
                content=section_content,
                heading_hierarchy=heading_hierarchy,
                source_file=source_file,
                line_number=line_num,
            )
            sections.append(section)

        return sections

    def extract_code_blocks(self, content: str) -> list[dict[str, str]]:
        """
        Extract code blocks from markdown content.

        Args:
            content: Markdown content string

        Returns:
            List of dicts with 'language' and 'code' keys
        """
        code_blocks = []
        for match in self.CODE_BLOCK_PATTERN.finditer(content):
            language = match.group(1) or "text"
            code = match.group(2).strip()
            code_blocks.append({"language": language, "code": code})

        return code_blocks

    def has_code_blocks(self, content: str) -> bool:
        """
        Check if content contains any code blocks.

        Args:
            content: Markdown content string

        Returns:
            True if code blocks are present, False otherwise
        """
        return bool(self.CODE_BLOCK_PATTERN.search(content))
