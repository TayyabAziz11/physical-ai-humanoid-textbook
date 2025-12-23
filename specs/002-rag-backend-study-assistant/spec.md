# Feature Specification: RAG Backend & Study Assistant API

**Feature Branch**: `002-rag-backend-study-assistant`
**Created**: 2025-12-07
**Status**: Draft
**Input**: User description: "Create a feature specification for the RAG backend + chat API for the Physical AI & Humanoid Robotics Textbook project. Scope: Backend and API only for the Study Assistant (RAG chatbot) implemented with FastAPI (Python), using OpenAI Agents/ChatKit SDKs, Qdrant Cloud (Free Tier), and Neon serverless Postgres. Integrates with existing Docusaurus frontend components. Auth, personalization, and Urdu translation are OUT OF SCOPE."

## User Scenarios & Testing

### User Story 1 - Ask General Questions About Textbook Content (Priority: P1)

A student studying Physical AI and Humanoid Robotics opens the textbook site and has a question about a concept that might be covered across multiple chapters. They click the floating "Ask the Textbook" button from any page, type their question (e.g., "What is the difference between ROS 2 nodes and topics?"), and receive an AI-generated answer that synthesizes information from the entire textbook with references to relevant chapters.

**Why this priority**: This is the core value proposition of the Study Assistant. Users can get answers to conceptual questions without manually searching through chapters. This delivers immediate value and represents the minimum viable product.

**Independent Test**: Can be fully tested by opening the chat interface, submitting a question, and verifying that the response includes relevant content from multiple textbook chapters with source citations. Delivers value immediately by answering user questions.

**Acceptance Scenarios**:

1. **Given** a student is on the homepage, **When** they click "Ask the Textbook" and enter "What are the main components of a humanoid robot?", **Then** the system returns an answer synthesizing information from relevant chapters with citations
2. **Given** a student asks a question about ROS 2 basics, **When** the answer is generated, **Then** the response includes references to the specific chapter sections (e.g., "Module 1, Chapter 1: ROS 2 Basics")
3. **Given** a student asks a very broad question (e.g., "Tell me everything about physical AI"), **When** processing the query, **Then** the system retrieves the most relevant chunks and provides a focused answer rather than overwhelming the user

---

### User Story 2 - Ask Questions About Selected Text (Priority: P2)

A student is reading a specific section in Chapter 1 of Module 2 about Gazebo simulation. They encounter a complex paragraph about sensor configurations, select the text, click "Ask about this," and ask "Can you explain this with an example?" The system provides a targeted explanation focused on the selected text, using only the surrounding context from that chapter.

**Why this priority**: Selection-based Q&A provides deeper, context-aware explanations for difficult passages. It enhances comprehension but requires the whole-book Q&A to already exist. This is a natural progression after P1.

**Independent Test**: Can be tested by navigating to any chapter, selecting 10+ characters of text, clicking the "Ask about this" tooltip, and verifying that the chat opens in selection mode with the selected text displayed and answers focused on that specific content.

**Acceptance Scenarios**:

1. **Given** a student has selected a paragraph about digital twins, **When** they click "Ask about this" and type "What are practical applications?", **Then** the answer focuses specifically on the selected text and draws from the same chapter/module
2. **Given** a student selects text from Module 3 about NVIDIA Isaac, **When** asking for clarification, **Then** the system restricts retrieval to Module 3 content and neighboring sections rather than the entire textbook
3. **Given** a student selects text but doesn't type a follow-up question, **When** they just click "Ask about this", **Then** the system provides an explanation of the selected passage

---

### User Story 3 - Review Past Conversations (Priority: P3)

A student returns to the textbook site after a few days and wants to review their previous questions and answers about VLA models. They can see a history of their chat sessions (even without formal authentication) and revisit the AI's explanations.

**Why this priority**: Chat history improves learning continuity and reduces redundant questions. However, it's less critical than the core Q&A functionality and can be added after the primary flows work.

