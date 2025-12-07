# Physical AI & Humanoid Robotics Textbook Constitution

## Executive Summary

This constitution governs the development of the **Physical AI & Humanoid Robotics Textbook** hackathon project. It serves as the supreme source of truth for all architectural, technical, and process decisions. This project implements Hackathon I requirements using Spec-Kit Plus workflow and delivers:

1. **Core Deliverables** (100 points base):
   - Docusaurus-based textbook covering Introduction + 4 modules (ROS 2, Gazebo & Unity, NVIDIA Isaac, VLA)
   - Integrated RAG chatbot with whole-book and selection-based Q&A capabilities
   - Deployed to GitHub Pages or Vercel

2. **Bonus Deliverables** (up to 200 additional points):
   - Claude Code subagents and skills (50 points)
   - Better-Auth signup/signin with user background profiling (50 points)
   - Per-chapter personalization based on user level (50 points)
   - Per-chapter Urdu translation (50 points)

**Assignment Document as Single Source of Truth**: The file `Hackathon I_ Physical AI & Humanoid Robotics Textbook.md` is the canonical requirements document. Any interpretation conflicts defer to this document.

---

## I. Hackathon Alignment & Scope Control

### A. Assignment Fidelity (NON-NEGOTIABLE)
- **Assignment.md is law**: All requirements, constraints, bonus features, and evaluation criteria MUST align exactly with `Hackathon I_ Physical AI & Humanoid Robotics Textbook.md`.
- **No requirement invention**: Do NOT add robotics hardware control, real-time motor drivers, safety-critical systems, or any functionality not explicitly described in the assignment.
- **Content scope**: The textbook teaches concepts, architecture, simulations, and developer experience—not production robot deployment.

### B. Core Requirements (Base 100 Points)
1. **Docusaurus Textbook**:
   - Modern, responsive design with clean UI/UX
   - Structure: Introduction + 4 modules (ROS 2, Gazebo & Unity, NVIDIA Isaac, VLA)
   - Each module must have at minimum 1 complete chapter with meaningful content
   - Deployed and publicly accessible via GitHub Pages or Vercel
   - Repository must be public on GitHub

2. **Integrated RAG Chatbot**:
   - Built using OpenAI Agents/ChatKit SDKs + FastAPI backend
   - Vector storage: Qdrant Cloud (Free Tier)
   - Structured data: Neon Serverless Postgres
   - **Two operational modes**:
     a. Whole-book context: Answer questions about any content in the textbook
     b. Selection-based: Answer questions restricted to user-selected text spans
   - Embedded within the Docusaurus site (no external popups or separate sites)

### C. Bonus Features (Up to 200 Additional Points)
All bonus features are optional but add significant value:

1. **Claude Code Intelligence** (50 points):
   - Create reusable Claude Code subagents for repetitive tasks (e.g., content formatting, spec generation)
   - Develop Claude Code skills for domain-specific operations
   - Document reusable intelligence patterns in project

