"""Response generation service using OpenAI Chat API."""

import asyncio
from typing import Any

from openai import AsyncOpenAI, OpenAIError, RateLimitError

from app.core.config import settings
from app.core.logging import get_logger
from app.models.chunk import ContentChunk
from app.models.response import Citation

logger = get_logger(__name__)


class ResponseService:
    """Service for generating responses using OpenAI's chat completion API."""

    def __init__(self, max_retries: int = 3):
        """
        Initialize the response service.

        Args:
            max_retries: Maximum number of retry attempts for failed API calls
        """
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_CHAT_MODEL
        self.max_retries = max_retries
        self.logger = get_logger(__name__)

    async def generate_answer(
        self,
        question: str,
        retrieved_chunks: list[ContentChunk],
        conversation_history: list[dict[str, Any]] | None = None,
    ) -> tuple[str, list[Citation]]:
        """
        Generate an answer to a question using retrieved context chunks.

        Args:
            question: User's question
            retrieved_chunks: List of relevant ContentChunk objects from retrieval
            conversation_history: Optional conversation history for follow-up questions

        Returns:
            Tuple of (answer_text, list_of_citations)
        """
        self.logger.info(f"Generating answer for question: '{question[:100]}...'")

        # Assemble prompt with context
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(question, retrieved_chunks)

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current question with context
        messages.append({"role": "user", "content": user_prompt})

        # Generate response with retries
        answer = await self._generate_with_retry(messages)

        # Extract citations from retrieved chunks
        citations = self._extract_citations(retrieved_chunks)

        self.logger.info(
            f"Generated answer ({len(answer)} chars) with {len(citations)} citations"
        )

        return answer, citations

    async def generate_selection_answer(
        self,
        question: str,
        selected_text: str,
    ) -> str:
        """
        Generate an answer to a question about selected text (no retrieval).

        This enforces strict context isolation - the LLM only sees the selected text.

        Args:
            question: User's question about the selected text
            selected_text: The text selected by the user

        Returns:
            Answer text
        """
        self.logger.info(
            f"Generating selection-based answer for question: '{question[:100]}...'"
        )

        # Build constrained prompt for selection mode
        system_prompt = self._build_selection_system_prompt()
        user_prompt = self._build_selection_user_prompt(question, selected_text)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Generate response with retries
        answer = await self._generate_with_retry(messages)

        self.logger.info(f"Generated selection answer ({len(answer)} chars)")

        return answer

    async def generate_response_selection(
        self,
        question: str,
        selected_text: str,
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        Generate an answer to a question about selected text (alternative signature).

        This method enforces strict context isolation and returns empty citations
        as selection mode does not retrieve from the database.

        Args:
            question: User's question about the selected text
            selected_text: The text selected by the user

        Returns:
            Tuple of (answer_text, empty_citations_list)
        """
        answer = await self.generate_selection_answer(question, selected_text)

        # Return answer with empty citations (no retrieval in selection mode)
        return answer, []

    def _build_system_prompt(self) -> str:
        """
        Build system prompt for global query mode.

        Returns:
            System prompt string
        """
        return """You are a helpful AI assistant that answers questions about a technical book on Physical AI and Humanoid Robotics.

Your task is to:
1. Answer the user's question based ONLY on the provided context from the book
2. Be precise and cite specific sections when possible
3. If the context doesn't contain enough information, say so clearly
4. Use technical language appropriate for the book's audience
5. Format your answer in clear, readable markdown

Guidelines:
- Stay factual and grounded in the provided context
- Don't make up information not present in the context
- If multiple sections are relevant, synthesize them coherently
- Use code examples from the context when relevant
"""

    def _build_selection_system_prompt(self) -> str:
        """
        Build system prompt for selection query mode with strict context isolation.

        Returns:
            System prompt string
        """
        return """You are a helpful AI assistant that answers questions about a specific text selection from a technical book.

CRITICAL: Answer using ONLY the selected text provided below. DO NOT use external knowledge.

Your task is to:
1. Answer the user's question based EXCLUSIVELY on the provided selected text
2. Do not reference or draw on any external knowledge about the topic
3. If the selected text doesn't contain the answer, clearly state that
4. Be concise and directly address the question
5. Use quotes from the selection when helpful

STRICT REQUIREMENT: You must ignore all general knowledge about the topic and rely solely on the selected text. If the answer is not in the selected text, say "The selected text does not contain information to answer this question."
"""

    def _build_user_prompt(self, question: str, chunks: list[ContentChunk]) -> str:
        """
        Build user prompt with question and context chunks.

        Args:
            question: User's question
            chunks: Retrieved context chunks

        Returns:
            User prompt string
        """
        # Build context section from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.metadata
            section_title = metadata.get("section_title", "Unknown Section")
            source_file = metadata.get("source_file", "Unknown File")

            context_parts.append(
                f"[Context {i} - {section_title} from {source_file}]\n{chunk.text}\n"
            )

        context = "\n".join(context_parts)

        prompt = f"""Context from the book:

{context}

---

Question: {question}

Please answer the question based on the context provided above. If the context doesn't contain sufficient information to answer the question, say so clearly.
"""

        return prompt

    def _build_selection_user_prompt(self, question: str, selected_text: str) -> str:
        """
        Build user prompt for selection mode.

        Args:
            question: User's question
            selected_text: Text selected by the user

        Returns:
            User prompt string
        """
        prompt = f"""Selected text:

{selected_text}

---

Question: {question}

Please answer the question based ONLY on the selected text above.
"""

        return prompt

    def _extract_citations(self, chunks: list[ContentChunk]) -> list[Citation]:
        """
        Extract citations from retrieved chunks.

        Args:
            chunks: List of ContentChunk objects

        Returns:
            List of Citation objects
        """
        citations = []
        seen_sections = set()

        for chunk in chunks:
            metadata = chunk.metadata
            section_title = metadata.get("section_title", "Unknown Section")
            source_file = metadata.get("source_file", "Unknown File")

            # Avoid duplicate citations for the same section
            citation_key = (section_title, source_file)
            if citation_key not in seen_sections:
                seen_sections.add(citation_key)

                # Build link URL (this would need to be adjusted based on Docusaurus routing)
                # For now, use a placeholder format
                link_url = self._build_link_url(source_file, section_title)

                citation = Citation(
                    section_title=section_title,
                    source_file=source_file,
                    link_url=link_url,
                )
                citations.append(citation)

        return citations

    def _build_link_url(self, source_file: str, section_title: str) -> str:
        """
        Build a URL to navigate to a specific section in Docusaurus.

        Args:
            source_file: Source file path (e.g., "docs/intro.md")
            section_title: Section heading

        Returns:
            URL string
        """
        # Convert file path to URL path (remove docs/ prefix and .md extension)
        url_path = source_file.replace("docs/", "").replace(".md", "")

        # Convert section title to URL fragment (lowercase, replace spaces with hyphens)
        section_fragment = section_title.lower().replace(" ", "-")
        section_fragment = "".join(c for c in section_fragment if c.isalnum() or c == "-")

        return f"/{url_path}#{section_fragment}"

    async def _generate_with_retry(self, messages: list[dict[str, str]]) -> str:
        """
        Generate chat completion with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            Generated response text

        Raises:
            OpenAIError: If API call fails after all retries
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,  # type: ignore
                    temperature=0.7,
                    max_tokens=1000,
                )

                # Extract answer from response
                answer = response.choices[0].message.content or ""
                return answer

            except RateLimitError as e:
                if attempt < self.max_retries:
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
                self.logger.error(f"Unexpected error during response generation: {e}")
                raise

        raise OpenAIError("Failed to generate response after all retries")