**Independent Test**: Can be tested by creating multiple chat sessions, closing the browser, reopening the site, and verifying that previous conversations are persisted and accessible. Delivers value by allowing students to review their learning journey.

**Acceptance Scenarios**:

1. **Given** a student has asked 3 questions in a previous session, **When** they return to the site and open the chat, **Then** they can see their previous session listed with timestamps
2. **Given** a student is viewing their chat history, **When** they click on a past session, **Then** the conversation is loaded with all questions and answers intact
3. **Given** a student has multiple sessions spanning different topics, **When** browsing history, **Then** each session shows a preview of the first question or timestamp for easy identification

---

### User Story 4 - Index New or Updated Textbook Content (Priority: P1)

A content administrator or developer adds a new chapter to the textbook or updates existing content. They run an indexing script that processes the new Markdown files, generates embeddings, and stores them in the vector database. Subsequent user questions immediately reflect the new content.

**Why this priority**: Without the ability to index content, the RAG system has no knowledge base. This is a foundational requirement that must work before any Q&A can happen. It's as critical as P1 for user-facing features.

**Independent Test**: Can be tested by adding a new MDX file to the docs folder, running the indexing script, and then asking a question about the new content. If the answer includes information from the new file, the test passes.

**Acceptance Scenarios**:

1. **Given** a new chapter file `docs/module-5-advanced-topics/chapter-1-intro.mdx` is created, **When** the indexing script is run, **Then** the chapter content is chunked, embedded, and stored in Qdrant with metadata (module_id=5, doc_path, headings)
2. **Given** an existing chapter is updated with new sections, **When** re-indexing is triggered, **Then** old chunks are replaced or versioned, and new chunks are added
3. **Given** the indexing script encounters a malformed MDX file, **When** processing, **Then** the script logs an error for that specific file but continues processing other files

---

### Edge Cases

- What happens when a user asks a question in a language other than English? The system should return a polite message indicating only English is supported for now (Urdu and other languages are out of scope).
- How does the system handle extremely long user questions (e.g., 500+ words)? The system should truncate or summarize the question while preserving intent, or return an error message asking the user to be more concise.
- What if the vector database (Qdrant) returns zero relevant chunks for a query? The system should respond with "I couldn't find relevant information in the textbook for this question. Please try rephrasing or ask about a different topic."
- What happens if a user selects text that spans multiple unrelated sections (e.g., due to a page layout issue)? The system should still process the selection but may provide a less focused answer; this is acceptable degradation.
- How does the system behave when OpenAI API rate limits are hit? The system should return a user-friendly error message like "The assistant is currently busy. Please try again in a moment" and log the rate limit error for monitoring.
- What if a user submits an empty question? The system should return a validation error before making any API calls: "Please enter a question."
- How does the system handle concurrent requests from multiple users? The FastAPI backend should handle concurrent requests asynchronously; session data in Postgres ensures each user's context is isolated.
- What happens when the selected text is exactly 10 characters (the minimum threshold)? The system should accept it as a valid selection and proceed with selection-based Q&A.
- What if the user asks a question completely unrelated to the textbook (e.g., "What's the weather today?")? The system should politely decline and guide the user: "I'm designed to answer questions about Physical AI and Humanoid Robotics from this textbook. Please ask a related question."

## Requirements

### Functional Requirements

#### Core Q&A Functionality

- **FR-001**: System MUST accept user questions via a REST API endpoint and return AI-generated answers based on textbook content
- **FR-002**: System MUST support two distinct query modes: "whole-book" (searches entire textbook) and "selection" (searches only selected text and surrounding context)
- **FR-003**: System MUST include citations in responses, specifying the document path, heading/section, and a short snippet from the source for each piece of information used
- **FR-004**: System MUST retrieve relevant content chunks from a vector database (Qdrant) using semantic similarity search on user queries
- **FR-005**: System MUST generate answers using OpenAI's language models via the Agents or ChatKit SDK

#### Whole-book Q&A Mode

