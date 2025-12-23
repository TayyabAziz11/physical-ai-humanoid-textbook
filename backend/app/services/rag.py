# backend/app/services/rag.py

from qdrant_client import QdrantClient

class RagRetriever:
    def __init__(self, client: QdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    def retrieve(self, query: str, top_k: int = 5):
        # Basic example using Qdrant search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=self.embed_text(query),
            limit=top_k
        )
        # Return just payloads/text
        return [hit.payload["text"] for hit in search_result]

    def embed_text(self, text: str):
        # Use OpenAI embeddings or a dummy vector for now
        from openai import OpenAI
        client = OpenAI()
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return embedding.data[0].embedding

class RagChat:
    def __init__(self, retriever: RagRetriever):
        self.retriever = retriever

    def answer(self, query: str) -> str:
        chunks = self.retriever.retrieve(query)
        if not chunks:
            return "No relevant information found."
        # For simplicity, just concatenate top chunks
        return "\n\n".join(chunks)
"""
RAG (Retrieval-Augmented Generation) pipeline for Study Assistant.

Implements:
1. Retrieve relevant chunks from Qdrant based on user question
2. Build context from retrieved chunks
3. Generate answer using OpenAI chat model
4. Extract citations from retrieved chunks

Modes:
- whole-book: search entire textbook
- selection: use selected text and nearby chunks
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.core.config import Settings, settings
from app.core.logging import get_logger
from app.models.schemas import ChatRequest, ChatResponse, Citation
from app.services.embeddings import embed_text
from app.services.qdrant import search_similar, SearchResult

logger = get_logger(__name__)

# System prompt template
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
7. Format your answer in clear paragraphs (2-4 paragraphs typically), not bullet points unless specifically asked.
"""

# -------------------
# RAG Retrieval
# -------------------
async def retrieve_chunks_whole_book(
    question: str,
    limit: int = 10,
) -> List[SearchResult]:
    logger.info(f"Retrieving chunks for whole-book mode (limit={limit})")
    query_vector = await embed_text(question)
    results = await search_similar(query_vector=query_vector, limit=limit)
    logger.info(f"Retrieved {len(results)} chunks from Qdrant")
    return results


async def retrieve_chunks_selection(
    question: str,
    selected_text: str,
    doc_path: str,
    limit: int = 5,
) -> List[SearchResult]:
    logger.info(f"Retrieving chunks for selection mode (doc={doc_path}, limit={limit})")
    query_vector = await embed_text(selected_text)
    results = await search_similar(query_vector=query_vector, limit=limit, doc_path=doc_path)

    if not results:
        logger.warning(f"No chunks found in {doc_path}, falling back to whole-book mode")
        results = await retrieve_chunks_whole_book(question, limit=limit)

    logger.info(f"Retrieved {len(results)} chunks (selection mode)")
    return results

# -------------------
# Context & Citations
# -------------------
def build_context(chunks: List[SearchResult]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"""
[Source {i}]
Document: {chunk.doc_path}
Section: {chunk.heading}
Content: {chunk.text}
---""".strip())
    return "\n\n".join(context_parts)


def extract_citations(chunks: List[SearchResult], max_citations: int = 5) -> List[Citation]:
    citations = []
    for chunk in chunks[:max_citations]:
        snippet = chunk.text
        if len(snippet) > 150:
            cutoff = snippet[:150].rfind(". ")
            snippet = snippet[:cutoff+1] if cutoff > 0 else snippet[:150] + "..."
        citations.append(Citation(doc_path=chunk.doc_path, heading=chunk.heading, snippet=snippet))
    return citations

# -------------------
# OpenAI Answer Generation (v2 SDK)
# -------------------
async def generate_answer(question: str, context: str, chat_model: str) -> str:
    logger.info(f"Generating answer with model: {chat_model}")
    try:
        # Use AsyncOpenAI for async operations (OpenAI SDK v2+)
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
        answer = response.choices[0].message.content
        logger.info(f"Generated answer ({len(answer)} chars)")
        return answer
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise

# -------------------
# Main RAG Pipeline
# -------------------
async def answer_chat_request(
    request: ChatRequest,
    db: AsyncSession,
    settings: Settings | None = None,
) -> ChatResponse:
    # Import default settings if not provided
    from app.core.config import settings as default_settings
    config = settings or default_settings
    logger.info(
        f"Processing chat request: mode={request.mode}, question_len={len(request.question)}, "
        f"user_id={getattr(request, 'user_id', 'anonymous')}"
    )

    # Retrieve relevant chunks
    if request.mode == "whole-book":
        chunks = await retrieve_chunks_whole_book(
            question=request.question, limit=config.RAG_TOP_K_CHUNKS
        )
    elif request.mode == "selection":
        if not request.selected_text or not request.doc_path:
            raise ValueError("mode='selection' requires both selected_text and doc_path")
        chunks = await retrieve_chunks_selection(
            question=request.question,
            selected_text=request.selected_text,
            doc_path=request.doc_path,
            limit=min(config.RAG_TOP_K_CHUNKS, 5),
        )
    else:
        raise ValueError(f"Invalid mode: {request.mode}")

    if not chunks:
        logger.warning("No relevant chunks found in Qdrant")
        return ChatResponse(
            answer="I couldn't find relevant information in the textbook to answer your question. Please try rephrasing or asking a different question.",
            citations=[],
            mode=request.mode,
        )

    # Build context
    context = (
        f"USER SELECTED TEXT:\n\n{request.selected_text}\n\nRELEVANT TEXTBOOK SECTIONS:\n\n{build_context(chunks)}"
        if request.mode == "selection" and request.selected_text
        else build_context(chunks)
    )

    # Generate answer
    answer = await generate_answer(
        question=request.question,
        context=context,
        chat_model=config.OPENAI_CHAT_MODEL,
    )

    # Extract citations
    citations = extract_citations(chunks, max_citations=5)

    return ChatResponse(answer=answer, citations=citations, mode=request.mode)
