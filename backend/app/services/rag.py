"""
RAG (Retrieval-Augmented Generation) pipeline for Study Assistant.
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.core.config import get_settings, Settings
from app.core.logging import get_logger
from app.models.schemas import ChatRequest, ChatResponse, Citation
from app.services.embeddings import embed_text
from app.services.qdrant import search_similar, SearchResult

logger = get_logger(__name__)

settings = get_settings()  # ✅ single, correct settings instance

# -------------------
# System prompt
# -------------------
SYSTEM_PROMPT = """You are a helpful AI tutor for the Physical AI & Humanoid Robotics textbook.

CONTEXT FROM TEXTBOOK:
{context}

INSTRUCTIONS:
1. Answer the user's question using ONLY the information provided in the context above.
2. If the context contains information relevant to the question, use it to provide a detailed answer.
3. If the user question is vague or unclear, explain the main concepts in the provided context.
4. Cite specific sections when possible.
5. If the context does NOT contain enough information to answer, politely say:
   "I don't have enough information about that specific topic in the provided sections."
6. Use clear, educational language appropriate for students learning robotics.
7. Format your answer in clear paragraphs (2-4 paragraphs typically).
"""

# -------------------
# RAG Retrieval
# -------------------
async def retrieve_chunks_whole_book(
    question: str,
    limit: int = 10,
) -> List[SearchResult]:
    logger.info(f"Retrieving chunks (whole-book, limit={limit})")
    query_vector = await embed_text(question)
    return await search_similar(query_vector=query_vector, limit=limit)


async def retrieve_chunks_selection(
    question: str,
    selected_text: str,
    doc_path: str,
    limit: int = 5,
) -> List[SearchResult]:
    logger.info(f"Retrieving chunks (selection, doc={doc_path}, limit={limit})")
    query_vector = await embed_text(selected_text)
    results = await search_similar(
        query_vector=query_vector,
        limit=limit,
        doc_path=doc_path,
    )

    if not results:
        logger.warning("No selection chunks found, falling back to whole-book")
        results = await retrieve_chunks_whole_book(question, limit)

    return results

# -------------------
# Context & Citations
# -------------------
def build_context(chunks: List[SearchResult]) -> str:
    return "\n\n".join(
        f"""
[Source {i}]
Document: {chunk.doc_path}
Section: {chunk.heading}
Content: {chunk.text}
""".strip()
        for i, chunk in enumerate(chunks, 1)
    )


def extract_citations(
    chunks: List[SearchResult],
    max_citations: int = 5,
) -> List[Citation]:
    citations = []
    for chunk in chunks[:max_citations]:
        snippet = chunk.text[:150].rsplit(". ", 1)[0] + "..."
        citations.append(
            Citation(
                doc_path=chunk.doc_path,
                heading=chunk.heading,
                snippet=snippet,
            )
        )
    return citations

# -------------------
# OpenAI Answer Generation
# -------------------
async def generate_answer(
    question: str,
    context: str,
    chat_model: str,
) -> str:
    logger.info(f"Generating answer using model={chat_model}")
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    response = await client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
        max_tokens=800,
    )

    return response.choices[0].message.content

# -------------------
# Main RAG Pipeline
# -------------------
async def answer_chat_request(
    request: ChatRequest,
    db: AsyncSession,
    config: Settings | None = None,
) -> ChatResponse:
    config = config or settings

    logger.info(
        f"Chat request: mode={request.mode}, question_len={len(request.question)}"
    )

    if request.mode == "whole-book":
        chunks = await retrieve_chunks_whole_book(
            request.question,
            config.RAG_TOP_K_CHUNKS,
        )
    elif request.mode == "selection":
        if not request.selected_text or not request.doc_path:
            raise ValueError("selection mode requires selected_text and doc_path")

        chunks = await retrieve_chunks_selection(
            request.question,
            request.selected_text,
            request.doc_path,
            min(config.RAG_TOP_K_CHUNKS, 5),
        )
    else:
        raise ValueError(f"Invalid mode: {request.mode}")

    if not chunks:
        return ChatResponse(
            answer="I couldn't find relevant information to answer your question.",
            citations=[],
            mode=request.mode,
        )

    context = build_context(chunks)

    answer = await generate_answer(
        request.question,
        context,
        config.OPENAI_CHAT_MODEL,
    )

    citations = extract_citations(chunks)

    return ChatResponse(
        answer=answer,
        citations=citations,
        mode=request.mode,
    )