- **FR-006**: When mode is "whole-book", system MUST search across all indexed textbook content without filtering by module or document
- **FR-007**: System MUST return the top N most relevant chunks (configurable, default 5-10) to provide context to the language model
- **FR-008**: System MUST clearly tag responses with `"mode": "whole-book"` in the API response

#### Selection-based Q&A Mode

- **FR-009**: When mode is "selection", system MUST accept `selectedText`, `docPath`, and optional section/heading metadata as input
- **FR-010**: System MUST restrict vector search to chunks from the same document (docPath) and neighboring sections/chunks
- **FR-011**: System MUST include the selected text as additional context in the prompt sent to the language model
- **FR-012**: System MUST clearly tag responses with `"mode": "selection"` in the API response

#### Embedding & Indexing Pipeline

- **FR-013**: System MUST provide a script or CLI command to index all Markdown/MDX files from the `/docs` directory
- **FR-014**: Indexing pipeline MUST strip MDX frontmatter (YAML metadata) while preserving headings, text content, and module structure
- **FR-015**: Indexing pipeline MUST chunk documents by logical sections (e.g., by heading or fixed token length) to optimize retrieval granularity
- **FR-016**: Each chunk MUST be stored in Qdrant with metadata: `doc_path` (file path), `module_id` (1-4 based on directory), `heading` (section title), `chunk_index` (position in document)
- **FR-017**: Indexing pipeline MUST use OpenAI embedding models to generate vector representations of each chunk
- **FR-018**: Indexing script MUST support incremental re-indexing (update changed files without reprocessing the entire corpus)
- **FR-019**: Indexing script MUST log errors for malformed files but continue processing remaining files

#### Chat API Design

- **FR-020**: System MUST expose a `GET /api/health` endpoint that returns API status and version information
- **FR-021**: System MUST expose a `POST /api/chat` endpoint accepting JSON with fields: `mode` ("whole-book" | "selection"), `question` (string), `selectedText` (optional string), `docPath` (optional string), `userId` (optional string)
- **FR-022**: `POST /api/chat` response MUST include: `answer` (string), `citations` (array of {docPath, heading, snippet}), `mode` (echoed from request), `sessionId` (string)
- **FR-023**: System MUST validate required fields (`mode`, `question`) and return a 400 error with clear messages for missing or invalid data
- **FR-024**: System MUST return a 500 error with a user-friendly message for internal failures (e.g., OpenAI API down, Qdrant unreachable)

#### Data Storage (Postgres)

- **FR-025**: System MUST persist chat sessions in Postgres with fields: `id`, `user_id` (nullable), `started_at`, `mode`, `last_message_at`
- **FR-026**: System MUST persist chat messages in Postgres with fields: `id`, `session_id`, `role` (user|assistant), `content`, `created_at`, `selected_text` (nullable), `doc_path` (nullable)
- **FR-027**: System MUST create a new session on the first message from a user (or when no `sessionId` is provided)
- **FR-028**: System MUST link all messages in a conversation to the same `sessionId`
- **FR-029**: System MUST support storing a `userId` (string) even when formal authentication is not implemented (for future integration)

#### Integration with Frontend

- **FR-030**: API MUST support CORS requests from the Docusaurus frontend origin (e.g., GitHub Pages URL or localhost for development)
- **FR-031**: API responses MUST include appropriate HTTP status codes: 200 (success), 400 (bad request), 500 (internal error)
- **FR-032**: API MUST return JSON responses with consistent structure across all endpoints

#### Security & Configuration

- **FR-033**: System MUST load all API keys (OpenAI, Qdrant, Neon Postgres) from environment variables, never hardcoded
- **FR-034**: System MUST reject requests from origins not explicitly allowed in CORS configuration
- **FR-035**: System MUST sanitize user input (questions, selected text) to prevent injection attacks or prompt manipulation

#### Performance & Reliability

