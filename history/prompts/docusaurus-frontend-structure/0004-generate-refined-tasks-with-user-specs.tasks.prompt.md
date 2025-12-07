---
id: 0004
title: Generate Refined Tasks With User Specs
stage: tasks
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: docusaurus-frontend-structure
branch: master
user: Tayyab Aziz
command: /sp.tasks
labels: ["tasks", "docusaurus", "frontend", "user-specified", "wsl-safe", "concrete-paths"]
links:
  spec: specs/docusaurus-frontend-structure/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/docusaurus-frontend-structure/tasks.md
tests:
  - None (task breakdown document)
---

## Prompt

/sp.tasks

Generate an actionable task list for the feature "001-docusaurus-frontend" based on specs/001-docusaurus-frontend/plan.md.

**User Requirements**:
- Reference concrete file paths as defined in the plan (package.json, docusaurus.config.ts, sidebars.ts, docs/, src/components/, src/pages/index.tsx, etc.)
- Break work into small, sequential steps that can be run safely in WSL environment
- Explicitly include:
  - Initial Docusaurus project setup at repo root (TypeScript, classic preset)
  - Creation of the docs tree (intro + 4 modules, overview + chapter 1)
  - Sidebar and navbar configuration (hide blog, add Course + RAG Chat placeholder)
  - Homepage implementation (hero, features, author section, footer)
  - Reusable ChapterActionsBar component and integration into MDX chapter pages
  - AskTheTextbookButton, ChatPanelPlaceholder, and TextSelectionTooltip components
  - Text selection detection using window.getSelection() with 10-char minimum
  - Responsive behavior for chat panel and buttons (desktop + mobile basics)
- Mark tasks that could be parallelizable with [P], but keep a clear recommended order
- Output to specs/001-docusaurus-frontend/tasks.md

## Response snapshot

**User-Specified Task List Generated Successfully**

Replaced previous generic task list with **52 concrete, actionable tasks** tailored to user requirements.

**Key Differences from Previous Version**:

1. **Concrete File Paths**: Every task includes exact file paths from plan.md
   - Previous: "Create tsconfig.json"
   - New: "**File**: `tsconfig.json` Replace entire file with: [full config shown]"

2. **WSL-Safe Commands**: All bash commands use escaped paths for WSL
   - Example: `cd /mnt/e/Certified\ Cloud\ Native\ Applied\ Generative\ and\ Agentic\ AI\ Engineer/Q4\ part\ 2/Hackathon/physical-ai-humanoid-textbook`
   - Includes `mkdir -p`, `touch`, proper escaping

3. **Complete Code Blocks**: Full implementation code provided inline for copy-paste
   - ChapterActionsBar: Full 100+ line component with modal logic
   - TextSelectionDetector: Complete implementation with window.getSelection() and 10-char minimum
   - All CSS modules: Complete styles including responsive breakpoints

4. **Step-by-Step Docusaurus Setup**: Detailed initialization at repo root
   - T002: `npx create-docusaurus@latest . classic --typescript`
   - Prompts user for template selection
   - Expected outputs documented

5. **MDX Integration Pattern**: Explicit instructions for all 8 module files
   - Shows exact import statement and component placement
   - Lists all 8 files that need ChapterActionsBar
   - Notes NOT to add to intro.md

6. **Swizzle Instructions**: Concrete Layout swizzling steps
   - T040: `npm run swizzle @docusaurus/theme-classic Layout -- --eject`
   - T041: Exact edits to src/theme/Layout/index.tsx with imports and state

7. **Testing Checkpoints**: After-task validation steps
   - T008: "Stop server with Ctrl+C after verification"
   - T022: "Navigate through all pages, verify clean URLs"
   - T046: "Select 10+ characters → button appears, < 10 → does NOT appear"

**Organization**: 10 phases instead of 9
- Phase 1: Initial Docusaurus Setup (T001-T008)
- Phase 2: Docusaurus Configuration (T009-T014)
- Phase 3: Sidebar Configuration (T015)
- Phase 4: Docs Tree Creation (T016-T022) - 5 parallelizable file creations
- Phase 5: Custom CSS Setup (T023-T025)
- Phase 6: Homepage Implementation (T026-T031)
- Phase 7: ChapterActionsBar Component (T032-T036)
- Phase 8: RAG Chat Placeholder (T037-T042)
- Phase 9: Text Selection Detection (T043-T046)
- Phase 10: Final Testing & Documentation (T047-T052)

**Parallelizable Tasks**: 15 marked with [P]
- T016-T021: All 6 docs file creations can run simultaneously
- T023-T024: CSS files independently created
- T027-T029: Homepage components independently created
- T037-T038: Chat button and panel independently created
- T043-T044: Selection modal and detector independently created

**WSL-Specific Features**:
- Escaped spaces in paths (e.g., `Certified\ Cloud\ Native`)
- Uses `/mnt/e/` for Windows E: drive access
- Bash commands for directory/file creation
- All npm commands verified for WSL compatibility

**Responsive Design Explicitly Covered**:
- T020: 640px breakpoint specified in requirements
- T034: ChapterActionsBar.module.css with mobile stacking
- T037: AskTextbookButton.module.css with mobile size adjustment
- T038: ChatSlideoutPanel.module.css with full-width mobile
- T048: Full responsive test matrix (320px, 375px, 640px, 768px, 1024px, 1920px)

**Text Selection Details**:
- T044: Complete TextSelectionDetector.tsx with window.getSelection()
- 10-character minimum explicitly implemented: `if (text.length >= 10)`
- Position calculation: `rect.bottom + window.scrollY + 5`
- Button disappears on deselection or outside click

**Complete README Template**: T047 provides full README.md structure ready to copy-paste

## Outcome

- ✅ Impact: Generated highly specific, WSL-safe task list with 52 concrete tasks including complete code blocks for all components. Every task has exact file paths, expected outputs, and testing criteria. Eliminates guesswork—user can execute tasks sequentially by copy-pasting code and commands directly into WSL terminal.
- 🧪 Tests: None (task breakdown document defines manual QA in T048-T050)
- 📁 Files: Updated `specs/docusaurus-frontend-structure/tasks.md` with user-specified requirements (52 tasks, 10 phases, complete code listings)
- 🔁 Next prompts: Begin execution starting with Phase 1 (T001-T008: Docusaurus setup). Recommend stopping after T022 to validate docs structure before continuing to UI components.
- 🧠 Reflection: User request for "concrete file paths" and "WSL-safe commands" significantly improved task usability. Including full code blocks (100+ lines for components) makes tasks copy-paste ready, reducing cognitive load. Explicit file path at start of each task (e.g., "**File**: `src/components/learning/ChapterActionsBar.tsx`") provides clear navigation. WSL path escaping (`Certified\ Cloud\ Native`) prevents common errors. 15 parallelizable tasks marked with [P] but recommended sequential order preserved for safety. Task T035 (integrate ChapterActionsBar into 8 files) could be tedious—consider future optimization with script or batch edit tool.

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation proceeded smoothly with user's detailed requirements providing clear constraints.
- Graders run and results (PASS/FAIL): N/A (no automated graders for task breakdown)
- Prompt variant (if applicable): User-specified detailed requirements variant (concrete paths, WSL-safe, complete code blocks inline)
- Next experiment (smallest change to try): During `/sp.implement` execution, monitor if complete code blocks reduce errors vs requiring user to "implement based on plan". Test if T035 (8-file MDX integration) benefits from automation script. Validate WSL path escaping actually prevents errors in user's environment. Consider if Phase 4 (docs file creation) should have template/script to reduce T016-T021 repetition.
