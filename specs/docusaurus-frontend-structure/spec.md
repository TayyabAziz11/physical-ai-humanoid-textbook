# Feature Specification: Docusaurus Frontend Structure

**Feature Branch**: `feature/docusaurus-frontend-structure`
**Created**: 2025-12-05
**Status**: Draft
**Input**: User description: "Create a feature specification for the Docusaurus FRONTEND STRUCTURE ONLY for the Physical AI & Humanoid Robotics Textbook project. Set up Docusaurus site with overall docs structure, routing, nav, and layout with light placeholder content. No backend wiring yet."

## Executive Summary

This feature establishes the foundational frontend structure for the Physical AI & Humanoid Robotics Textbook using Docusaurus (TypeScript, classic preset). The scope is strictly limited to the frontend presentation layer—implementing the navigable course structure, homepage, UI placeholders for future features (RAG chatbot, personalization, translation), but with NO backend integration. This ensures a clear separation of concerns and allows the textbook structure to be validated by humans before content creation begins.

**Key Principle**: Structure-before-content. This feature creates the skeleton; future features will add the meat (actual course content, backend services, etc.).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Student Discovers Course Structure (Priority: P1)

A prospective student lands on the textbook homepage and wants to understand what the course covers and how to start learning.

**Why this priority**: This is the primary entry point for all users. Without a clear homepage and navigation, students cannot begin their learning journey. This is the foundation upon which all other features depend.

**Independent Test**: Can be fully tested by opening the deployed site, viewing the homepage, clicking "Start the Course", and navigating through the module structure via sidebar. Delivers immediate value by showing the course scope and organization.

**Acceptance Scenarios**:

1. **Given** a student visits the textbook homepage, **When** they view the page, **Then** they see a hero section with title "Physical AI & Humanoid Robotics", a descriptive subtitle about embodied intelligence, and a prominent "Start the Course" button.

2. **Given** a student is on the homepage, **When** they click "Start the Course", **Then** they are taken to `/docs/intro` which provides an introduction to the course.

3. **Given** a student is viewing any docs page, **When** they look at the sidebar, **Then** they see a clear hierarchical structure with 4 labeled modules (ROS 2, Digital Twin, NVIDIA Isaac, VLA), each expandable to show overview + at least chapter 1.

4. **Given** a student is on the homepage, **When** they view the feature cards, **Then** they see highlights for Physical AI concepts, sim-to-real robotics, AI tutor (coming soon), and adaptive learning.

