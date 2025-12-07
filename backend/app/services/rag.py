"""
RAG (Retrieval-Augmented Generation) service

Handles semantic search, context assembly, and chat completion for the Study Assistant.
"""
from typing import List, Tuple, Optional
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import Citation

logger = get_logger(__name__)


def generate_query_embedding(question: str, openai_client: OpenAI, model: str) -> List[float]:
    """
    Generate embedding vector for search query

    Args:
        question: User's question
        openai_client: OpenAI client
        model: Embedding model name

    Returns:
        Embedding vector (list of floats)
    """
    response = openai_client.embeddings.create(
        input=question,
        model=model
    )
    return response.data[0].embedding


def semantic_search(
    question: str,
    qdrant_client: QdrantClient,
    openai_client: OpenAI,
    collection_name: str,
    embedding_model: str,
    top_k: int = 7
) -> List[ScoredPoint]:
    """
    Perform semantic search to find relevant textbook chunks

    Args:
        question: User's question
        qdrant_client: Qdrant client
        openai_client: OpenAI client
        collection_name: Qdrant collection name
        embedding_model: OpenAI embedding model name
        top_k: Number of chunks to retrieve

    Returns:
        List of scored points (chunks with relevance scores)
    """
    # Generate query embedding
    logger.info(f"Generating embedding for question: {question[:50]}...")
    query_vector = generate_query_embedding(question, openai_client, embedding_model)

    # Search Qdrant
    logger.info(f"Searching Qdrant collection '{collection_name}' (top_k={top_k})...")
    search_results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )

    logger.info(f"Retrieved {len(search_results)} chunks")
    return search_results


def assemble_context_and_citations(
    search_results: List[ScoredPoint],
    max_context_length: int = 6000
) -> Tuple[str, List[Citation]]:
    """
    Assemble context from retrieved chunks and generate citations

    Args:
        search_results: List of scored points from Qdrant search
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
        doc_title = payload.get("doc_title", "")

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
    logger.info(f"Assembled context: {current_length} chars, {len(citations)} unique citations")

    return context_text, citations


def generate_chat_completion(
    question: str,
    context: str,
    conversation_history: Optional[List[dict]] = None,
    openai_client: OpenAI = None,
    chat_model: str = "gpt-4-turbo-preview"
) -> str:
    """
    Generate chat completion using OpenAI with RAG context

    Args:
        question: User's current question
        context: Retrieved context from vector search
        conversation_history: Previous messages in conversation (optional)
        openai_client: OpenAI client
        chat_model: OpenAI chat model name

    Returns:
        AI-generated answer
    """
    # System prompt
    system_prompt = """You are an expert Study Assistant for the Physical AI & Humanoid Robotics Textbook.

Your role:
- Answer questions accurately using ONLY the provided context from the textbook
- If the context doesn't contain enough information, say so clearly
- Be concise but thorough
- Use technical terms correctly
- Reference source sections when helpful (e.g., "According to the ROS 2 Basics section...")

Guidelines:
- DO NOT make up information not in the context
- DO NOT use knowledge outside the provided textbook context
- If the question is unclear, ask for clarification
- Format code snippets with proper markdown (```language)
- Use bullet points and numbered lists for clarity"""

    # Build messages
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add conversation history if exists
    if conversation_history:
        messages.extend(conversation_history)

    # Add current question with context
    user_message = f"""Context from textbook:

{context}

---

Question: {question}"""

    messages.append({"role": "user", "content": user_message})

    # Generate completion
    logger.info(f"Generating chat completion with model {chat_model}...")
    response = openai_client.chat.completions.create(
        model=chat_model,
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )

    answer = response.choices[0].message.content
    logger.info(f"Generated answer: {len(answer)} chars")

    return answer


def rag_query(
    question: str,
    mode: str = "whole-book",
    selected_text: Optional[str] = None,
    doc_path: Optional[str] = None,
    conversation_history: Optional[List[dict]] = None
) -> Tuple[str, List[Citation]]:
    """
    Execute full RAG pipeline: search → assemble context → generate answer

    Args:
        question: User's question
        mode: "whole-book" or "selection"
        selected_text: Selected text (for selection mode)
        doc_path: Document path (for selection mode)
        conversation_history: Previous messages in conversation

    Returns:
        Tuple of (answer, citations)
    """
    settings = get_settings()

    # Initialize clients
    from app.services.qdrant_client import get_qdrant_client
    qdrant_client = get_qdrant_client()
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    if mode == "whole-book":
        # Semantic search across entire textbook
        search_results = semantic_search(
            question=question,
            qdrant_client=qdrant_client,
            openai_client=openai_client,
            collection_name=settings.QDRANT_COLLECTION,
            embedding_model=settings.OPENAI_EMBEDDING_MODEL,
            top_k=settings.RAG_TOP_K_CHUNKS
        )

        # Assemble context and citations
        context, citations = assemble_context_and_citations(search_results)

    elif mode == "selection":
        # Use selected text directly as context
        logger.info("Using selection mode with provided text")
        context = f"Selected passage from {doc_path}:\n\n{selected_text}"
        citations = [
            Citation(
                doc_path=doc_path or "unknown",
                heading="Selected Text",
                snippet=selected_text[:150] + ("..." if len(selected_text) > 150 else "")
            )
        ]

    else:
        raise ValueError(f"Invalid mode: {mode}")

    # Generate answer
    answer = generate_chat_completion(
        question=question,
        context=context,
        conversation_history=conversation_history,
        openai_client=openai_client,
        chat_model=settings.OPENAI_CHAT_MODEL
    )

    return answer, citations
