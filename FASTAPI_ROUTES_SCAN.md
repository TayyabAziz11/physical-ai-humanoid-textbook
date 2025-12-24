# FastAPI Backend - Complete HTTP Routes Scan

**Scan Date**: 2025-12-23
**Main Application**: `backend/app/main.py`
**Framework**: FastAPI
**API Version**: v1

---

## ✅ Required Routes Status

| Requirement | Status | Endpoint | Location |
|------------|---------|----------|-----------|
| Root route (GET /) | ✅ FOUND | `GET /` | `backend/app/main.py:73` |
| Health check (GET /health) | ✅ FOUND | `GET /health` | `backend/app/main.py:90` |
| API prefix | ✅ FOUND | `/api/v1` | `backend/app/main.py:70` |
| Swagger docs | ✅ DEFAULT | `/docs` | FastAPI default |

---

## 📋 Complete Route Inventory

### Root Routes (No Prefix)

#### 1. GET /
- **Handler**: `root()` in `backend/app/main.py:73-87`
- **Tags**: `["Root"]`
- **Description**: Root endpoint for health check and API information
- **Response**:
  ```json
  {
    "name": "Physical AI Study Assistant",
    "version": "1.0.0",
    "status": "running",
    "docs_url": "/docs",
    "api_version": "v1"
  }
  ```

#### 2. GET /health
- **Handler**: `health_check()` in `backend/app/main.py:90-102`
- **Tags**: `["Health"]`
- **Description**: Health check endpoint for monitoring and load balancers
- **Response**:
  ```json
  {
    "status": "healthy",
    "app": "Physical AI Study Assistant",
    "version": "1.0.0"
  }
  ```

---

### API v1 Routes (Prefix: `/api/v1`)

#### Health & Monitoring

##### 3. GET /api/v1/health
- **Handler**: `health_check()` in `backend/app/api/v1/health.py:14-72`
- **Tags**: `["health"]`
- **Description**: Detailed health check with DB and Qdrant status
- **Dependencies**: Database session, Qdrant client, Settings
- **Response**:
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "database": "connected",
    "qdrant": "connected (collection: textbook_chunks, points: 1234)",
    "timestamp": "2025-12-23T12:00:00Z"
  }
  ```

---

#### Chat Endpoints

##### 4. POST /api/v1/chat
- **Handler**: `chat()` in `backend/app/api/v1/chat.py:155-268`
- **Tags**: `["chat"]`
- **Description**: Chat with Study Assistant using RAG
- **Request Model**: `ChatRequest`
  - `question` (str): User's question
  - `mode` (str): "whole-book" or "selection"
  - `session_id` (str, optional): Existing session ID
  - `user_id` (str, optional): User identifier
  - `selected_text` (str, optional): Required for selection mode
  - `doc_path` (str, optional): Document path for selection mode
- **Response Model**: `ChatResponse`
  - `answer` (str): Generated answer
  - `citations` (List): Source citations
  - `mode` (str): Chat mode used
  - `session_id` (str): Session ID for continuation
- **Features**:
  - Session management (create/continue)
  - Conversation history (last 10 messages)
  - Input validation and sanitization
  - Dual mode support (whole-book semantic search / selection-based)

---

#### Session Management

##### 5. GET /api/v1/sessions
- **Handler**: `list_sessions()` in `backend/app/api/v1/sessions.py:21-83`
- **Tags**: `["sessions"]`
- **Description**: List all chat sessions
- **Query Parameters**:
  - `user_id` (str, optional): Filter by user
- **Response Model**: `List[SessionListItem]`
  ```json
  [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "mode": "whole-book",
      "started_at": "2025-12-23T10:00:00Z",
      "last_message_at": "2025-12-23T10:30:00Z",
      "first_question_preview": "What is ROS 2 and how does it work?..."
    }
  ]
  ```

##### 6. GET /api/v1/sessions/{session_id}/messages
- **Handler**: `get_session_messages()` in `backend/app/api/v1/sessions.py:93-162`
- **Tags**: `["sessions"]`
- **Description**: Retrieve all messages for a specific session
- **Path Parameters**:
  - `session_id` (UUID): Session identifier
- **Response Model**: `List[MessageItem]`
  ```json
  [
    {
      "role": "user",
      "content": "What is ROS 2?",
      "created_at": "2025-12-23T10:00:00Z",
      "selected_text": null,
      "doc_path": null
    },
    {
      "role": "assistant",
      "content": "ROS 2 is...",
      "created_at": "2025-12-23T10:00:05Z",
      "selected_text": null,
      "doc_path": null
    }
  ]
  ```

##### 7. DELETE /api/v1/sessions/{session_id}
- **Handler**: `delete_session()` in `backend/app/api/v1/sessions.py:165-227`
- **Tags**: `["sessions"]`
- **Description**: Delete a chat session and all its messages (CASCADE)
- **Path Parameters**:
  - `session_id` (UUID): Session to delete
- **Response**:
  ```json
  {
    "message": "Session deleted successfully",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

---

#### Query Endpoints (RAG)

##### 8. POST /api/v1/query/global
- **Handler**: `global_query()` in `backend/app/api/v1/endpoints/query.py:18-87`
- **Tags**: `["Query"]`
- **Description**: Answer question using RAG semantic search across entire book
- **Request Model**: `GlobalQueryRequest`
  - `question` (str): User's question
  - `conversation_history` (List[dict], optional): Previous messages for context
- **Response Model**: `QueryResponse`
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
    "retrieved_chunks": 5,
    "processing_time_ms": 234.56
  }
  ```

##### 9. POST /api/v1/query/selection
- **Handler**: `selection_query()` in `backend/app/api/v1/endpoints/query.py:90-144`
- **Tags**: `["Query"]`
- **Description**: Answer question based on selected text (no retrieval)
- **Request Model**: `SelectionQueryRequest`
  - `question` (str): User's question
  - `selected_text` (str): User-selected text passage
- **Response Model**: `QueryResponse`
  ```json
  {
    "answer": "Based on the selected text...",
    "citations": [],
    "retrieved_chunks": 0,
    "processing_time_ms": 123.45
  }
  ```
- **Note**: Enforces strict context isolation - no vector search, only uses provided text

---

#### Admin Endpoints

##### 10. POST /api/v1/admin/reindex
- **Handler**: `reindex_content()` in `backend/app/api/v1/endpoints/admin.py:47-106`
- **Tags**: `["Admin"]`
- **Description**: Trigger content re-indexing (asynchronous background task)
- **Request Model**: `ReindexRequest`
  - `docs_directory` (str): Path to documentation directory
- **Response Model**: `ReindexResponse`
  ```json
  {
    "status": "started",
    "total_files": 0,
    "total_chunks": 0,
    "duration_seconds": 0.0
  }
  ```
- **HTTP Status**: 202 ACCEPTED
- **Process**: Uses atomic swap strategy (temp collection → alias swap → old collection delete)
- **⚠️ WARNING**: Should be protected with authentication in production

##### 11. GET /api/v1/admin/health
- **Handler**: `admin_health_check()` in `backend/app/api/v1/endpoints/admin.py:109-121`
- **Tags**: `["Admin"]`
- **Description**: Admin-specific health check
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "admin"
  }
  ```