2. **Better-Auth Integration** (50 points):
   - Implement signup/signin using Better-Auth (https://www.better-auth.com/)
   - Capture user background during signup:
     - Software experience level (beginner, intermediate, advanced)
     - Robotics/AI exposure (none, hobbyist, academic, professional)
     - Available hardware (simulation-only, Jetson kit, robot hardware, full lab)
   - Store profiles in Neon Postgres

3. **Per-Chapter Personalization** (50 points):
   - Add "Personalize Content" button at the start of each chapter
   - Adapt difficulty and depth based on user profile:
     - **Beginner**: Simpler language, more diagrams, fewer assumptions, step-by-step
     - **Intermediate** (default): Balanced technical depth
     - **Advanced**: Deep technical details, links to specs, performance trade-offs
   - Personalization must NOT hide safety-critical information
   - Default content works without login; personalization is enhancement only

4. **Urdu Translation** (50 points):
   - Add "Translate to Urdu" button at the start of each chapter
   - Use AI translation (OpenAI, Google Cloud Translation, or similar)
   - Maintain technical term accuracy (preserve English terms for ROS, Isaac, etc. where appropriate)
   - Preserve markdown structure and code blocks

### D. Out of Scope (Explicit Non-Goals)
- Real-world robot control or motor driver code
- Safety-critical closed-loop control systems
- Hardware procurement or lab setup beyond conceptual teaching
- Production-grade deployment of robots
- Real-time operating systems or low-latency control loops
- Custom robotics hardware design

---

## II. Structure-Before-Content Mandate

### A. Docusaurus Architecture Design First
**Principle**: Always design and review structure before writing extensive content.

**Required Steps**:
1. **Define Docs Tree**:
   - `/docs/intro.md` - Introduction to Physical AI
   - `/docs/module-1-ros2/` - ROS 2 Fundamentals
   - `/docs/module-2-simulation/` - Gazebo & Unity
   - `/docs/module-3-isaac/` - NVIDIA Isaac Platform
   - `/docs/module-4-vla/` - Vision-Language-Action
   - Each module must have at least Chapter 1 with meaningful content

2. **Sidebar Configuration**:
   - Clear navigation hierarchy
   - Logical progression through modules
   - Easy chapter discovery

3. **Homepage Design**:
   - Hero section with course title and brief description
   - Prominent "Start the Course" CTA linking to `/docs/intro`
   - Key features highlight (RAG chatbot, personalization, etc.)
   - Author credit: "Authored by Tayyab Aziz"
   - Footer with GitHub link (https://github.com/Psqasim) and LinkedIn

4. **Blog Removal**:
   - Remove or hide blog from navbar unless explicitly requested
   - Focus navigation on documentation

### B. Module Development Workflow
For each module:
1. **Outline First**: Create overview + chapter structure with headings only
2. **Human Approval**: Present outline to user and get explicit approval
3. **Content Creation**: Only after approval, write full content
4. **Default Difficulty**: Write at intermediate level initially
5. **Adaptation**: Add personalization hooks for beginner/advanced variations

### C. Content Quality Standards
- **Accuracy**: Modern, up-to-date information about ROS 2 (Humble/Iron), Gazebo, Unity, NVIDIA Isaac, VLA
- **Clarity**: Distinguish between "conceptual explanation", "minimal example", and "production pattern"
- **Code Quality**:
  - TypeScript for Docusaurus frontend integrations
  - Python for FastAPI, ROS 2 (rclpy), Isaac stubs
  - All snippets must be syntactically valid or explicitly labeled as pseudo-code
  - Prefer tested, working examples
- **Visual Support**:
  - Diagrams for architecture and workflows
  - Code callouts for important concepts
  - Warning/info boxes for hardware requirements and prerequisites

---

## III. Adaptive Learning & Personalization

### A. User Profiling Requirements
**Data Collection** (via Better-Auth signup):
- Software experience: beginner | intermediate | advanced
- Robotics/AI exposure: none | hobbyist | academic | professional
- Hardware access: simulation-only | jetson-kit | robot-hardware | full-lab
- Learning preferences (optional): visual | hands-on | theory-first

**Storage**: Neon Postgres user profiles table

### B. Personalization Logic
**Principles**:
1. **Explicit, Auditable**: Personalization decisions must be transparent and logged
2. **Safety-First**: NEVER hide critical safety information or warnings
3. **Graceful Degradation**: Content works without login; personalization enhances, not replaces
4. **Per-Chapter Control**: User must explicitly trigger personalization per chapter (not automatic)

**Implementation**:
- **Beginner Mode**:
  - Simpler vocabulary (avoid jargon without definition)
  - More step-by-step instructions
  - Additional diagrams and visual aids
  - Explicit prerequisites and setup guides
  - More code comments

- **Intermediate Mode** (default):
  - Balanced technical depth
  - Assume basic programming knowledge
  - Moderate code examples with explanations

- **Advanced Mode**:
  - Deep technical details
  - Performance optimization discussion
  - Links to official specs and RFCs
  - Architectural trade-offs
  - Advanced debugging and profiling

### C. Personalization API Design
```python
# FastAPI endpoint example structure
POST /api/personalize-chapter
{
  "chapter_id": "module-1-ros2/chapter-1",
  "user_profile": {
    "software_level": "beginner",
    "robotics_exposure": "none",
    "hardware": "simulation-only"
  }
}

Response:
{
  "personalized_content": "...",
  "difficulty_applied": "beginner",
  "modifications": ["simplified-terminology", "added-diagrams", "expanded-setup"]
}
```

---

## IV. RAG Chatbot Architecture

### A. Functional Requirements
1. **Whole-Book Q&A**:
   - User asks question about any textbook content
   - System retrieves relevant chunks from Qdrant
   - OpenAI Agents/ChatKit generates contextual answer

2. **Selection-Based Q&A**:
   - User selects text span in Docusaurus
   - Small, unobtrusive "Ask about this" button appears
   - Question restricted to selected text context only
   - Clear UI indication of context scope

### B. Tech Stack Constraints
- **Backend**: FastAPI (Python)
- **LLM Framework**: OpenAI Agents SDK or ChatKit SDK
- **Vector DB**: Qdrant Cloud (Free Tier)
- **Relational DB**: Neon Serverless Postgres
- **Deployment**: Backend on Vercel/Railway/Render (free tier acceptable)

### C. Data Pipeline
1. **Content Ingestion**:
   - Parse Docusaurus markdown files
   - Chunk content (target: 500-1000 tokens per chunk)
   - Generate embeddings (OpenAI text-embedding-3-small or similar)
   - Store vectors in Qdrant with metadata (module, chapter, section)

2. **Retrieval Strategy**:
   - Semantic search in Qdrant (top-k=5 default)
   - Rerank results if needed
   - Pass to LLM with system prompt

3. **Response Generation**:
   - Use ChatKit or OpenAI Agents to generate response
   - Include source citations (chapter/section references)
   - Handle edge cases (no relevant content found, ambiguous query)

### D. UX Design Principles
- **Embedded Chat Panel**: Slide-out or sidebar panel within Docusaurus (no popups)
- **Context Indicators**: Clear visual feedback on whether query uses whole-book or selection-only context
- **Source Citations**: Link back to relevant chapters/sections
- **Responsive Design**: Works on mobile and desktop
- **Keyboard Navigation**: Accessible via keyboard

### E. API Security
- **Rate Limiting**: Prevent abuse of OpenAI API quota
- **Input Validation**: Sanitize user queries
- **CORS**: Properly configured for Docusaurus frontend
- **Secrets Management**: Environment variables for API keys (NEVER commit to git)

---

## V. Content Quality & Code Standards

### A. Technical Accuracy
- **ROS 2**: Focus on Humble/Iron distributions (latest LTS + current)
- **Gazebo**: Classic (Gazebo 11) or Gazebo Sim (Fortress+) - clarify which
- **Unity**: Unity 2022 LTS or later
- **NVIDIA Isaac**: Isaac Sim (Omniverse) and Isaac ROS (latest stable)
- **VLA Models**: Reference latest research (RT-1, RT-2, OpenVLA, etc.)

### B. Code Example Standards
1. **Language-Specific**:
   - **TypeScript**: Docusaurus plugins, frontend RAG UI, Better-Auth integration
   - **Python**: FastAPI backend, ROS 2 examples (rclpy), Isaac integration stubs

2. **Quality Requirements**:
   - Syntactically valid (run through linter/formatter)
   - Include imports and dependencies
   - Add comments for non-obvious logic
   - Provide context (where this code runs, prerequisites)

3. **Example Types**:
   - **Conceptual**: Simplified to teach principle (label as "conceptual example")
   - **Minimal Working**: Complete, runnable, minimal dependencies
   - **Production Pattern**: Robust error handling, logging, configuration (label as "production pattern")

### C. UI/UX Standards
- **Responsive Design**: Mobile-first, test on common breakpoints
- **Accessibility**: WCAG 2.1 AA compliance (minimum)
  - Readable fonts (16px+ base size)
  - Sufficient color contrast (4.5:1 for body text)
  - Keyboard navigation support
  - Alt text for images
- **Performance**: Lighthouse score 90+ (performance, accessibility, SEO)
- **Consistency**: Use Docusaurus design tokens, maintain visual consistency

### D. Branding & Attribution
- **Author Credit**: "Authored by Tayyab Aziz" on homepage and prominent in book
- **Footer Links**:
  - GitHub: https://github.com/Psqasim
  - LinkedIn: [user to provide]
  - Email: [optional]
- **Hackathon Attribution**: Reference Panaversity and PIAIC/GIAIC if appropriate

---

## VI. Engineering Practices & Workflow

### A. Spec-Driven Development (SDD) Workflow
**Mandatory Process** (Spec-Kit Plus):
1. `/sp.constitution` - Define project principles (this document)
2. `/sp.specify` - Create feature specification
3. `/sp.clarify` - Resolve ambiguities with targeted questions
4. `/sp.plan` - Design architecture and implementation plan
5. `/sp.tasks` - Break down into testable tasks
6. `/sp.implement` - Execute implementation

**Non-Negotiables**:
- NEVER skip spec/plan/tasks for non-trivial features
- Keep spec.md, plan.md, tasks.md as single source of truth
- Update specs BEFORE implementing large changes
- Get human approval on plans before major implementation

### B. Separation of Concerns
**Module Boundaries**:
1. **Textbook Frontend**: Docusaurus site
   - Content rendering
   - Navigation
   - UI components (personalization buttons, translation buttons)
   - Selection-based UI for RAG

2. **RAG Backend**: FastAPI service
   - Content ingestion and embedding
   - Vector search (Qdrant)
   - LLM orchestration (OpenAI Agents/ChatKit)
   - Response generation

3. **Auth & Personalization**: Better-Auth + FastAPI
   - User signup/signin
   - Profile management
   - Personalization logic
   - Translation service integration

**Communication**:
- REST APIs between frontend and backend
- Clear API contracts documented in plan.md
- Error handling at boundaries

### C. Git & Change Management
**Commit Standards**:
- Small, coherent commits
- Meaningful commit messages (Conventional Commits format recommended)
- One logical change per commit

**Branch Strategy**:
- `main` or `master`: production-ready code
- Feature branches: `feature/<feature-name>`
- Hotfix branches: `hotfix/<issue>`

**Pull Request Process**:
- All changes via PR (even solo development for documentation)
- PR description references spec/plan/tasks
- Self-review checklist before requesting review

**No Large Rewrites**:
- Avoid massive refactors without updating spec/plan first
- Incremental improvements preferred over big-bang changes

### D. Testing Strategy
**Minimum Testing Requirements**:
1. **Backend Tests**:
   - Unit tests for core logic (personalization, translation, embedding)
   - Integration tests for API endpoints
   - Health check endpoint (`/health`)
   - Smoke tests for Qdrant and Neon connectivity

2. **Frontend Tests**:
   - Build succeeds without errors
   - Main routes render without crashing
   - RAG UI loads and displays correctly
   - Selection-based UI triggers properly

3. **E2E Tests** (nice-to-have):
   - Full user flow: select text → ask question → get answer
   - Personalization flow: signup → set profile → personalize chapter

**Testing Philosophy**:
- Pragmatic testing (not 100% coverage)
- Focus on critical paths and integration points
- Manual testing acceptable for UI/UX validation
- Document test cases in tasks.md

---

## VII. AI Governance & Development

### A. AI-Assisted Development Principles
1. **Spec-First**: Always update spec/plan before major AI-generated code
2. **Clarity Over Cleverness**: Prefer readable, maintainable code over complex AI abstractions
3. **Human Approval**: Get user approval on plans before large implementations
4. **Iterative Development**: Small increments, frequent check-ins

### B. Prompt History Records (PHR)
**Automatic PHR Creation**:
- Create PHR after every significant user interaction
- Routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- Capture full user prompt verbatim (no truncation)
- Record key assistant outputs
- Include metadata (stage, date, files changed, tests run)

### C. Architecture Decision Records (ADR)
**When to Suggest ADR**:
- Significant architectural decisions (framework choice, data model, API design)
- Multiple viable alternatives with trade-offs
- Cross-cutting concerns (security, performance, deployment)

**Process**:
1. Detect decision significance (impact, alternatives, scope)
2. Suggest: "📋 Architectural decision detected: [brief]. Document reasoning? Run `/sp.adr [title]`"
3. Wait for user consent
4. Never auto-create ADRs

**ADR Storage**: `history/adr/`

### D. Human-as-Tool Strategy
**Invoke User For**:
1. **Ambiguous Requirements**: Ask 2-3 targeted clarifying questions
2. **Unforeseen Dependencies**: Surface and ask for prioritization
3. **Architectural Uncertainty**: Present options with trade-offs
4. **Completion Checkpoints**: Summarize progress and confirm next steps

---

## VIII. Security & Secrets Management

### A. Secrets Handling (NON-NEGOTIABLE)
- **NEVER commit secrets to git**: API keys, tokens, passwords, connection strings
- **Environment Variables**: Use `.env` files (add to `.gitignore`)
- **Documentation**: README must document required environment variables
- **.env.example**: Provide template with dummy values

**Required Secrets**:
- `OPENAI_API_KEY` (for OpenAI Agents/ChatKit)
- `QDRANT_URL` and `QDRANT_API_KEY` (for Qdrant Cloud)
- `DATABASE_URL` (for Neon Postgres)
- `BETTER_AUTH_SECRET` (for Better-Auth)

### B. Frontend Security
- **Input Sanitization**: Sanitize user input in chat queries
- **XSS Prevention**: Use React/Docusaurus built-in protections
- **CORS**: Configure properly for backend API

### C. Backend Security
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Validate all API inputs
- **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
- **Authentication**: Protect personalization/translation endpoints with Better-Auth

---

## IX. Deployment & Operations

### A. Deployment Targets
1. **Frontend**: GitHub Pages or Vercel
   - Static site generation (Docusaurus build)
   - Custom domain (optional)
   - HTTPS enabled

2. **Backend**: Vercel, Railway, Render, or similar
   - FastAPI application
   - Environment variables configured
   - Health check endpoint exposed

### B. Operational Requirements
- **Health Checks**: `/health` endpoint returns 200 OK
- **Logging**: Structured logging (JSON format recommended)
- **Error Handling**: Graceful error messages (no stack traces to users)
- **Monitoring**: Basic uptime monitoring (UptimeRobot, Pingdom, or similar)

### C. Documentation Requirements
**README.md Must Include**:
1. Project description and goals
2. Tech stack overview
3. Setup instructions (local development)
4. Environment variables documentation
5. Deployment instructions
6. Demo video link (90 seconds max)
7. Links to deployed site and backend

---

## X. Constraints & Non-Functional Requirements

### A. Performance Budgets
- **Frontend Load Time**: < 3 seconds (Lighthouse)
- **RAG Response Time**: < 5 seconds (p95)
- **Personalization**: < 3 seconds (p95)
- **Translation**: < 5 seconds (p95)

### B. Cost Constraints
- **Free Tier Usage**: Prioritize free tiers (Qdrant Cloud, Neon, Vercel)
- **OpenAI API**: Monitor usage, implement caching where possible
- **Hosting**: Free or minimal cost (<$10/month)

### C. Browser Compatibility
- Modern browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)
- Mobile responsive: iOS Safari, Chrome Android

### D. Accessibility
- WCAG 2.1 AA compliance (minimum)
- Keyboard navigation support
- Screen reader friendly

---

## XI. Deliverables Checklist

### Core Deliverables (Required)
- [ ] Docusaurus textbook with Introduction + 4 modules
- [ ] At least 1 complete chapter per module with meaningful content
- [ ] Homepage with hero, "Start the Course" CTA, author credit
- [ ] RAG chatbot embedded in site
- [ ] Whole-book Q&A functional
- [ ] Selection-based Q&A functional
- [ ] Deployed to GitHub Pages or Vercel
- [ ] Public GitHub repository
- [ ] README with setup and deployment instructions
- [ ] Demo video (90 seconds max)

### Bonus Deliverables (Optional)
- [ ] Claude Code subagents and skills documented
- [ ] Better-Auth signup/signin implemented
- [ ] User background profiling functional
- [ ] Per-chapter personalization button
- [ ] Personalization adapts content based on user level
- [ ] Per-chapter Urdu translation button
- [ ] Translation preserves markdown and code structure

### Submission Requirements
- [ ] Public GitHub repository link
- [ ] Published book link (GitHub Pages or Vercel)
- [ ] Demo video link (<90 seconds)
- [ ] WhatsApp number (for live presentation invitation)

---

## XII. Governance & Amendments

### A. Constitution Authority
- This constitution supersedes all other development practices
- In case of conflict, constitution takes precedence
- Assignment document (`Hackathon I_ Physical AI & Humanoid Robotics Textbook.md`) supersedes constitution if direct conflict

### B. Amendment Process
1. Identify need for amendment (architectural decision, new requirement)
2. Document rationale in ADR
3. Update constitution
4. Update all dependent specs/plans/tasks
5. Communicate changes to team (if applicable)

### C. Compliance Verification
- All PRs must verify compliance with constitution
- Spec/plan/tasks must reference relevant constitution sections
- Complexity and deviations must be justified

### D. Living Document
- Constitution evolves with project understanding
- Regular reviews during major milestones
- Version-controlled in git

---

## XIII. Success Criteria

### A. Hackathon Evaluation (100 Base Points)
1. **Docusaurus Textbook** (50 points):
   - Structure and navigation
   - Content quality and accuracy
   - Visual design and UX
   - Deployment and accessibility

2. **RAG Chatbot** (50 points):
   - Whole-book Q&A functionality
   - Selection-based Q&A functionality
   - Response quality and accuracy
   - UI/UX integration

### B. Bonus Points (Up to 200 Additional)
- Claude Code intelligence: 50 points
- Better-Auth integration: 50 points
- Per-chapter personalization: 50 points
- Urdu translation: 50 points

### C. Project Success Measures
- All core requirements implemented and functional
- Code is maintainable and well-documented
- Deployment is stable and accessible
- Demo video clearly demonstrates functionality
- Potential for future development and scaling

---

**Version**: 1.0.0
**Ratified**: 2025-12-05
**Last Amended**: 2025-12-05
**Author**: Tayyab Aziz
**Project**: Hackathon I - Physical AI & Humanoid Robotics Textbook