- **FR-036**: System MUST respond to chat queries within 10 seconds under normal load (target: < 7 seconds)
- **FR-037**: System MUST handle at least 10 concurrent requests without degradation or errors
- **FR-038**: System MUST log all errors with sufficient detail for debugging (timestamp, request ID, error type, stack trace)
- **FR-039**: System MUST gracefully handle external service failures (OpenAI, Qdrant, Neon) with user-friendly error messages

### Key Entities

- **ChatSession**: Represents a conversation between a user and the Study Assistant. Contains session metadata (start time, mode, user ID if available). Each session groups related messages.

- **ChatMessage**: Represents a single message in a conversation. Attributes include role (user or assistant), content (text), timestamp, and optional metadata (selected text, document path for context).

- **DocumentChunk**: Represents a segment of textbook content stored in the vector database. Attributes include text content, embedding vector, document path, module ID, heading/section, and chunk index. Used for semantic search.

- **User**: Represents a textbook user (student, learner). Currently a placeholder entity with just an ID (string). Will be expanded when authentication is implemented in a future feature.

- **Citation**: Represents a reference to textbook source material used in an answer. Attributes include document path, heading/section, and a short snippet of the original text. Returned in API responses to show provenance.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users receive answers to whole-book questions in under 7 seconds for 90% of queries (measured from API request to response)
- **SC-002**: Selection-based queries return answers in under 5 seconds for 90% of requests (faster due to narrower search scope)
- **SC-003**: At least 80% of user questions return relevant answers with at least one valid citation from the textbook
- **SC-004**: The indexing script successfully processes all existing textbook content (4 modules, multiple chapters) in under 5 minutes on a standard development machine
- **SC-005**: System handles at least 10 concurrent chat requests without errors or timeouts
- **SC-006**: API health check endpoint responds in under 500ms for 99% of requests
- **SC-007**: Chat sessions and messages are persisted correctly in Postgres with 100% data integrity (no lost messages or corrupted sessions)
- **SC-008**: Users can access their previous chat history (from the same browser session) without errors or missing data
- **SC-009**: System returns user-friendly error messages (not technical stack traces) for at least 95% of error scenarios
- **SC-010**: Zero API keys or secrets are exposed in code repositories, logs, or API responses

## Assumptions

1. **Textbook Content Scope**: The initial implementation will index content from Modules 1-4 as currently structured in the Docusaurus site. New modules can be added by re-running the indexing script.

2. **User Identification**: Without formal authentication, user sessions will be tracked via frontend-generated session IDs or browser storage. The `userId` field in the database will be nullable and populated later when auth is implemented.

3. **Embedding Model**: We will use OpenAI's `text-embedding-ada-002` or a newer recommended model for generating embeddings. The choice can be updated in configuration.

4. **Chunk Size**: Documents will be chunked by semantic sections (headings) where possible, with a fallback to fixed token length (e.g., 500-1000 tokens) for long sections.

5. **Language Support**: Only English questions and content are supported. Urdu translation is explicitly out of scope for this feature.

6. **Deployment Environment**: The backend will be deployed to a PaaS provider (e.g., Railway, Fly.io, Render) that supports Python/FastAPI. Specific provider choice is deferred to the planning phase.

7. **Qdrant Free Tier**: Qdrant Cloud Free Tier limits (e.g., 1GB storage, API rate limits) are sufficient for the initial textbook content. If limits are exceeded, we will need to upgrade or optimize.

8. **Neon Free Tier**: Neon Postgres Free Tier limits (e.g., 0.5GB storage, limited compute hours) are sufficient for initial usage. Heavy usage may require tier upgrades.

9. **OpenAI Rate Limits**: Standard OpenAI API rate limits will apply. If exceeded, users will see a "busy" error message. We assume moderate usage that stays within free or low-cost tier limits.

10. **Single-shot Responses**: Initial implementation will return complete answers in one API call. Streaming (token-by-token) responses are a future enhancement.

11. **Citation Format**: Citations will include document path, heading, and a short snippet (50-100 characters). Exact line numbers or character positions are not required.

12. **CORS Origins**: During development, CORS will allow `localhost:3000` (Docusaurus dev server). For production, CORS will allow the deployed GitHub Pages URL or custom domain.