---

## 📚 Documentation Endpoints

### Swagger UI
- **URL**: `/docs`
- **Type**: Interactive API documentation
- **Framework**: FastAPI auto-generated (Swagger/OpenAPI 3.0)

### ReDoc
- **URL**: `/redoc`
- **Type**: Alternative API documentation
- **Framework**: FastAPI auto-generated (ReDoc)

### OpenAPI Schema
- **URL**: `/openapi.json`
- **Type**: OpenAPI 3.0 schema JSON
- **Framework**: FastAPI auto-generated

---

## 🔧 Middleware & Configuration

### CORS Middleware
- **Allow Origins**: Configurable via `settings.CORS_ORIGINS`
- **Allow Credentials**: `True`
- **Allow Methods**: `["*"]`
- **Allow Headers**: `["*"]`
- **Location**: `backend/app/main.py:60-67`

### Lifespan Events
- **Startup**:
  - Initialize Qdrant collection
  - Log application configuration
- **Shutdown**:
  - Clean up resources
- **Handler**: `lifespan()` in `backend/app/main.py:16-48`

---

## 📂 Route Organization

```
backend/
├── main.py                          # Root routes (/, /health)
└── app/
    ├── main.py                      # FastAPI app + lifespan
    └── api/
        ├── chat.py                  # Legacy /api/chat endpoint
        └── v1/
            ├── router.py            # API v1 router aggregator
            ├── chat.py              # POST /api/v1/chat
            ├── health.py            # GET /api/v1/health
            ├── sessions.py          # Session management routes
            └── endpoints/
                ├── query.py         # RAG query routes (global/selection)
                └── admin.py         # Admin routes (reindex/health)
```

---

## ⚠️ Issues Found & Resolved

1. **Merge Conflicts**: Fixed in `backend/app/main.py`, `backend/app/api/v1/router.py`
   - Resolved by keeping HEAD version (more complete implementation)
   - All routes now functional

2. **Duplicate Implementations**: Two main.py files exist:
   - `backend/main.py` - Simple version (2 routes: /health, /chat)
   - `backend/app/main.py` - Full version ✅ (11+ routes, session management, etc.)
   - **Recommendation**: Use `backend/app/main.py` as primary entry point

---

## 🎯 Summary

### Route Count: **11 HTTP endpoints**
- Root routes: 2
- API v1 routes: 9
- Documentation: 3 (auto-generated)

### ✅ All Required Routes Present
- ✅ GET / (root)
- ✅ GET /health (health check)
- ✅ /api/v1 prefix
- ✅ /docs (Swagger documentation)

### ❌ No Missing Routes
All standard endpoints are implemented. No additions needed.

---

## 🚀 How to Start the Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access documentation at: http://localhost:8000/docs
