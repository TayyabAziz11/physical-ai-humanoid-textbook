---
id: 001
title: Create Project Constitution for Physical AI Textbook
stage: constitution
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Tayyab Aziz
command: /sp.constitution
labels: ["constitution", "hackathon", "project-setup", "spec-kit-plus", "physical-ai"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (constitution is a specification document)
---

## Prompt

/sp.constitution

Create a project constitution for the "Physical AI & Humanoid Robotics Textbook" hackathon project.

Context and non‑negotiables:
- This project implements the official "Hackathon I: Physical AI & Humanoid Robotics Textbook" assignment.md.
- Use Spec‑Kit Plus as the primary workflow: /sp.constitution → /sp.specify → /sp.clarify → /sp.plan → /sp.tasks → /sp.implement.
- Tech stack (high‑level):
  - Frontend textbook: Docusaurus (TypeScript) deployed to GitHub Pages (or similar).
  - Backend: FastAPI (Python) using OpenAI Agents / ChatKit SDKs, Qdrant Cloud (Free Tier), and Neon serverless Postgres.
  - Auth & personalization: Better‑Auth for signup/signin and user profile (software + hardware background).
- All requirements and constraints must align with assignment.md; do NOT invent extra robotics/hardware requirements.

Please define principles in the following areas:

1) Hackathon Alignment & Scope
- Always treat assignment.md as the single source of truth.
- Base deliverables:
  - Docusaurus textbook for the "Physical AI & Humanoid Robotics" course (intro + 4 modules).
  - Integrated RAG chatbot that can answer questions about the whole book AND questions based only on user‑selected text.
- Bonus deliverables (if time allows):
  - Claude Code subagents and skills to create reusable intelligence for this project.
  - Better‑Auth signup/signin capturing user software & hardware background.
  - Per‑chapter personalization button that adapts content to the user's level/background.
  - Per‑chapter Urdu translation button.
- No real hardware control is required; the book teaches concepts, simulations, and hardware architecture.

2) Structure‑Before‑Content (Docusaurus)
- Always design and review structure before writing lots of content:
  - Docs tree: intro + 4 modules (ROS 2, Gazebo & Unity, NVIDIA Isaac, VLA) with at least 1 chapter each.
  - Sidebars and routing.
  - Homepage with hero, "Start the Course" CTA to /docs/intro, and key features.
  - Hide/remove blog from navbar unless explicitly requested.
- For each module:
  - First: outline (overview + chapter 1 headings).
  - Then: get human approval.
  - Only then: write content (medium difficulty as baseline, then adapt per user level).

3) Adaptive Learning & Personalization
- During signup with Better‑Auth, collect user background (software experience, robotics/AI exposure, available hardware).
- Based on profile, each chapter can adapt difficulty:
  - Beginner: simpler explanations, more diagrams, fewer assumptions, step‑by‑step.
  - Intermediate (default): medium difficulty.
  - Advanced: deeper technical details, links to specs, performance trade‑offs.
- Constitution should require that:
  - Personalization logic is explicit, auditable, and does NOT silently hide critical safety content.
  - Default content works even without login; personalization is an enhancement, not a dependency.

4) RAG Chatbot & Selection‑Based UX
- RAG backend responsibilities:
  - Answer questions about the entire textbook content.
  - Answer questions restricted to user‑selected text spans (selection‑based Q&A).
- Frontend UI principles:
  - When the user selects text in the docs, a small, unobtrusive "Ask about this" or "Ask the textbook" UI appears.
  - Users can open a chat panel embedded in the book (no janky popups) to interact with the RAG system.
  - Clear indication whether the answer is based on:
    - Whole‑book context, or
    - Only the selected text.
- Data and infra:
  - Use Qdrant Cloud for vector storage of book content.
  - Use Neon Postgres for structured data (users, profiles, personalization config, etc.).
  - Ensure API keys and secrets are never committed to git.

5) Content Quality, Code Examples & UI/UX
- Emphasize:
  - Accurate, modern information about ROS 2, Gazebo, Unity, NVIDIA Isaac, VLA, and related tools.
  - Clear distinctions between "conceptual explanation", "minimal working example", and "production‑ready pattern".
- Code snippets:
  - Prefer TypeScript examples for Docusaurus front‑end integrations.
  - Python examples for FastAPI, ROS 2 (rclpy), NVIDIA Isaac integration stubs, etc.
  - Keep snippets tested or at least syntactically valid; no pseudo‑code unless explicitly labeled as such.
- UI/UX:
  - Clean, modern layout; responsive design.
  - Consistent components for callouts, warnings, hardware requirements, and step‑by‑step labs.
  - Accessibility: readable fonts, good contrast, keyboard navigation basics.
- Branding:
  - Clearly credit the author as "Muhammad Qasim" on the homepage and in the book (e.g., "Authored by Muhammad Qasim").
  - Footer should include GitHub and other relevant links (GitHub: https://github.com/Psqasim, LinkedIn, etc.).

6) Engineering Practices & AI Governance
- Separate concerns:
  - Textbook frontend vs RAG backend vs auth/personalization logic.
  - Each major feature should have its own spec, plan, and tasks where appropriate.