5. **Given** a student views the homepage footer, **When** they scroll down, **Then** they see author credit "Authored by Tayyab Aziz" with a link to GitHub (https://github.com/Psqasim).

---

### User Story 2 - Student Navigates Through Course Modules (Priority: P1)

A student who has started the course wants to navigate between different modules and chapters to explore the content structure.

**Why this priority**: Navigation is critical for a learning experience. Students must be able to easily move between topics to understand the course flow and jump to areas of interest. This is essential for the MVP.

**Independent Test**: Can be tested by starting at `/docs/intro`, clicking through each module in the sidebar, viewing overview pages, and accessing chapter 1 of each module. Delivers value by allowing students to explore the entire course structure.

**Acceptance Scenarios**:

1. **Given** a student is on `/docs/intro`, **When** they click "Module 1 – ROS 2: Robotic Nervous System" in the sidebar, **Then** the sidebar expands to show "Overview" and "Chapter 1: Basics", and they can click to view either page.

2. **Given** a student is viewing any module's overview page, **When** they click on "Chapter 1" in the sidebar, **Then** they are taken to that chapter's page with placeholder content explaining the chapter's purpose.

3. **Given** a student is on any docs page, **When** they use the navbar, **Then** they see "Course" (active when in docs) and a placeholder "Study Assistant" link (for future RAG chatbot).

4. **Given** a student is on any docs page, **When** they check the navbar, **Then** the "Blog" link is NOT visible (hidden by default per constitution).

5. **Given** a student navigates to any module, **When** they view the URL, **Then** they see clean, readable slugs like `/docs/module-1-ros2/overview` or `/docs/module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics`.

---

### User Story 3 - Student Discovers Future Features (Placeholders) (Priority: P2)

A student exploring a chapter wants to see what personalization and study assistance features will be available, even though they're not yet functional.

**Why this priority**: While these features don't work yet, showing their UI placeholders helps students understand the roadmap and validates the UX before backend development. This is important for hackathon demo purposes but not critical for basic navigation.

**Independent Test**: Can be tested by viewing any chapter page and observing the "Personalize for Me" and "View in Urdu" buttons at the top, and the "Ask the Textbook" interface. No backend calls required; buttons show console logs or placeholder messages.

**Acceptance Scenarios**:

1. **Given** a student is viewing any chapter page (e.g., Module 1 Chapter 1), **When** they look at the top of the content area, **Then** they see two prominent buttons: "Personalize for Me" and "View in Urdu".

2. **Given** a student clicks "Personalize for Me", **When** the button is activated, **Then** they see a placeholder message or console log indicating "Personalization backend not connected yet" (no actual content change occurs).

3. **Given** a student clicks "View in Urdu", **When** the button is activated, **Then** they see a placeholder message or console log indicating "Translation backend not connected yet" (no actual translation occurs).

4. **Given** a student is on any docs page, **When** they look at the page layout, **Then** they see an "Ask the Textbook" entry point (e.g., floating button or sidebar widget) that opens a placeholder chat interface.

5. **Given** a student opens the placeholder chat interface, **When** they type a question and submit, **Then** they see a message like "RAG chatbot backend coming soon" (no actual AI response).

---

### User Story 4 - Student Selects Text to Ask Questions (Priority: P2)

A student reading a chapter wants to ask a question about a specific passage, so they select text to trigger a context-specific query option.

**Why this priority**: This validates the unique "selection-based Q&A" UX before backend work. It's a key differentiator for the hackathon and should be demoed early, but the site is still usable without it.

**Independent Test**: Can be tested by selecting text in any chapter, observing the "Ask about this" tooltip/button appearing, and clicking it to see a placeholder response. Delivers UX validation independent of backend.

**Acceptance Scenarios**:

1. **Given** a student is reading a chapter, **When** they select a span of text (e.g., a paragraph about ROS 2 nodes), **Then** a small, unobtrusive "Ask about this" button or tooltip appears near the selection.

2. **Given** the "Ask about this" button is visible, **When** the student clicks it, **Then** a placeholder interface appears (e.g., modal or chat panel) showing the selected text and a message "Selection-based Q&A backend not connected yet".

3. **Given** a student has selected text, **When** they view the UI, **Then** there is a clear visual distinction between "Ask about this selection" and the general "Ask the Textbook" option (e.g., different button colors, labels, or icons).

4. **Given** a student deselects text or clicks elsewhere, **When** the selection is cleared, **Then** the "Ask about this" button disappears or becomes inactive.

5. **Given** a student uses the text selection feature on mobile, **When** they select text, **Then** the "Ask about this" UI is appropriately sized and positioned for touch interfaces (no overlapping or awkward placement).

---

### User Story 5 - Developer Sets Up and Builds the Site Locally (Priority: P1)

A developer (or the project author) clones the repository and wants to run the Docusaurus site locally for development and testing.

**Why this priority**: Without a working local build, no development or content addition can occur. This is foundational for all contributors and essential for hackathon submission (must be deployable).

**Independent Test**: Can be tested by following README instructions to install dependencies, run the dev server, and build for production. Delivers value by enabling development workflow.

**Acceptance Scenarios**:

1. **Given** a developer has cloned the repository, **When** they run `npm install`, **Then** all dependencies install without errors.

2. **Given** dependencies are installed, **When** the developer runs `npm start`, **Then** the Docusaurus dev server starts on `http://localhost:3000` and the homepage loads correctly.

3. **Given** the dev server is running, **When** the developer makes changes to a markdown file (e.g., `/docs/intro.md`), **Then** the site hot-reloads and reflects the changes without requiring a restart.

4. **Given** the developer wants to create a production build, **When** they run `npm run build`, **Then** the build completes successfully and generates a `build/` directory with static assets.

5. **Given** a production build exists, **When** the developer runs `npm run serve`, **Then** they can preview the production build locally at `http://localhost:3000` (or another port) and verify all routes work.

---

### Edge Cases

- **What happens when a student navigates to a non-existent route** (e.g., `/docs/nonexistent-page`)?
  - **Expected**: Docusaurus shows a 404 page with a link back to the homepage or docs index.

- **What happens when a student disables JavaScript in their browser?**
  - **Expected**: The static site still renders (Docusaurus generates static HTML), but interactive features (text selection UI, placeholder chat) won't work. A message or graceful degradation should inform the user.

- **What happens when a student tries to access the site on a very small screen (e.g., 320px wide)?**
  - **Expected**: The site remains usable with responsive design. Sidebar collapses into a hamburger menu, buttons stack vertically, and text is readable.

- **What happens when a developer tries to build the site without TypeScript configured correctly?**
  - **Expected**: Build fails with clear error messages pointing to the TypeScript configuration issue. README should document TypeScript setup.

- **What happens when placeholder buttons ("Personalize for Me", "View in Urdu") are clicked multiple times rapidly?**
  - **Expected**: No adverse effects; the placeholder message/console log appears each time without causing errors or UI glitches.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Site Setup & Configuration

- **FR-001**: System MUST use Docusaurus (v3.x or latest stable) with the classic preset and TypeScript support.
- **FR-002**: System MUST configure site metadata with title "Physical AI & Humanoid Robotics Textbook", tagline about embodied intelligence, and use Docusaurus default favicon or a simple robot/AI icon placeholder.
- **FR-003**: System MUST set author credit as "Authored by Tayyab Aziz" in site configuration and display it on homepage and footer.
- **FR-004**: System MUST configure GitHub repository link (https://github.com/Psqasim) in footer and navbar (if applicable).

#### Docs Structure & Routing

- **FR-005**: System MUST create `/docs/intro.md` as the course introduction page, accessible via homepage CTA.
- **FR-006**: System MUST organize docs into 4 module directories:
  - `module-1-ros2/` (ROS 2: Robotic Nervous System)
  - `module-2-digital-twin-gazebo-unity/` (Digital Twin: Gazebo & Unity)
  - `module-3-nvidia-isaac/` (NVIDIA Isaac: AI-Robot Brain)
  - `module-4-vision-language-action/` (VLA: Vision-Language-Action)
- **FR-007**: Each module directory MUST contain at minimum:
  - `overview.md` (module overview)
  - `chapter-1-*.md` (first chapter with descriptive filename, e.g., `chapter-1-basics.md`)
- **FR-008**: System MUST generate clean, readable URL slugs (e.g., `/docs/module-1-ros2/overview`, `/docs/module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics`).
- **FR-009**: All docs pages MUST contain light placeholder content (1-3 paragraphs) with brief descriptions explaining the purpose of the page, but NOT full textbook content or bulleted topic lists (defer to future features to avoid premature content decisions).

#### Sidebar & Navigation

- **FR-010**: Sidebar MUST display a hierarchical navigation structure with clear labels and smart expansion behavior:
  - "Intro" (linking to `/docs/intro`)
  - "Module 1 – ROS 2: Robotic Nervous System" (collapsible/expandable)
    - Overview
    - Chapter 1: Basics
  - "Module 2 – Digital Twin (Gazebo & Unity)" (collapsible/expandable)
    - Overview
    - Chapter 1: Simulation Basics
  - "Module 3 – NVIDIA Isaac (AI-Robot Brain)" (collapsible/expandable)
    - Overview
    - Chapter 1: Getting Started
  - "Module 4 – Vision-Language-Action (VLA)" (collapsible/expandable)
    - Overview
    - Chapter 1: VLA Intro
  - **Collapse behavior**: Only the module containing the current page should be expanded; all other modules should be collapsed. When user navigates to a different module, that module expands and the previous one collapses automatically.
- **FR-011**: Navbar MUST include:
  - "Course" link (to `/docs/intro`)
  - "Study Assistant" link pointing to `/chat` placeholder page with clear indication it's a placeholder or "Coming Soon"
- **FR-012**: Navbar MUST NOT display a "Blog" link by default (hide or remove blog from navbar configuration).

#### Homepage Design

- **FR-013**: Homepage MUST include a hero section with:
  - Main heading: "Physical AI & Humanoid Robotics"
  - Subtitle/tagline describing embodied intelligence and AI in the physical world (1-2 sentences)
  - Primary CTA button labeled "Start the Course" linking to `/docs/intro`
- **FR-014**: Homepage MUST include a features section with at least 4 feature cards highlighting:
  1. Physical AI & Embodied Intelligence
  2. Sim-to-Real Robotics and Digital Twins
  3. Integrated AI Tutor / RAG Chatbot (with "Coming Soon" indicator if not functional)
  4. Adaptive Learning (Beginner / Intermediate / Advanced)
- **FR-015**: Homepage MUST include an author section with:
  - Text "Authored by Tayyab Aziz"
  - Link to GitHub profile (https://github.com/Psqasim)
  - Optional: LinkedIn link (placeholder if not provided)
- **FR-016**: Homepage footer MUST display standard footer information (copyright, links, author credit if not already in author section).

#### Personalization & Translation Placeholders

- **FR-017**: All module content pages (both overview pages like `module-1-ros2/overview.md` AND chapter pages like `module-1-ros2/chapter-1-basics.md`) MUST display two buttons at the top of the content area:
  - "Personalize for Me" button
  - "View in Urdu" button
  - Note: Buttons should NOT appear on `/docs/intro` page (intro is not part of a module)
- **FR-018**: When "Personalize for Me" button is clicked, system MUST display a placeholder message (e.g., modal, alert, or console log) stating "Personalization backend not connected yet. This feature will adapt content to your skill level (beginner/intermediate/advanced)."
- **FR-019**: When "View in Urdu" button is clicked, system MUST display a placeholder message (e.g., modal, alert, or console log) stating "Translation backend not connected yet. This feature will translate content to Urdu."
- **FR-020**: Buttons MUST be visually distinct, well-styled, and responsive:
  - On screens **≤ 640px** (phones): Buttons MUST stack vertically (one above the other)
  - On screens **> 640px** (tablets, desktop): Buttons MUST display horizontally side-by-side
  - Maintain adequate spacing and touch-friendly tap targets (minimum 44x44px) on all screen sizes

#### RAG Chatbot Placeholder

- **FR-021**: System MUST provide an "Ask the Textbook" entry point visible on all docs pages (e.g., floating action button in bottom-right corner).
- **FR-021a**: System MUST create a dedicated `/chat` page (or `/assistant`) as the Study Assistant placeholder accessible via navbar link with clear messaging that the RAG chatbot is coming soon.
- **FR-022**: When "Ask the Textbook" entry point is activated on docs pages, system MUST open a slide-out panel from the right or left edge of the screen, keeping the user on the current docs page with the chat interface overlaying a partial view.
- **FR-023**: Placeholder chat interface MUST include:
  - Input field for user questions
  - Submit button
  - Placeholder response area showing "RAG chatbot backend not connected yet. Once integrated, this will answer questions about the entire textbook."
- **FR-024**: Placeholder chat slide-out panel MUST be closable (e.g., close button, ESC key, or clicking outside the panel on the dimmed background overlay).

#### Selection-Based Q&A Placeholder

- **FR-025**: When a user selects text within a docs page, system MUST display a small, unobtrusive "Ask about this" button or tooltip near the selection using custom CSS/JS with the native Selection API (no external libraries).
- **FR-026**: When "Ask about this" button is clicked, system MUST open a centered modal overlay (distinct from the slide-out panel used for general chat) showing:
  - The selected text (quoted or highlighted in a distinct section)
  - Input field for user question about the selection
  - Placeholder message: "Selection-based Q&A backend not connected yet. Once integrated, this will answer questions restricted to your selected text."
  - Close button (X icon) in top-right corner
  - Modal should be closable via ESC key or clicking outside the modal
- **FR-027**: System MUST provide clear visual distinction between:
  - General "Ask the Textbook" (whole-book context) → Uses slide-out panel from edge
  - "Ask about this" (selection-based context) → Uses centered modal overlay
  - Additional differentiation: Different button colors, icons, or labels (e.g., "Ask the Textbook" in blue, "Ask about this" in amber/orange).
- **FR-028**: Selection-based UI MUST be responsive and work on both desktop and mobile (touch-friendly).

### Non-Functional Requirements

#### Code Quality

- **NFR-001**: All code MUST use TypeScript where applicable (components, config files that support TS).
- **NFR-002**: Code MUST follow clean code principles: readable variable/function names, modular components, minimal duplication.
- **NFR-003**: All placeholder messages MUST use console.log() for debugging and/or user-visible messages (modal, alert, or toast notification).

#### Dependencies

- **NFR-004**: Project MUST minimize dependencies; avoid adding heavy UI libraries (e.g., large component libraries) unless clearly justified.
- **NFR-005**: Docusaurus classic preset dependencies are acceptable; additional React components should be lightweight and purpose-built.

#### Build & Deployment

- **NFR-006**: Project MUST build successfully with `npm run build` and produce a `build/` directory with static assets.
- **NFR-007**: Built site MUST be deployable to GitHub Pages or Vercel without additional configuration beyond standard Docusaurus deployment docs.
- **NFR-008**: README MUST document setup steps: install dependencies, run dev server, build for production, and deploy.

#### Responsive Design & Accessibility

- **NFR-009**: Site MUST be responsive and usable on desktop, tablet, and mobile (minimum 320px width).
- **NFR-010**: Site MUST follow basic accessibility best practices:
  - Readable font sizes (16px+ base)
  - Sufficient color contrast (WCAG 2.1 AA minimum)
  - Keyboard navigable (tab through links, buttons)
  - Alt text for any images added (even placeholder images)
- **NFR-011**: Sidebar MUST collapse into a hamburger menu on mobile screens.

#### Constitution Compliance

- **NFR-012**: Feature MUST adhere to project constitution:
  - Structure-before-content principle (light placeholder content only)
  - Clear separation of concerns (no backend code in this feature)
  - No secrets or API keys committed (N/A for frontend-only, but enforce .env/.gitignore best practices)
- **NFR-013**: All file and directory names MUST use clear, readable naming conventions (kebab-case for directories, descriptive filenames).

### Key Entities *(include if feature involves data)*

This feature is primarily structural and does not introduce persistent data entities. However, it defines the following **content entities** (markdown files):

- **Intro Page** (`/docs/intro.md`): Single page introducing the course, learning outcomes, and motivation.
- **Module**: A thematic grouping of chapters (e.g., ROS 2, Digital Twin, NVIDIA Isaac, VLA). Represented by a directory containing:
  - **Module Overview** (`overview.md`): Summary of the module's goals, topics, and structure.
  - **Chapters** (`chapter-*.md`): Individual lessons or sections within a module. Each chapter has:
    - Title
    - Placeholder content (purpose, key topics)
    - Personalization and translation button placeholders
- **Homepage**: Landing page with hero, features, and author sections (not a markdown file, but a React component or Docusaurus homepage config).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can successfully run `npm install && npm start` and view the site at `http://localhost:3000` without errors within 2 minutes.
- **SC-002**: Homepage displays all required sections (hero, features, author credit) and "Start the Course" button successfully navigates to `/docs/intro`.
- **SC-003**: All 4 modules (ROS 2, Digital Twin, NVIDIA Isaac, VLA) are visible in the sidebar, each with an overview and chapter 1 accessible via clean URLs.
- **SC-004**: Clicking "Personalize for Me" or "View in Urdu" on any chapter page triggers a placeholder message visible to the user (modal, alert, or console log).
- **SC-005**: "Ask the Textbook" entry point is visible on all docs pages; clicking it opens a placeholder chat interface.
- **SC-006**: Selecting text in a docs page triggers an "Ask about this" button/tooltip; clicking it opens a placeholder selection-based Q&A interface.
- **SC-007**: Blog link is NOT visible in the navbar (hidden by default).
- **SC-008**: Production build (`npm run build`) completes without errors and generates deployable static assets in `build/` directory.
- **SC-009**: Site is responsive on mobile (320px width) and desktop (1920px width) without horizontal scrolling or broken layouts.
- **SC-010**: README documents setup, build, and deployment steps clearly enough for a new contributor to follow.

### User Satisfaction Metrics (Post-Launch)

- **SC-011**: 90% of initial testers can successfully navigate from homepage to a specific module chapter within 1 minute (validates navigation clarity).
- **SC-012**: Testers report that placeholder buttons and chat interface provide clear indications that features are "coming soon" (no confusion about functionality).

---

## Out of Scope (Explicit Non-Goals)

This feature spec explicitly EXCLUDES the following to maintain focus on frontend structure:

1. **Backend Integration**: No FastAPI, Qdrant, Neon, or Better-Auth integration. No API calls. All backend-dependent features are placeholders only.
2. **Full Textbook Content**: Only light placeholder content (1-3 paragraphs per page). Actual course material (detailed ROS 2 tutorials, Isaac Sim guides, etc.) will be separate features.
3. **Functional RAG Chatbot**: Chat interface is a placeholder only. No LLM calls, no embeddings, no vector search.
4. **Functional Personalization**: "Personalize for Me" button is a placeholder. No content adaptation based on user profiles.
5. **Functional Translation**: "View in Urdu" button is a placeholder. No actual Urdu translation.
6. **User Authentication**: No Better-Auth integration, no signup/signin pages (these are future features).
7. **Analytics or Tracking**: No Google Analytics, PostHog, or other analytics integrations (can be added later).
8. **SEO Optimization**: Basic Docusaurus SEO is fine, but no advanced SEO work (meta tags, structured data, etc.) in this feature.
9. **Automated Testing**: No unit tests, E2E tests, or integration tests required for this feature (though encouraged in future). Manual QA is sufficient.

---

## Dependencies & Prerequisites

### Technical Dependencies

- **Node.js**: Version 18.x or 20.x (LTS recommended)
- **Package Manager**: **npm** (primary and required for this project)
- **Docusaurus**: Version 3.x (latest stable)
- **TypeScript**: Version 5.x (as required by Docusaurus)

### External Dependencies

- **None**: This feature is frontend-only and does not depend on external APIs, databases, or services.

### Internal Dependencies

- **Constitution**: Must reference `.specify/memory/constitution.md` for principles (structure-before-content, separation of concerns, branding guidelines).
- **Spec-Kit Plus Workflow**: Must follow `/sp.constitution` → `/sp.specify` (this doc) → `/sp.clarify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`.

---

## Risks & Mitigations

### Risk 1: Docusaurus Version Compatibility

**Description**: Docusaurus v3 may have breaking changes or bugs that affect TypeScript or custom components.

**Likelihood**: Low
**Impact**: Medium (could delay setup)

**Mitigation**:
- Use Docusaurus official docs and starter templates as reference.
- Pin Docusaurus and dependency versions in `package.json` to avoid unexpected upgrades.
- Test build process early in implementation.

### Risk 2: Placeholder UI Confusion

**Description**: Users might confuse placeholder buttons (Personalize, Urdu, Chatbot) for functional features and be frustrated when they don't work.

**Likelihood**: Medium
**Impact**: Low (UX annoyance, but not a blocker)

**Mitigation**:
- Use clear labels: "Coming Soon", "Placeholder", or "Backend Not Connected" in all placeholder messages.
- Consider adding a banner or modal on first site visit explaining that certain features are in development.
- Include visual indicators (e.g., grayed-out buttons, "beta" badges) for non-functional features.

### Risk 3: Responsive Design Complexity

**Description**: Creating a responsive layout for sidebar, buttons, and text selection UI that works well on all screen sizes can be time-consuming.

**Likelihood**: Medium
**Impact**: Low (site still functional, but UX may degrade on some devices)

**Mitigation**:
- Leverage Docusaurus's built-in responsive design for sidebar and navbar.
- Test on common breakpoints (320px, 768px, 1024px, 1920px) early and often.
- Use CSS flexbox/grid and media queries for custom components.
- If time is limited, prioritize desktop and tablet; mobile refinement can be a follow-up task.

### Risk 4: Scope Creep (Adding Content or Backend)

**Description**: Developer or stakeholder may be tempted to add full chapter content or wire up backend features during this implementation.

**Likelihood**: Medium
**Impact**: High (delays feature completion, violates constitution's structure-before-content principle)

**Mitigation**:
- Clearly communicate that this feature is STRUCTURE ONLY.
- Reference constitution section II (Structure-Before-Content Mandate) in planning and review.
- Use placeholder content as specified (1-3 paragraphs) and resist expanding it.
- Schedule separate features for content creation and backend integration.

---

## Clarifications

### Session 2025-12-05

- Q: Package Manager Preference - Should the project standardize on npm, yarn, or pnpm? → A: **npm** (default Node.js package manager, widest adoption, comes pre-installed, reduces onboarding friction)

- Q: Text Selection UI Implementation - Should we use a library or build a custom solution for the "Ask about this" text selection UI? → A: **Custom CSS/JS** (build lightweight custom solution using native Selection API, minimal dependencies, full control over UX)

- Q: Module Content Depth - Should each chapter include a bulleted list of topics it will cover, or just a brief description? → A: **Brief description only** (1-3 paragraphs explaining purpose, avoids premature content decisions, aligns with structure-before-content principle)

- Q: Study Assistant Placeholder Link - Should the "Study Assistant" link in the navbar point to a placeholder page or just be a non-functional button with tooltip? → A: **Placeholder page at /chat** (creates dedicated route for future integration, better UX than tooltip-only, allows demo of chat interface layout)

- Q: Favicon & Branding Assets - Does the user have specific favicon, logo, or color scheme? → A: **Use Docusaurus defaults with robot/AI icon placeholder** (sufficient for MVP, can be customized later without affecting functionality)

- Q: Personalization/Translation Button Placement - Should buttons appear only on chapter pages, or also on overview pages? → A: **All module content** (buttons display on both module overview pages AND chapter pages within the 4 modules, but NOT on `/docs/intro` page)

- Q: "Ask the Textbook" Entry Point Behavior - Should clicking the entry point navigate to /chat, open a modal, or open a slide-out panel? → A: **Slide-out panel** (opens side panel from right/left edge, user stays on current docs page with chat interface overlaying partial view)

- Q: Text Selection "Ask about this" UI Behavior - Should selection-based Q&A use the same slide-out panel, a separate modal, or inline tooltip? → A: **Separate modal** (centered modal overlay on screen, distinct from slide-out panel, provides clear visual distinction between whole-book and selection-based queries)

- Q: Sidebar Module Collapse Behavior - Should all modules be collapsed, expanded, or smart-expanded by default? → A: **Smart expand** (expand only the current module the user is viewing, collapse all others; contextual behavior reduces clutter while maintaining navigation context)

- Q: Mobile Responsive Breakpoint for Button Stacking - At what screen width should personalization/translation buttons stack vertically? → A: **≤ 640px** (stack vertically on phones including larger phones, remain horizontal side-by-side on tablets 641px+ and desktop)

### Outstanding Items Requiring Clarification (Deferred)

- **LinkedIn Link**: The constitution mentions LinkedIn in the footer. This can be left as "optional" placeholder and added later when profile URL is available. Not blocking for implementation.

---

## Next Steps

After this spec is reviewed and approved:

1. **Run `/sp.clarify`** to resolve any ambiguities or questions listed in "Clarifications Needed" section.
2. **Run `/sp.plan`** to create a detailed technical architecture and implementation plan.
3. **Run `/sp.tasks`** to break down the plan into atomic, testable tasks with acceptance criteria.
4. **Run `/sp.implement`** to execute the tasks and build the feature.

---

## Appendix: Proposed Directory Structure

```
physical-ai-humanoid-textbook/
├── docs/
│   ├── intro.md                                      # Course introduction
│   ├── module-1-ros2/
│   │   ├── overview.md                               # Module 1 overview
│   │   └── chapter-1-basics.md                       # Module 1, Chapter 1
│   ├── module-2-digital-twin-gazebo-unity/
│   │   ├── overview.md                               # Module 2 overview
│   │   └── chapter-1-simulation-basics.md            # Module 2, Chapter 1
│   ├── module-3-nvidia-isaac/
│   │   ├── overview.md                               # Module 3 overview
│   │   └── chapter-1-getting-started.md              # Module 3, Chapter 1
│   └── module-4-vision-language-action/
│       ├── overview.md                               # Module 4 overview
│       └── chapter-1-vla-intro.md                    # Module 4, Chapter 1
├── src/
│   ├── components/
│   │   ├── PersonalizeButton.tsx                     # "Personalize for Me" button component
│   │   ├── TranslateButton.tsx                       # "View in Urdu" button component
│   │   ├── AskTextbookButton.tsx                     # "Ask the Textbook" floating button
│   │   ├── PlaceholderChatModal.tsx                  # Placeholder chat interface
│   │   └── TextSelectionPopup.tsx                    # "Ask about this" text selection UI (custom CSS/JS, no library)
│   ├── css/
│   │   └── custom.css                                # Custom styles
│   └── pages/
│       ├── index.tsx                                 # Homepage (hero, features, author)
│       └── chat.tsx                                  # Study Assistant placeholder page (/chat)
├── static/
│   └── img/
│       └── favicon.ico                               # Favicon (placeholder or custom)
├── docusaurus.config.ts                              # Docusaurus configuration (TS)
├── sidebars.ts                                       # Sidebar configuration (TS)
├── package.json                                      # Dependencies and scripts
├── tsconfig.json                                     # TypeScript configuration
└── README.md                                         # Setup and deployment instructions
```

---

## Appendix: Example Placeholder Content

### Example: `/docs/intro.md`

```markdown
---
id: intro
title: Introduction to Physical AI & Humanoid Robotics
sidebar_label: Intro
slug: /intro
---

# Introduction to Physical AI & Humanoid Robotics

Welcome to the **Physical AI & Humanoid Robotics** course. This textbook is designed to teach you how to bridge the gap between digital intelligence and the physical world through embodied AI and humanoid robotics.

## What You'll Learn

In this course, you'll explore:
- **ROS 2**: The middleware powering modern robots
- **Digital Twins**: Simulating robots in Gazebo and Unity
- **NVIDIA Isaac**: Advanced AI perception and training for robots
- **Vision-Language-Action (VLA)**: Combining language models with robotic control

By the end of this course, you'll understand how to design, simulate, and deploy intelligent robots capable of natural human interaction.

---

**Ready to begin?** Navigate to **Module 1: ROS 2** in the sidebar to start your journey.
```

### Example: `/docs/module-1-ros2/overview.md`

```markdown
---
id: module-1-overview
title: Module 1 Overview - ROS 2
sidebar_label: Overview
---

# Module 1: ROS 2 – The Robotic Nervous System

## Overview

ROS 2 (Robot Operating System 2) is the middleware that powers communication between different parts of a robot. Think of it as the nervous system that allows sensors, actuators, and AI brains to talk to each other.

## What You'll Learn in This Module

- ROS 2 architecture and core concepts (nodes, topics, services)
- Building ROS 2 packages with Python (`rclpy`)
- Understanding URDF (Unified Robot Description Format) for humanoids
- Bridging Python AI agents to ROS controllers

---

**Next**: Proceed to [Chapter 1: Basics](./chapter-1-basics.md) to dive into ROS 2 fundamentals.
```

### Example: `/docs/module-1-ros2/chapter-1-basics.md`

```markdown
---
id: chapter-1-basics
title: Chapter 1 - ROS 2 Basics
sidebar_label: Chapter 1: Basics
---

# Chapter 1: ROS 2 Basics

## Introduction

In this chapter, we'll introduce you to the fundamental building blocks of ROS 2: nodes, topics, and services. These are the core communication patterns you'll use to build any robotic system.

**Topics Covered:**
- What is a ROS 2 node?
- Publishing and subscribing to topics
- Calling services for request-response communication

---

*Note: This is placeholder content. Full chapter content will be added in a future feature.*
```

---

**Version**: 1.0.0
**Last Updated**: 2025-12-05
**Author**: Tayyab Aziz
**Reviewers**: [To be assigned]
**Status**: Ready for `/sp.clarify` and `/sp.plan`
