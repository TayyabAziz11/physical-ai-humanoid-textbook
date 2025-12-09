"""
RAG (Retrieval-Augmented Generation) service

Implements the core RAG pipeline: retrieve relevant chunks, assemble context,
and generate answers using OpenAI chat model.
"""
from typing import List, Optional
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.schemas import ChatRequest, ChatResponse, Citation
from app.services.embeddings import embed_text
from app.services.qdrant import search_similar
from app.services.chat_storage import get_conversation_history

logger = get_logger(__name__)


def assemble_context_and_citations(
    search_results: list,
    max_context_length: int = 6000
) -> tuple[str, List[Citation]]:
    """
    Assemble context from retrieved chunks and generate citations

    Args:
        search_results: List of ScoredPoint from Qdrant search
        max_context_length: Maximum context length in characters

    Returns:
        Tuple of (context_text, citations_list)
    """
    context_parts = []
    citations = []
    seen_sources = set()  # Track unique sources for citations
    current_length = 0

    for idx, point in enumerate(search_results, 1):
        payload = point.payload
        chunk_text = payload.get("chunk_text", "")
        doc_path = payload.get("doc_path", "")
        heading = payload.get("heading", "")

        # Add chunk to context
        chunk_part = f"[Source {idx}] {heading}\n{chunk_text}\n"
        chunk_length = len(chunk_part)

        # Stop if we exceed max context length
        if current_length + chunk_length > max_context_length:
            logger.info(f"Context limit reached ({current_length}/{max_context_length} chars)")
            break

        context_parts.append(chunk_part)
        current_length += chunk_length

        # Create citation (deduplicate by doc_path + heading)
        source_key = f"{doc_path}::{heading}"
        if source_key not in seen_sources:
            seen_sources.add(source_key)

            # Create snippet (first 100-150 chars of chunk)
            snippet = chunk_text[:150].strip()
            if len(chunk_text) > 150:
                snippet += "..."

            citation = Citation(
                doc_path=doc_path,
                heading=heading,
                snippet=snippet
            )
            citations.append(citation)

    context_text = "\n".join(context_parts)
    logger.info(f"Assembled context: {current_length} chars, {len(citations)} citations")

    return context_text, citations


async def answer_chat_request(
    request: ChatRequest,
    db: AsyncSession,
    settings: Settings
) -> ChatResponse:
    """
    Main RAG pipeline: retrieve relevant chunks and generate answer

    Args:
        request: Chat request with question, mode, and optional context
        db: Database session (for conversation history)
        settings: Application settings

    Returns:
        ChatResponse with answer and citations

    Raises:
        ValueError: If mode is invalid or required fields missing
    """
    logger.info(f"Processing chat request: mode={request.mode}, question_len={len(request.question)}")

    # Initialize OpenAI client
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Get session for conversation history (if available)
    session = None
    if request.session_id and request.user_id:
        # Import here to avoid circular dependency
        from app.services.chat_storage import get_or_create_session
        session = await get_or_create_session(
            request.session_id,
            request.user_id,
            request.mode,
            db
        )

    # Get conversation history
    conversation_history = await get_conversation_history(session, db, limit=10)

    # === MODE: WHOLE-BOOK ===
    if request.mode == "whole-book":
        logger.info("Processing in whole-book mode")

        # 1. Embed the question
        logger.info("Generating embedding for question...")
        query_vector = await embed_text(request.question)

        # 2. Search Qdrant across whole collection
        logger.info(f"Searching Qdrant (top_k={settings.RAG_TOP_K_CHUNKS})...")
        search_results = search_similar(
            query_vector=query_vector,
            limit=settings.RAG_TOP_K_CHUNKS
        )

        logger.info(f"Retrieved {len(search_results)} chunks")

        # 3. Assemble context and citations
        context, citations = assemble_context_and_citations(search_results)

    # === MODE: SELECTION ===
    elif request.mode == "selection":
        logger.info("Processing in selection mode")

        # Validate required fields
        if not request.selected_text:
            raise ValueError("selected_text is required for selection mode")

        # Option 1: Use selected text directly as context (simpler)
        # This avoids the need to search and is more direct
        context = f"Selected passage from {request.doc_path or 'textbook'}:\n\n{request.selected_text}"

        # Create citation from selection
        citations = [
            Citation(
                doc_path=request.doc_path or "unknown",
                heading="Selected Text",
                snippet=request.selected_text[:150] + ("..." if len(request.selected_text) > 150 else "")
            )
        ]

        logger.info(f"Using selected text as context ({len(request.selected_text)} chars)")

        # Option 2: Search within filtered subset (more sophisticated)
        # Uncomment this block if you want to also search for related chunks
        # if request.doc_path:
        #     query_vector = await embed_text(request.question)
        #     search_results = search_similar(
        #         query_vector=query_vector,
        #         limit=settings.RAG_TOP_K_CHUNKS,
        #         doc_path_filter=request.doc_path
        #     )
        #     additional_context, additional_citations = assemble_context_and_citations(search_results)
        #     context += "\n\n" + additional_context
        #     citations.extend(additional_citations)

    else:
        raise ValueError(f"Invalid mode: {request.mode}")

    # === BUILD PROMPT ===
    system_prompt = """You are an expert Study Assistant for the Physical AI & Humanoid Robotics Textbook.

Your role:
- Answer questions accurately using ONLY the provided context from the textbook
- If the context doesn't contain enough information, clearly say: "This topic is not covered in the provided section" or "I don't have enough information to answer this question based on the textbook content"
- Be concise but thorough
- Use technical terms correctly
- Reference source sections when helpful

Guidelines:
- DO NOT make up information not in the context
- DO NOT use knowledge outside the provided textbook context
- If the question is unclear, ask for clarification
- Format code snippets with proper markdown (```language)
- Use bullet points and numbered lists for clarity"""

    # Build messages for OpenAI
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add conversation history if available
    if conversation_history:
        messages.extend(conversation_history)

    # Add current question with context
    user_message = f"""Context from textbook:

{context}

---

Question: {request.question}"""

    messages.append({"role": "user", "content": user_message})

    # === CALL OPENAI CHAT API ===
    logger.info(f"Generating answer with {settings.OPENAI_CHAT_MODEL}...")

    try:
        response = openai_client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        answer = response.choices[0].message.content
        logger.info(f"Generated answer: {len(answer)} chars")

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise

    # === CONSTRUCT RESPONSE ===
    chat_response = ChatResponse(
        answer=answer,
        citations=citations,
        mode=request.mode,
        session_id=str(session.id) if session else ""
    )

    return chat_response