- Git and change management:
  - Small, coherent commits with meaningful messages.
  - Avoid large, unreviewed rewrites without first updating spec/plan/tasks.
- Testing:
  - At minimum:
    - Backend: sanity tests for core FastAPI endpoints (healthcheck, chat, personalization).
    - Frontend: basic checks that main routes build and render, and that RAG UI loads without errors.
- AI usage:
  - Use Spec‑Driven Development: keep spec.md, plan.md, and tasks.md as the single source of truth for implementation decisions.
  - Before generating large amounts of code, ensure the spec and plan are updated to reflect the new scope.
  - Favor clarity and maintainability over overly clever AI‑generated abstractions.

7) Constraints & Out‑of‑Scope
- Do NOT add robotics or hardware requirements beyond what assignment.md clearly describes.
- Real‑world robot control, motor drivers, or safety‑critical closed‑loop systems are out of scope.
- Focus on teaching, simulation, architecture, and developer experience.

Write the constitution as a clear, structured markdown document that future /sp.* steps must respect.

## Response snapshot

Successfully created a comprehensive constitution at `.specify/memory/constitution.md` covering all requested areas:

**Executive Summary:**
- Core deliverables (100 base points): Docusaurus textbook + integrated RAG chatbot
- Bonus deliverables (200 additional points): Claude Code intelligence, Better-Auth, personalization, Urdu translation
- Assignment document as single source of truth

**13 Major Sections:**

I. Hackathon Alignment & Scope Control
- Assignment fidelity (NON-NEGOTIABLE)
- Core requirements (base 100 points)
- Bonus features (up to 200 additional points)
- Explicit out-of-scope items

II. Structure-Before-Content Mandate
- Docusaurus architecture design first
- Module development workflow
- Content quality standards

III. Adaptive Learning & Personalization
- User profiling requirements
- Personalization logic (beginner/intermediate/advanced)
- Personalization API design

IV. RAG Chatbot Architecture
- Functional requirements (whole-book & selection-based Q&A)
- Tech stack constraints (FastAPI, Qdrant, Neon, OpenAI)
- Data pipeline and UX design principles

V. Content Quality & Code Standards
- Technical accuracy (ROS 2, Gazebo, Unity, Isaac, VLA)
- Code example standards (TypeScript, Python)
- UI/UX standards (accessibility, performance, branding)

VI. Engineering Practices & Workflow
- Spec-Driven Development workflow
- Separation of concerns
- Git and change management
- Testing strategy

VII. AI Governance & Development
- AI-assisted development principles
- Prompt History Records (PHR) automatic creation
- Architecture Decision Records (ADR) suggestions
- Human-as-tool strategy

VIII. Security & Secrets Management
- Secrets handling (NON-NEGOTIABLE)
- Frontend and backend security
- Required secrets documented

IX. Deployment & Operations
- Deployment targets (GitHub Pages/Vercel for frontend, Vercel/Railway/Render for backend)
- Operational requirements (health checks, logging, monitoring)
- Documentation requirements

X. Constraints & Non-Functional Requirements
- Performance budgets
- Cost constraints (free tier prioritization)
- Browser compatibility
- Accessibility (WCAG 2.1 AA)

XI. Deliverables Checklist
- Core deliverables (required)
- Bonus deliverables (optional)
- Submission requirements

XII. Governance & Amendments
- Constitution authority
- Amendment process
- Compliance verification

XIII. Success Criteria
- Hackathon evaluation (100 base points breakdown)
- Bonus points (up to 200 additional)
- Project success measures

**Version**: 1.0.0
**Ratified**: 2025-12-05
**Author**: Tayyab Aziz
**Project**: Hackathon I - Physical AI & Humanoid Robotics Textbook

## Outcome

- ✅ Impact: Created comprehensive constitution (600+ lines) covering all hackathon requirements, technical architecture, development workflow, security, deployment, and governance
- 🧪 Tests: None (constitution is a specification document, not code)
- 📁 Files: Created/updated `.specify/memory/constitution.md`
- 🔁 Next prompts: `/sp.specify` to create first feature specification (likely "Docusaurus textbook structure" or "RAG chatbot integration")
- 🧠 Reflection: Constitution successfully captures all requirements from assignment.md and user's detailed context. Emphasizes structure-before-content, spec-driven development, human approval gates, and clear separation between core (100 pts) and bonus (200 pts) deliverables. PHR and ADR processes integrated per Spec-Kit Plus principles.

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution creation was straightforward with clear requirements from user and assignment document.
- Graders run and results (PASS/FAIL): N/A (no automated graders for constitution documents)
- Prompt variant (if applicable): N/A (initial constitution creation)
- Next experiment (smallest change to try): Validate constitution completeness by creating first feature spec and ensuring all referenced sections exist and are actionable. Test human approval workflow by presenting Docusaurus structure outline before content creation.
