# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.db.qdrant import get_qdrant_client
from app.services.rag import RagRetriever, RagChat

# FastAPI instance
app = FastAPI(title="Physical AI Humanoid Textbook Chatbot")

# Initialize Qdrant client
qdrant_client = get_qdrant_client()
retriever = RagRetriever(client=qdrant_client, collection_name="textbook_chunks")
rag_chat = RagChat(retriever=retriever)

# Request model
class QueryRequest(BaseModel):
    query: str

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Chat endpoint
@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        answer = rag_chat.answer(request.query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
