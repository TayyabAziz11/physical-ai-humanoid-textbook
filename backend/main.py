# backend/app/main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.services.rag import answer_chat_request
from app.models.schemas import ChatRequest, ChatResponse
from app.db.session import get_db  # adjust if your DB dependency is named differently

settings = get_settings()

# FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# -----------------------
# Health check
# -----------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# -----------------------
# Chat endpoint
# -----------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await answer_chat_request(
            request=request,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
