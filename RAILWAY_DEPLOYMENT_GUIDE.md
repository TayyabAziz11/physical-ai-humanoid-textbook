# Railway Deployment Guide - FastAPI Backend

## 🚀 Production URL
```
https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/
```

---

## ✅ Testing Checklist

### 1. Root Endpoint Test

**GET /** - API Information

```bash
curl https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/
```

**Expected Response (200 OK)**:
```json
{
  "name": "RAG Study Assistant",
  "version": "0.1.0",
  "status": "running",
  "environment": "production",
  "docs_url": "/docs",
  "redoc_url": "/redoc",
  "openapi_url": "/openapi.json",
  "endpoints": {
    "health": "/health",
    "chat": "/chat (POST)"
  }
}
```

---

### 2. Health Check Test

**GET /health** - Simple Health Check

```bash
curl https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/health
```

**Expected Response (200 OK)**:
```json
{
  "status": "healthy",
  "app": "RAG Study Assistant",
  "version": "0.1.0"
}
```

---

### 3. API Documentation Test

**GET /docs** - Swagger UI

```
https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/docs
```

**Expected**: Interactive Swagger UI page with all endpoints documented

---

**GET /openapi.json** - OpenAPI Schema

```bash
curl https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/openapi.json
```

**Expected**: Valid OpenAPI 3.0 JSON schema

---

### 4. Chat Endpoint Test

**POST /chat** - RAG Question Answering

```bash
curl -X POST https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is ROS 2?",
    "mode": "whole-book"
  }'
```

**Expected Response (200 OK)**:
```json
{
  "answer": "ROS 2 (Robot Operating System 2) is...",
  "citations": [
    {
      "text": "...",
      "source": "module-1-ros2/chapter-1.mdx",
      "score": 0.92
    }
  ],
  "mode": "whole-book",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 🧪 Local Testing

### Prerequisites
```bash
cd backend
pip install -r requirements.txt  # or use uv/pip-tools
```

### Environment Setup
Create `.env` file:
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant Vector DB
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=...
QDRANT_COLLECTION=textbook_chunks

# Neon Postgres
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# CORS (optional)
CORS_ORIGINS=["http://localhost:3000"]

# Debug (optional)
DEBUG=true
LOG_LEVEL=DEBUG
```

### Run Locally
```bash
# Method 1: Direct uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Python module
python -m uvicorn main:app --reload

# Method 3: Using main.py directly
python main.py
```

### Test Locally
```bash
# Root endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Docs
open http://localhost:8000/docs

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ROS 2?", "mode": "whole-book"}'
```

---

## 🔧 Railway Configuration

### Environment Variables (Required)

Set these in Railway Dashboard → Variables:

```bash
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=...
QDRANT_COLLECTION=textbook_chunks

# Neon Postgres Database
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Application Config
DEBUG=false
LOG_LEVEL=INFO

# CORS (if frontend is separate)
CORS_ORIGINS=["https://your-frontend.com"]
```

### Start Command

Railway automatically detects uvicorn. If needed, set manually:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Important**: Use `$PORT` (Railway injects this automatically)

---

## 📊 Database Configuration

### Neon Postgres + asyncpg

The app automatically:
1. ✅ Converts `postgresql://` → `postgresql+asyncpg://`
2. ✅ Handles SSL (`sslmode=require`)
3. ✅ Removes incompatible params (`channel_binding`)
4. ✅ Uses connection pooling with `pool_pre_ping=True`

**No manual intervention needed!**

### Qdrant Vector DB

The app automatically:
1. ✅ Creates collection if missing (1536-dim, cosine similarity)
2. ✅ Singleton client (prevents connection leaks)
3. ✅ 30-second timeout for cloud deployments

**Collection is auto-created on first startup.**

---

## 🐛 Troubleshooting

### Issue: 404 on "/"
**Cause**: Railway running wrong `main.py` file
**Fix**: Ensure Railway runs `backend/main.py` (not `backend/app/main.py`)

### Issue: Database SSL Errors
**Cause**: Neon requires SSL, asyncpg needs proper SSL context
**Fix**: Already handled in `app/db/session.py:61` (creates SSL context)

### Issue: Qdrant Connection Timeout
**Cause**: Cloud Qdrant needs longer timeout
**Fix**: Already set to 30s in `app/db/qdrant.py:32`

### Issue: CORS Errors
**Cause**: Frontend origin not in `CORS_ORIGINS`
**Fix**: Add frontend URL to Railway env vars:
```bash
CORS_ORIGINS=["https://your-frontend.com"]
```

### Issue: Import Errors
**Cause**: Wrong Python path or missing dependencies
**Fix**:
```bash
# Rebuild Railway deployment
# Or locally:
pip install -r requirements.txt
```

---

## 📝 Logs Monitoring

### Railway Logs
```
Dashboard → Deployments → View Logs
```

**Look for**:
- ✅ `🚀 Starting RAG Study Assistant v0.1.0`
- ✅ `✅ Qdrant collection initialized`
- ⚠️ `❌ Qdrant initialization failed` (check API key/URL)

---

## 🔐 Security Best Practices

### 1. Environment Variables
- ✅ **NEVER** commit `.env` to git
- ✅ Use Railway's secrets manager
- ✅ Rotate API keys regularly

### 2. CORS Configuration
- ✅ Set specific origins (not `*` in production)
- ✅ Use HTTPS for all origins
- ❌ Avoid `allow_credentials=True` with `*` origin

### 3. Database Security
- ✅ Use SSL connections (Neon requires this)
- ✅ Use strong passwords
- ✅ Enable connection pooling (already configured)

### 4. Rate Limiting
Consider adding:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(...):
    ...
```

---

## 🚢 Deployment Workflow

### 1. Push to Main Branch
```bash
git add .
git commit -m "Update backend"
git push origin main
```

### 2. Railway Auto-Deploys
- Detects changes
- Builds Docker container
- Runs migrations (if configured)
- Starts uvicorn server
- Health check passes
- Routes traffic to new deployment

### 3. Verify Deployment
```bash
# Check root endpoint
curl https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/

# Check health
curl https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/health
```

---

## 📊 Performance Optimization

### Connection Pooling (Already Configured)
```python
# app/db/session.py
engine = create_async_engine(
    CLEAN_DATABASE_URL,
    pool_pre_ping=True,  # ✅ Validates connections
    pool_size=5,         # Default: 5
    max_overflow=10,     # Default: 10
)
```

### Async Operations
- ✅ All DB queries use `async/await`
- ✅ Qdrant client is singleton
- ✅ OpenAI client supports async

### Logging
- ✅ Structured logging with emojis for clarity
- ✅ Request/response tracking
- ✅ Error context with `exc_info=True`

---

## 🎯 Summary

| Component | Status | Notes |
|-----------|---------|-------|
| **Root Endpoint (/)** | ✅ Fixed | Returns API metadata |
| **Health Check (/health)** | ✅ Working | Simple status check |
| **Chat Endpoint (/chat)** | ✅ Working | RAG-powered Q&A |
| **API Docs (/docs)** | ✅ Working | Swagger UI |
| **Database (Neon Postgres)** | ✅ Configured | asyncpg + SSL |
| **Vector DB (Qdrant)** | ✅ Configured | Singleton client |
| **CORS** | ✅ Configured | Supports custom origins |
| **Logging** | ✅ Enhanced | Structured with emojis |

---

## 🆘 Support

If issues persist:
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Test locally first (`uvicorn main:app --reload`)
4. Check Neon Postgres connection string format
5. Verify Qdrant API key and URL

---

**Last Updated**: 2025-12-23
**Railway URL**: https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/