## Out of Scope

The following are explicitly **NOT** included in this feature and will be addressed in separate specifications:

- **User Authentication & Authorization**: No login, signup, or user management. The `userId` field is a placeholder for future integration.
- **Personalization Logic**: No adaptive learning, personalized recommendations, or user preference tracking.
- **Urdu Translation**: No translation of textbook content or Q&A responses into Urdu or other languages.
- **Admin Dashboard**: No UI for monitoring usage, managing content, or viewing analytics.
- **Advanced Analytics**: No dashboards, reports, or detailed usage tracking beyond basic session/message storage.
- **Streaming Responses**: No token-by-token streaming of LLM output. Responses are returned as complete text.
- **Multi-turn Conversation Context**: System will process each question independently. Maintaining conversational context across multiple exchanges is a future enhancement.
- **User Feedback Mechanism**: No thumbs-up/down, ratings, or comment system for answers.
- **Content Moderation**: No filtering or flagging of inappropriate questions or answers.
- **Voice/Audio Queries**: Text-only input and output.
- **Offline Mode**: Backend requires internet connectivity for OpenAI, Qdrant, and Neon services.

## Dependencies

- **Docusaurus Frontend**: This backend depends on the existing frontend components (AskTheTextbookButton, ChatPanelPlaceholder, TextSelectionTooltip) being functional and able to make HTTP requests.
- **OpenAI API Access**: Requires an active OpenAI API key with access to chat completion and embedding models.
- **Qdrant Cloud Account**: Requires a Qdrant Cloud Free Tier account with a cluster provisioned and accessible via API.
- **Neon Postgres Account**: Requires a Neon serverless Postgres database provisioned and accessible via connection string.
- **Textbook Content**: Requires existing Markdown/MDX files in the `docs/` directory to index. Empty or missing content will result in no answers.
- **Python Environment**: Development and deployment environments must support Python 3.10+ and pip for dependency management.

## Constraints

- **Technology Stack**: Backend must use FastAPI (Python). Other frameworks are not acceptable.
- **Vector Database**: Must use Qdrant Cloud (Free Tier). No local or self-hosted vector databases.
- **Relational Database**: Must use Neon serverless Postgres. No other SQL or NoSQL databases.
- **LLM Provider**: Must use OpenAI models via Agents or ChatKit SDK. No other LLM providers (Anthropic, Cohere, etc.) for this feature.
- **Free Tier Limits**: Solution must work within free tier limits of Qdrant, Neon, and OpenAI (or low-cost tiers). Architecture should account for potential quota exhaustion.
- **No Frontend Changes in This Spec**: This specification covers backend only. Frontend integration details are assumptions; actual frontend code changes will be a separate task.
- **No Authentication**: Cannot implement login/logout or user management in this feature. Must support anonymous or pseudo-anonymous usage.
- **Backend Directory Structure**: All backend code must reside in a `backend/` directory at the repository root, separate from the Docusaurus `docs/` and `src/` directories.

## Notes

- **Incremental Indexing**: The indexing script should support both full re-index (process all files) and incremental mode (only process changed files based on timestamps or checksums).
- **Error Handling Philosophy**: User-facing errors should be friendly and actionable (e.g., "I'm having trouble connecting to the knowledge base. Please try again."). Technical errors should be logged server-side for debugging.
- **Future Streaming**: While streaming is out of scope, the API design should not preclude adding streaming responses later (e.g., using Server-Sent Events or WebSockets).
- **Session Persistence**: Sessions are currently browser-based (sessionId stored in frontend). When auth is added, sessions can be linked to authenticated user accounts.
- **Prompt Engineering**: The system prompt sent to OpenAI should instruct the model to act as a helpful study assistant, stay on topic (Physical AI and Humanoid Robotics), and cite sources when possible.
- **Testing Strategy**: API endpoints should be testable via tools like Postman or `curl`. Indexing script should have sample test files to verify chunking and embedding logic.
