# Implementation Plan: Docusaurus Frontend Structure

**Feature**: Docusaurus Frontend Structure
**Spec**: [spec.md](./spec.md)
**Created**: 2025-12-05
**Status**: Ready for Implementation
**Scope**: FRONTEND ONLY - No backend integration in this feature

---

## Executive Summary

This plan details the technical implementation of the Docusaurus-based frontend for the Physical AI & Humanoid Robotics Textbook. The implementation uses **Docusaurus v3.x** (latest stable) with TypeScript, npm as package manager, and the classic preset. The project will be structured at the repository root with a clear separation between frontend (root level) and future backend (separate `backend/` directory).

**Key Architectural Decisions** (from clarifications):
- **Package Manager**: npm (widest adoption, pre-installed with Node.js)
- **Text Selection UI**: Custom CSS/JS using native Selection API (no external libraries)
- **Button Placement**: All module content pages (overview + chapters, NOT `/docs/intro`)
- **Chat UI**: Slide-out panel from right edge for whole-book Q&A
- **Selection-based Q&A**: Separate centered modal (distinct from slide-out panel)
- **Sidebar Behavior**: Smart expand (only current module expanded)
- **Responsive Breakpoint**: ≤ 640px for vertical button stacking

---

## 1. Project Layout & Tooling

### 1.1 Directory Structure (Repository Root)

```
physical-ai-humanoid-textbook/
├── .github/                          # GitHub workflows (future: deploy to Pages)
├── .specify/                         # Spec-Kit Plus templates and scripts
├── docs/                             # Markdown/MDX content for textbook
│   ├── intro.md                      # Course introduction
│   ├── module-1-ros2/
│   │   ├── overview.mdx              # Module 1 overview (with buttons)
│   │   └── chapter-1-basics.mdx      # Module 1, Chapter 1 (with buttons)
│   ├── module-2-digital-twin-gazebo-unity/
│   │   ├── overview.mdx
│   │   └── chapter-1-simulation-basics.mdx
│   ├── module-3-nvidia-isaac/
│   │   ├── overview.mdx
│   │   └── chapter-1-getting-started.mdx
│   └── module-4-vision-language-action/
│       ├── overview.mdx
│       └── chapter-1-vla-intro.mdx
├── src/                              # Custom React/TS components and theme
│   ├── components/
│   │   ├── learning/
│   │   │   ├── ChapterActionsBar.tsx          # "Personalize" + "Urdu" buttons
│   │   │   ├── AskTextbookButton.tsx          # Floating "Ask the Textbook" button
│   │   │   ├── ChatSlideoutPanel.tsx          # Whole-book chat panel (slide-out)
│   │   │   ├── SelectionModal.tsx             # Selection-based Q&A modal
│   │   │   └── TextSelectionDetector.tsx      # Custom text selection hook/component
│   │   └── homepage/
│   │       ├── Hero.tsx                       # Homepage hero section
│   │       ├── Features.tsx                   # Feature cards
│   │       └── AuthorSection.tsx              # Author credit section
│   ├── css/
│   │   ├── custom.css                         # Global custom styles
│   │   └── responsive.css                     # Responsive breakpoints (640px, etc.)
│   ├── pages/
│   │   ├── index.tsx                          # Homepage (replaces default)
│   │   └── chat.tsx                           # /chat placeholder page
│   └── theme/                                 # Docusaurus theme customizations (if needed)
│       └── Layout/
│           └── index.tsx                      # Custom layout wrapper (for text selection)
├── static/
│   ├── img/
│   │   ├── favicon.ico                        # Docusaurus default or robot icon
│   │   └── logo.svg                           # Site logo (optional)
│   └── .nojekyll                              # For GitHub Pages
├── docusaurus.config.ts                       # Main Docusaurus configuration
├── sidebars.ts                                # Sidebar structure configuration
├── tsconfig.json                              # TypeScript configuration
├── package.json                               # npm dependencies and scripts
├── package-lock.json                          # npm lock file
├── .gitignore                                 # Ignore node_modules, build/, .env
├── README.md                                  # Setup and deployment instructions
└── backend/                                   # (Future) FastAPI backend (not in this feature)
```

### 1.2 TypeScript Configuration

**File**: `tsconfig.json`

```json
{
  "extends": "@docusaurus/tsconfig",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@site/*": ["./*"],
      "@components/*": ["src/components/*"]
    },
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react"
  },
  "include": ["src/**/*", "docusaurus.config.ts", "sidebars.ts"]
}
```

**Strictness Level**: `strict: true` for type safety, but use `skipLibCheck: true` to avoid issues with external packages.

**Type Definitions**:
- Use Docusaurus-provided types: `@docusaurus/types`, `@docusaurus/theme-common`
- Create custom types in `src/types/` for component props (if needed)
- Leverage TypeScript's inference where possible to reduce verbosity

### 1.3 Node.js Version Requirement

**Recommended**: Node.js **18.x or 20.x LTS**

**Enforcement**:
- Add `"engines"` field to `package.json`:
  ```json
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
  ```
- Document in README: "This project requires Node.js 18.x or later."

### 1.4 npm Scripts

**File**: `package.json` scripts section

```json
"scripts": {
  "start": "docusaurus start",
  "build": "docusaurus build",
  "serve": "docusaurus serve",
  "clear": "docusaurus clear",
  "deploy": "docusaurus deploy",
  "swizzle": "docusaurus swizzle",
  "write-translations": "docusaurus write-translations",
  "write-heading-ids": "docusaurus write-heading-ids"
}
```

**Usage**:
- `npm start`: Development server (http://localhost:3000)
- `npm run build`: Production build to `build/` directory
- `npm run serve`: Serve production build locally
- `npm run deploy`: Deploy to GitHub Pages (configured via `docusaurus.config.ts`)

---

## 2. Docusaurus Configuration

### 2.1 Main Configuration File

**File**: `docusaurus.config.ts`

```typescript
import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Bridging the gap between digital intelligence and the physical world through embodied AI',
  favicon: 'img/favicon.ico',

  // GitHub Pages deployment config
  url: 'https://<USERNAME>.github.io',  // Replace with actual GitHub username
  baseUrl: '/physical-ai-humanoid-textbook/',  // Replace with repo name
  organizationName: '<USERNAME>',  // GitHub org/user name
  projectName: 'physical-ai-humanoid-textbook',  // Repo name
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Optional: edit URL for "Edit this page" links
          // editUrl: 'https://github.com/<USERNAME>/physical-ai-humanoid-textbook/tree/main/',
        },
        blog: false,  // Hide blog entirely (per FR-012)
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',  // Optional: replace with robot icon
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Course',
        },
        {
          to: '/chat',
          label: 'Study Assistant',
          position: 'left',
        },
        {
          href: 'https://github.com/Psqasim',  // Author's GitHub
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            {
              label: 'Course Introduction',
              to: '/docs/intro',
            },
            {
              label: 'Study Assistant',
              to: '/chat',
            },
          ],
        },
        {
          title: 'Connect',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Psqasim',
            },
            // LinkedIn (optional, deferred per clarifications)
            // {
            //   label: 'LinkedIn',
            //   href: 'https://linkedin.com/in/<profile>',
            // },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Authored by Tayyab Aziz.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml'],
    },
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
```

**Key Configuration Points**:
- **Blog**: Set to `false` (FR-012)
- **Navbar**: "Course" (docs sidebar) + "Study Assistant" (/chat) + GitHub link
- **Footer**: Author credit "Authored by Tayyab Aziz", GitHub link, copyright
- **URL/BaseUrl**: Configured for GitHub Pages deployment (update with actual username/repo)
- **Dark Mode**: Respects system preference, allows user toggle

### 2.2 Sidebar Configuration

**File**: `sidebars.ts`

```typescript
import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Module 1 – ROS 2: Robotic Nervous System',
      collapsed: true,  // Smart expand: collapse by default, expand when user navigates here
      items: [
        'module-1-ros2/overview',
        'module-1-ros2/chapter-1-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 2 – Digital Twin (Gazebo & Unity)',
      collapsed: true,
      items: [
        'module-2-digital-twin-gazebo-unity/overview',
        'module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics',
      ],
    },
    {
      type: 'category',
      label: 'Module 3 – NVIDIA Isaac (AI-Robot Brain)',
      collapsed: true,
      items: [
        'module-3-nvidia-isaac/overview',
        'module-3-nvidia-isaac/chapter-1-getting-started',
      ],
    },
    {
      type: 'category',
      label: 'Module 4 – Vision-Language-Action (VLA)',
      collapsed: true,
      items: [
        'module-4-vision-language-action/overview',
        'module-4-vision-language-action/chapter-1-vla-intro',
      ],
    },
  ],
};

export default sidebars;
```

**Smart Expansion Behavior**:
- Set `collapsed: true` on all categories by default
- Docusaurus automatically expands the category containing the current page
- This implements the "smart expand" requirement from clarifications (Q4)

---

## 3. Docs & MDX Strategy

### 3.1 File Format Decision

**Use MDX (`.mdx`) for module content pages** (overview + chapters) to enable React component imports.

**Use Markdown (`.md`) for simple pages** like `/docs/intro.md` that don't need interactive components.

**Rationale**:
- MDX allows importing `<ChapterActionsBar />` directly into module pages
- Keeps intro page simple and fast (no extra React overhead)

### 3.2 Docs File Structure

```
docs/
├── intro.md                                    # Plain markdown (no components needed)
├── module-1-ros2/
│   ├── overview.mdx                            # MDX (imports ChapterActionsBar)
│   └── chapter-1-basics.mdx                    # MDX (imports ChapterActionsBar)
├── module-2-digital-twin-gazebo-unity/
│   ├── overview.mdx
│   └── chapter-1-simulation-basics.mdx
├── module-3-nvidia-isaac/
│   ├── overview.mdx
│   └── chapter-1-getting-started.mdx
└── module-4-vision-language-action/
    ├── overview.mdx
    └── chapter-1-vla-intro.mdx
```

### 3.3 Content Strategy (Placeholder Content)

**Principle**: Structure-before-content (Constitution Section II)

**Content Guidelines**:
1. **Intro Page** (`docs/intro.md`):
   - 2-3 paragraphs introducing Physical AI & Humanoid Robotics
   - Brief course overview (4 modules)
   - Learning outcomes
   - CTA: "Navigate to Module 1: ROS 2 in the sidebar to start"

2. **Module Overview Pages** (e.g., `module-1-ros2/overview.mdx`):
   - 1-2 paragraphs describing the module's focus
   - What students will learn (brief bullet list)
   - Link to Chapter 1: "Proceed to [Chapter 1: Basics](./chapter-1-basics) to dive deeper"

3. **Chapter Pages** (e.g., `module-1-ros2/chapter-1-basics.mdx`):
   - 1-3 paragraphs explaining the chapter's purpose
   - Topics covered (brief list, NOT detailed bullet points per clarification Q3)
   - Placeholder note: "This is placeholder content. Full chapter content will be added in a future feature."

**Example**: `docs/module-1-ros2/chapter-1-basics.mdx`

```mdx
---
id: chapter-1-basics
title: Chapter 1 - ROS 2 Basics
sidebar_label: Chapter 1: Basics
---

import ChapterActionsBar from '@site/src/components/learning/ChapterActionsBar';

<ChapterActionsBar />

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

### 3.4 MDX Frontmatter Requirements

Every MDX/MD file MUST include frontmatter:

```yaml
---
id: unique-id              # Unique ID for routing (kebab-case)
title: Full Page Title     # Displayed at top of page
sidebar_label: Short Label # Displayed in sidebar (can be shorter)
---
```

---

## 4. Reusable UI Components

### 4.1 Component Architecture

All custom components will be TypeScript React components in `src/components/`.

**Design Principles**:
- **Modular**: Each component has a single responsibility
- **Typed**: Full TypeScript prop interfaces
- **Placeholder Logic**: All buttons/interactions log to console or show alerts (no backend calls)
- **Responsive**: Mobile-first CSS with breakpoints

### 4.2 ChapterActionsBar Component

**File**: `src/components/learning/ChapterActionsBar.tsx`

**Purpose**: Renders "Personalize for Me" and "View in Urdu" buttons at the top of module content pages.

**Requirements** (from spec):
- Display on all module content pages (overview + chapters), NOT on `/docs/intro` (FR-017)
- Stack vertically on screens ≤ 640px, horizontal on > 640px (FR-020)
- Touch-friendly: minimum 44x44px tap targets
- Placeholder behavior: Show alert/modal or console.log when clicked (FR-018, FR-019)

**Implementation Sketch**:

```typescript
import React, { useState } from 'react';
import styles from './ChapterActionsBar.module.css';

export default function ChapterActionsBar(): JSX.Element {
  const [showPersonalizeModal, setShowPersonalizeModal] = useState(false);
  const [showUrduModal, setShowUrduModal] = useState(false);

  const handlePersonalize = () => {
    console.log('[Personalize] Button clicked - backend not connected');
    setShowPersonalizeModal(true);
  };

  const handleUrdu = () => {
    console.log('[Urdu Translation] Button clicked - backend not connected');
    setShowUrduModal(true);
  };

  return (
    <div className={styles.chapterActionsBar}>
      <button
        className={`${styles.actionButton} ${styles.personalizeButton}`}
        onClick={handlePersonalize}
        aria-label="Personalize content for your skill level"
      >
        Personalize for Me
      </button>
      <button
        className={`${styles.actionButton} ${styles.urduButton}`}
        onClick={handleUrdu}
        aria-label="Translate content to Urdu"
      >
        View in Urdu
      </button>

      {/* Placeholder modals */}
      {showPersonalizeModal && (
        <div className={styles.modal} onClick={() => setShowPersonalizeModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3>Personalization Coming Soon</h3>
            <p>Personalization backend not connected yet. This feature will adapt content to your skill level (beginner/intermediate/advanced).</p>
            <button onClick={() => setShowPersonalizeModal(false)}>Close</button>
          </div>
        </div>
      )}

      {showUrduModal && (
        <div className={styles.modal} onClick={() => setShowUrduModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h3>Translation Coming Soon</h3>
            <p>Translation backend not connected yet. This feature will translate content to Urdu.</p>
            <button onClick={() => setShowUrduModal(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
```

**CSS**: `src/components/learning/ChapterActionsBar.module.css`

```css
.chapterActionsBar {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.actionButton {
  min-width: 44px;
  min-height: 44px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.actionButton:hover {
  transform: translateY(-2px);
}

.personalizeButton {
  background-color: #0066cc;
  color: white;
}

.urduButton {
  background-color: #ff9500;
  color: white;
}

/* Mobile: stack vertically */
@media (max-width: 640px) {
  .chapterActionsBar {
    flex-direction: column;
  }
  .actionButton {
    width: 100%;
  }
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modalContent {
  background-color: white;
  padding: 2rem;
  border-radius: 0.5rem;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### 4.3 AskTextbookButton Component

**File**: `src/components/learning/AskTextbookButton.tsx`

**Purpose**: Floating action button visible on all docs pages to open the chat slide-out panel.

**Requirements** (from spec + clarifications):
- Floating button in bottom-right corner (FR-021)
- Opens slide-out panel on click (Clarification Q2)
- Visible on all docs pages

**Implementation Sketch**:

```typescript
import React from 'react';
import styles from './AskTextbookButton.module.css';

interface AskTextbookButtonProps {
  onClick: () => void;
}

export default function AskTextbookButton({ onClick }: AskTextbookButtonProps): JSX.Element {
  return (
    <button
      className={styles.floatingButton}
      onClick={onClick}
      aria-label="Ask the textbook a question"
      title="Ask the Textbook"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    </button>
  );
}
```

**CSS**: `src/components/learning/AskTextbookButton.module.css`

```css
.floatingButton {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #0066cc;
  color: white;
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  z-index: 999;
}

.floatingButton:hover {
  transform: scale(1.1);
}

/* Mobile: adjust positioning */
@media (max-width: 640px) {
  .floatingButton {
    bottom: 1rem;
    right: 1rem;
    width: 50px;
    height: 50px;
  }
}
```

### 4.4 ChatSlideoutPanel Component

**File**: `src/components/learning/ChatSlideoutPanel.tsx`

**Purpose**: Slide-out panel from right edge for whole-book Q&A (placeholder).

**Requirements**:
- Slides in from right/left edge (Clarification Q2)
- Input field + submit button (FR-023)
- Placeholder message: "RAG chatbot backend not connected yet" (FR-023)
- Closable via close button, ESC key, or click outside (FR-024)

**Implementation Sketch**:

```typescript
import React, { useEffect } from 'react';
import styles from './ChatSlideoutPanel.module.css';

interface ChatSlideoutPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatSlideoutPanel({ isOpen, onClose }: ChatSlideoutPanelProps): JSX.Element | null {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEsc);
    }
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Dimmed background overlay */}
      <div className={styles.overlay} onClick={onClose} />

      {/* Slide-out panel */}
      <div className={`${styles.slideoutPanel} ${isOpen ? styles.open : ''}`}>
        <div className={styles.header}>
          <h3>Ask the Textbook</h3>
          <button className={styles.closeButton} onClick={onClose} aria-label="Close chat">
            ×
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.placeholder}>
            <p><strong>RAG chatbot backend not connected yet.</strong></p>
            <p>Once integrated, this will answer questions about the entire textbook.</p>
          </div>

          <input
            type="text"
            className={styles.input}
            placeholder="Ask a question about the textbook..."
            disabled
          />
          <button className={styles.submitButton} disabled>
            Submit
          </button>
        </div>
      </div>
    </>
  );
}
```

**CSS**: `src/components/learning/ChatSlideoutPanel.module.css`

```css
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.slideoutPanel {
  position: fixed;
  top: 0;
  right: -400px;  /* Start off-screen */
  width: 400px;
  height: 100%;
  background-color: white;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease-in-out;
  z-index: 1001;
  display: flex;
  flex-direction: column;
}

.slideoutPanel.open {
  right: 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.closeButton {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
}

.content {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.placeholder {
  background-color: #f0f0f0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.input {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.submitButton {
  padding: 0.75rem;
  background-color: #0066cc;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: not-allowed;
  opacity: 0.5;
}

/* Mobile: full width */
@media (max-width: 640px) {
  .slideoutPanel {
    width: 100%;
    right: -100%;
  }
}
```

### 4.5 SelectionModal Component

**File**: `src/components/learning/SelectionModal.tsx`

**Purpose**: Centered modal for selection-based Q&A (distinct from slide-out panel).

**Requirements**:
- Opens when "Ask about this" is clicked (FR-026)
- Shows selected text (quoted/highlighted) (FR-026)
- Input field for question (FR-026)
- Placeholder message (FR-026)
- Closable via close button (X), ESC, or click outside (FR-026)
- Distinct from slide-out panel (Clarification Q3)

**Implementation Sketch**:

```typescript
import React, { useEffect } from 'react';
import styles from './SelectionModal.module.css';

interface SelectionModalProps {
  isOpen: boolean;
  selectedText: string;
  onClose: () => void;
}

export default function SelectionModal({ isOpen, selectedText, onClose }: SelectionModalProps): JSX.Element | null {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEsc);
    }
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose} aria-label="Close">
          ×
        </button>

        <h3>Ask About This Selection</h3>

        <div className={styles.selectedText}>
          <strong>Selected Text:</strong>
          <blockquote>{selectedText}</blockquote>
        </div>

        <div className={styles.placeholder}>
          <p><strong>Selection-based Q&A backend not connected yet.</strong></p>
          <p>Once integrated, this will answer questions restricted to your selected text.</p>
        </div>

        <input
          type="text"
          className={styles.input}
          placeholder="Ask a question about this selection..."
          disabled
        />
        <button className={styles.submitButton} disabled>
          Submit
        </button>
      </div>
    </div>
  );
}
```

**CSS**: `src/components/learning/SelectionModal.module.css`

```css
.modalOverlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;  /* Higher than slide-out panel */
}

.modalContent {
  background-color: white;
  padding: 2rem;
  border-radius: 0.75rem;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  position: relative;
}

.closeButton {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
}

.selectedText {
  background-color: #fff8e1;  /* Amber background */
  padding: 1rem;
  border-left: 4px solid #ff9500;
  margin: 1rem 0;
  border-radius: 0.25rem;
}

.selectedText blockquote {
  margin: 0.5rem 0 0 0;
  font-style: italic;
  color: #333;
}

.placeholder {
  background-color: #f0f0f0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.submitButton {
  width: 100%;
  padding: 0.75rem;
  background-color: #ff9500;  /* Amber/orange to distinguish from blue chat */
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: not-allowed;
  opacity: 0.5;
}
```

### 4.6 TextSelectionDetector Component

**File**: `src/components/learning/TextSelectionDetector.tsx`

**Purpose**: Detects text selection on docs pages and shows "Ask about this" button.

**Requirements**:
- Use native Selection API (Clarification Q1)
- Show button near selection (FR-025)
- Minimum selection length: 10 characters (to avoid accidental triggers)
- Custom CSS/JS, no external libraries (Clarification Q1)

**Implementation Sketch**:

```typescript
import React, { useState, useEffect, useCallback } from 'react';
import styles from './TextSelectionDetector.module.css';
import SelectionModal from './SelectionModal';

export default function TextSelectionDetector(): JSX.Element {
  const [selectedText, setSelectedText] = useState('');
  const [showButton, setShowButton] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ top: 0, left: 0 });
  const [showModal, setShowModal] = useState(false);

  const handleSelection = useCallback(() => {
    const selection = window.getSelection();
    const text = selection?.toString().trim() || '';

    if (text.length >= 10) {  // Minimum 10 characters
      setSelectedText(text);

      // Position button near selection
      const range = selection?.getRangeAt(0);
      const rect = range?.getBoundingClientRect();

      if (rect) {
        setButtonPosition({
          top: rect.bottom + window.scrollY + 5,
          left: rect.left + window.scrollX,
        });
        setShowButton(true);
      }
    } else {
      setShowButton(false);
    }
  }, []);

  useEffect(() => {
    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleSelection);

    // Hide button when clicking elsewhere
    const handleClickOutside = (e: MouseEvent) => {
      if (!(e.target as HTMLElement).closest(`.${styles.askButton}`)) {
        setShowButton(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleSelection);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [handleSelection]);

  return (
    <>
      {showButton && (
        <button
          className={styles.askButton}
          style={{ top: buttonPosition.top, left: buttonPosition.left }}
          onClick={() => {
            setShowModal(true);
            setShowButton(false);
          }}
        >
          Ask about this
        </button>
      )}

      <SelectionModal
        isOpen={showModal}
        selectedText={selectedText}
        onClose={() => setShowModal(false)}
      />
    </>
  );
}
```

**CSS**: `src/components/learning/TextSelectionDetector.module.css`

```css
.askButton {
  position: absolute;
  background-color: #ff9500;  /* Amber/orange */
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1500;
  transition: transform 0.2s;
}

.askButton:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
```

### 4.7 Homepage Components

**Files**:
- `src/pages/index.tsx` - Main homepage
- `src/components/homepage/Hero.tsx`
- `src/components/homepage/Features.tsx`
- `src/components/homepage/AuthorSection.tsx`

**Implementation**: Standard React components following Docusaurus patterns. See Docusaurus docs for homepage customization.

**Key Requirements** (from spec):
- Hero: Title "Physical AI & Humanoid Robotics", subtitle about embodied intelligence, "Start the Course" CTA button → `/docs/intro` (FR-013)
- Features: 4 cards (Physical AI, Sim-to-Real, AI Tutor, Adaptive Learning) (FR-014)
- Author Section: "Authored by Tayyab Aziz" + GitHub link (FR-015)

---

## 5. Selection-Based Q&A Frontend Hook

### 5.1 Integration Strategy

**Approach**: Wrap all docs pages with `TextSelectionDetector` component via custom layout.

**File**: `src/theme/Layout/index.tsx` (swizzled Docusaurus layout)

**Implementation**:

```bash
# Swizzle the Layout component to customize it
npm run swizzle @docusaurus/theme-classic Layout -- --eject
```

**Edit**: `src/theme/Layout/index.tsx`

```typescript
import React from 'react';
import Layout from '@theme-original/Layout';
import type LayoutType from '@theme/Layout';
import type { WrapperProps } from '@docusaurus/types';
import TextSelectionDetector from '@site/src/components/learning/TextSelectionDetector';
import AskTextbookButton from '@site/src/components/learning/AskTextbookButton';
import ChatSlideoutPanel from '@site/src/components/learning/ChatSlideoutPanel';
import { useState } from 'react';

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props): JSX.Element {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      <Layout {...props} />
      <TextSelectionDetector />
      <AskTextbookButton onClick={() => setChatOpen(true)} />
      <ChatSlideoutPanel isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </>
  );
}
```

**Rationale**:
- Wrapping the layout ensures selection detection and chat button are available on all pages
- No need to manually add components to each MDX file
- Clean separation: layout handles interactive features, MDX handles content

### 5.2 Selection Detection Logic

**Key Implementation Details**:
- Use `window.getSelection()` API (native, no libraries)
- Minimum selection length: **10 characters** (avoids accidental triggers)
- Listen to `mouseup` and `keyup` events (handles both mouse and keyboard selection)
- Position "Ask about this" button near selection using `Range.getBoundingClientRect()`
- Hide button when user clicks elsewhere or clears selection

**Edge Cases to Handle**:
- Selection spans multiple elements (use `Range.getBoundingClientRect()`)
- Selection on mobile (handle touch events)
- Selection in code blocks (may want to disable in `<pre>` tags)

---

## 6. Responsive & Theming Strategy

### 6.1 Responsive Design Approach

**Mobile-First CSS** with these breakpoints:
- **≤ 640px**: Phone (buttons stack vertically, full-width chat panel)
- **641px - 1024px**: Tablet (buttons horizontal, chat panel 400px width)
- **> 1024px**: Desktop (full layout)

**Key Responsive Behaviors** (from spec):
- ChapterActionsBar buttons: Stack vertically on ≤ 640px (FR-020, Clarification Q5)
- ChatSlideoutPanel: Full width on mobile, 400px on desktop
- AskTextbookButton: Adjusted size/position on mobile (50px vs 60px)
- Sidebar: Docusaurus handles collapse to hamburger menu (NFR-011)

**CSS File**: `src/css/responsive.css`

```css
/* Mobile base styles */
@media (max-width: 640px) {
  /* Button stacking handled in ChapterActionsBar.module.css */

  /* Touch targets */
  button {
    min-width: 44px;
    min-height: 44px;
  }

  /* Text sizing */
  body {
    font-size: 16px;  /* Prevent iOS zoom on input focus */
  }
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  /* ... */
}

/* Desktop */
@media (min-width: 1025px) {
  /* ... */
}
```

### 6.2 Theme & Color Strategy

**Approach**: Minimize custom theming, use Docusaurus defaults with minor adjustments.

**Color Palette** (from clarifications & spec):
- **Primary Blue**: `#0066cc` (for "Ask the Textbook", "Personalize" button)
- **Amber/Orange**: `#ff9500` (for "Ask about this", "View in Urdu" button)
- **Background**: Docusaurus default light/dark themes
- **Contrast**: Ensure WCAG 2.1 AA compliance (4.5:1 for text) (NFR-010)

**Dark Mode**:
- Respect user's system preference (configured in `docusaurus.config.ts`)
- Allow manual toggle
- Test modals and panels in both modes

**CSS File**: `src/css/custom.css`

```css
:root {
  --ifm-color-primary: #0066cc;
  --ifm-color-primary-dark: #0052a3;
  --ifm-color-primary-darker: #004a99;
  --ifm-color-primary-darkest: #003d7a;
  --ifm-color-primary-light: #007ae6;
  --ifm-color-primary-lighter: #0080f0;
  --ifm-color-primary-lightest: #1a8cff;

  --selection-color: #ff9500;  /* Amber for selection-based Q&A */
}

/* Dark mode adjustments */
[data-theme='dark'] {
  --ifm-color-primary: #1a8cff;
  /* ... adjust other colors */
}

/* Ensure accessibility */
.modalContent, .slideoutPanel {
  color: #333;
}

[data-theme='dark'] .modalContent,
[data-theme='dark'] .slideoutPanel {
  background-color: #1c1e21;
  color: #e3e3e3;
}
```

---

## 7. Build & Deployment Preparation

### 7.1 npm Scripts (Already Defined in Section 1.4)

```json
"scripts": {
  "start": "docusaurus start",
  "build": "docusaurus build",
  "serve": "docusaurus serve",
  "deploy": "docusaurus deploy"
}
```

### 7.2 GitHub Pages Configuration

**In `docusaurus.config.ts`**:

```typescript
{
  url: 'https://<USERNAME>.github.io',
  baseUrl: '/physical-ai-humanoid-textbook/',
  organizationName: '<USERNAME>',
  projectName: 'physical-ai-humanoid-textbook',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,
}
```

**Deployment Steps** (manual, for now):

1. Build the site:
   ```bash
   npm run build
   ```

2. Deploy to GitHub Pages:
   ```bash
   GIT_USER=<USERNAME> npm run deploy
   ```

**Alternative: GitHub Actions** (future enhancement, not in this feature):
- Create `.github/workflows/deploy.yml` to auto-deploy on push to main
- Configure `GITHUB_TOKEN` secret

### 7.3 Static File Requirements

**File**: `static/.nojekyll`

**Purpose**: Tells GitHub Pages not to process the site with Jekyll (Docusaurus builds are already static).

**Content**: Empty file (just create it).

### 7.4 Environment Variables (None for Frontend-Only)

**Important**: This feature is **frontend-only** with **no backend integration**.

- **No API keys** needed (no OpenAI, Qdrant, Neon, Better-Auth)
- **No .env file** required
- All placeholder components use console.log or static alerts

**Future**: When backend is added, create `.env` for `OPENAI_API_KEY`, etc., and add `.env` to `.gitignore`.

### 7.5 .gitignore

**File**: `.gitignore`

```gitignore
# Dependencies
node_modules/
package-lock.json  # (optional, some teams commit this)

# Build output
build/
.docusaurus/
.cache-loader/

# Environment variables (future)
.env
.env.local
.env.production

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## 8. Risk & Complexity Notes

### 8.1 Identified Risks

#### Risk 1: Text Selection Tooltip Conflicts with Docusaurus Layout

**Description**: The custom text selection tooltip may conflict with Docusaurus's internal event handling or layout structure.

**Likelihood**: Medium
**Impact**: Medium (feature may not work correctly)

**Mitigation**:
- Use `z-index` carefully (set tooltip to `z-index: 1500`, higher than Docusaurus default)
- Test on multiple browsers (Chrome, Firefox, Safari)
- Ensure tooltip doesn't interfere with link clicks or navigation
- Add `pointer-events: none` to tooltip overlay if needed

**Testing**:
- Select text in various locations (paragraphs, code blocks, lists)
- Verify tooltip appears correctly and doesn't block interaction
- Test on mobile (touch selection)

#### Risk 2: MDX + Custom Components Causing Build Issues

**Description**: Importing custom React components into MDX files may cause build errors or type issues.

**Likelihood**: Low
**Impact**: High (blocks build/deployment)

**Mitigation**:
- Follow Docusaurus MDX documentation exactly
- Use `@site/` alias for imports (configured in tsconfig.json)
- Test incremental builds after adding each component
- Use `docusaurus clear` to clear cache if build issues occur

**Example** (correct import in MDX):
```mdx
import ChapterActionsBar from '@site/src/components/learning/ChapterActionsBar';
```

#### Risk 3: Responsive Design Testing Coverage

**Description**: Ensuring all components work correctly on all screen sizes (320px to 1920px+) requires extensive testing.

**Likelihood**: Medium
**Impact**: Medium (UX degradation on some devices)

**Mitigation**:
- Use browser DevTools to test common breakpoints (375px, 768px, 1024px, 1920px)
- Test on real devices if available (iPhone, iPad, Android phone)
- Use CSS Grid/Flexbox (modern, responsive-by-default)
- Prioritize desktop + tablet for MVP, refine mobile in follow-up

**Test Matrix**:
- 320px (iPhone SE) - minimum width per NFR-009
- 375px (iPhone 12/13)
- 640px (breakpoint for button stacking)
- 768px (tablet)
- 1024px (large tablet / small desktop)
- 1920px (desktop)

#### Risk 4: Slide-Out Panel Performance on Mobile

**Description**: Slide-out panel animation may be janky on low-end mobile devices.

**Likelihood**: Low
**Impact**: Low (cosmetic issue)

**Mitigation**:
- Use CSS `transform` instead of `right` property for animation (hardware-accelerated)
- Add `will-change: transform` hint
- Test on low-end device or throttled Chrome DevTools

**Optimized CSS**:
```css
.slideoutPanel {
  transform: translateX(100%);  /* Start off-screen */
  transition: transform 0.3s ease-in-out;
}

.slideoutPanel.open {
  transform: translateX(0);
}
```

### 8.2 Implementation Order (Incremental Approach)

**Recommended Order** to minimize risk and enable early testing:

**Phase 1: Core Structure (Days 1-2)**
1. Initialize Docusaurus project (`npx create-docusaurus@latest`)
2. Configure `docusaurus.config.ts` (title, navbar, footer, GitHub Pages config)
3. Configure `sidebars.ts` (4 modules structure)
4. Create docs tree (intro.md + 8 MDX files with placeholder content)
5. Test local build (`npm start`) and verify navigation

**Phase 2: Homepage (Day 2)**
6. Create `src/pages/index.tsx` (homepage)
7. Build Hero, Features, AuthorSection components
8. Test homepage → docs navigation

**Phase 3: Chapter Actions (Day 3)**
9. Build `ChapterActionsBar` component (buttons + modals)
10. Import into module MDX files
11. Test responsive behavior (640px breakpoint)
12. Test placeholder modals

**Phase 4: Chat UI (Day 4)**
13. Build `AskTextbookButton` component
14. Build `ChatSlideoutPanel` component
15. Integrate into layout wrapper
16. Test slide-out animation and placeholder behavior

**Phase 5: Selection-Based Q&A (Day 5)**
17. Build `TextSelectionDetector` component
18. Build `SelectionModal` component
19. Integrate into layout wrapper
20. Test text selection detection and modal behavior

**Phase 6: Polish & Testing (Day 6)**
21. Add responsive CSS refinements
22. Test on multiple browsers and devices
23. Fix any build issues or bugs
24. Create `/chat` placeholder page
25. Final production build test

**Phase 7: Deployment (Day 7)**
26. Deploy to GitHub Pages
27. Verify deployed site
28. Create README with setup instructions
29. Create demo video (if needed for hackathon)

### 8.3 Complexity Estimates

| Component | Complexity | Estimated Time |
|-----------|-----------|----------------|
| Docusaurus Setup & Config | Low | 2-3 hours |
| Docs Structure (MDX files) | Low | 2-3 hours |
| Homepage Components | Medium | 4-5 hours |
| ChapterActionsBar | Medium | 3-4 hours |
| ChatSlideoutPanel | Medium | 3-4 hours |
| AskTextbookButton | Low | 1-2 hours |
| TextSelectionDetector | High | 5-6 hours |
| SelectionModal | Medium | 2-3 hours |
| Responsive CSS | Medium | 3-4 hours |
| Testing & Bug Fixes | Medium | 4-6 hours |
| Deployment Setup | Low | 1-2 hours |
| **Total** | | **30-40 hours** |

**Note**: Assumes solo developer with Docusaurus + React + TypeScript experience.

---

## 9. Architecture Decision Records (ADRs)

The following architectural decisions have been made and should be documented as ADRs per constitution section VII.C:

### ADR 1: Use Docusaurus v3 with TypeScript Classic Preset

**Decision**: Use Docusaurus v3.x (latest stable) with the classic preset and TypeScript.

**Context**: Need a static site generator optimized for documentation with good DX, TypeScript support, and React integration for custom components.

**Alternatives Considered**:
- Docusaurus v2 (older, stable but less features)
- Next.js + Nextra (more complex, overkill for this use case)
- VitePress (Vue-based, less React ecosystem compatibility)

**Rationale**:
- Docusaurus is purpose-built for documentation sites
- Classic preset provides good defaults (sidebar, navbar, search)
- TypeScript support is first-class
- Large community and plugin ecosystem
- Easy GitHub Pages deployment

**Trade-offs**:
- Less flexibility than custom Next.js (but we don't need it)
- Opinionated structure (but this is a benefit for consistency)

**Status**: Accepted

---

### ADR 2: Custom Text Selection Detection Without External Libraries

**Decision**: Implement text selection detection using native Selection API with custom CSS/JS, no external libraries.

**Context**: Need to detect text selection on docs pages to show "Ask about this" button. Clarification Q1 specified custom solution.

**Alternatives Considered**:
- `react-text-selection-popover` library (~15KB)
- Tippy.js for tooltip positioning (~20KB)
- No text selection feature (defer to future)

**Rationale**:
- Native Selection API is well-supported (IE11+)
- Custom solution gives full control over UX and styling
- Minimizes dependencies (constitution NFR-004)
- Lightweight implementation (<100 lines of code)

**Trade-offs**:
- More development time vs using a library
- Need to handle edge cases manually (mobile, code blocks, etc.)
- Potential browser compatibility issues (mitigated by modern browser support)

**Status**: Accepted

---

### ADR 3: Slide-Out Panel for Chat, Separate Modal for Selection-Based Q&A

**Decision**: Use slide-out panel from right edge for whole-book chat, separate centered modal for selection-based Q&A.

**Context**: Need clear visual distinction between whole-book and selection-based query modes. Clarifications Q2 and Q3 specified this approach.

**Alternatives Considered**:
- Same slide-out panel for both modes (rejected: less clear distinction)
- Both as modals (rejected: modal fatigue, less modern UX for primary chat)
- Inline expansion near selection (rejected: too disruptive)

**Rationale**:
- Slide-out panel is modern UX pattern for primary chat features (Slack, Discord, etc.)
- Separate modal for selection-based Q&A provides clear mode distinction (FR-027)
- Different colors (blue slide-out, amber modal) reinforce distinction

**Trade-offs**:
- Need to implement two separate components (more code)
- Two different interaction patterns (but this is intentional for clarity)

**Status**: Accepted

---

## 10. Dependencies & Prerequisites

### 10.1 Required npm Packages

**Core Docusaurus Dependencies** (installed via `create-docusaurus`):

```json
{
  "dependencies": {
    "@docusaurus/core": "^3.0.0",
    "@docusaurus/preset-classic": "^3.0.0",
    "@docusaurus/theme-common": "^3.0.0",
    "@docusaurus/types": "^3.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@docusaurus/tsconfig": "^3.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

**No additional UI libraries** are needed (per constitution NFR-004).

### 10.2 Development Environment

**Required**:
- Node.js 18.x or 20.x (LTS)
- npm 9.x or later
- Git
- Code editor (VS Code recommended with Docusaurus extension)

**Optional**:
- Browser DevTools (Chrome/Firefox)
- React DevTools browser extension

### 10.3 External Services (None for Frontend-Only)

**This feature does NOT depend on**:
- OpenAI API
- Qdrant Cloud
- Neon Postgres
- Better-Auth

All external services will be integrated in separate backend feature.

---

## 11. Testing Strategy (Manual QA)

**Note**: Per spec Out of Scope section, automated testing is not required for this feature. Manual QA is sufficient.

### 11.1 Test Checklist

**Functional Tests**:
- [ ] Homepage displays hero, features, author section
- [ ] "Start the Course" button navigates to `/docs/intro`
- [ ] Sidebar shows 4 modules, each with overview + chapter 1
- [ ] Smart sidebar expansion: current module expands, others collapse
- [ ] "Course" link in navbar navigates to `/docs/intro`
- [ ] "Study Assistant" link navigates to `/chat` placeholder page
- [ ] Blog link is NOT visible in navbar
- [ ] ChapterActionsBar appears on all module content pages (not on intro)
- [ ] "Personalize for Me" button shows placeholder modal
- [ ] "View in Urdu" button shows placeholder modal
- [ ] Buttons stack vertically on screens ≤ 640px
- [ ] "Ask the Textbook" floating button visible on all docs pages
- [ ] Clicking floating button opens slide-out chat panel
- [ ] Chat panel slides in from right, shows placeholder message
- [ ] Chat panel closable via close button, ESC key, or click outside
- [ ] Selecting 10+ characters shows "Ask about this" button near selection
- [ ] Clicking "Ask about this" opens centered modal with selected text
- [ ] Selection modal shows placeholder message
- [ ] Selection modal closable via X button, ESC, or click outside
- [ ] Visual distinction clear between slide-out panel (blue) and modal (amber)

**Responsive Tests** (test on each breakpoint):
- [ ] 320px (iPhone SE): All elements visible, no horizontal scroll
- [ ] 375px (iPhone 12): Buttons stack, text readable
- [ ] 640px: Breakpoint works correctly (buttons stack below, horizontal above)
- [ ] 768px (iPad): Layout looks good, sidebar hamburger works
- [ ] 1024px: Desktop layout looks good
- [ ] 1920px: No weird stretching or layout issues

**Browser Tests**:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

**Accessibility Tests**:
- [ ] Tab navigation works through all interactive elements
- [ ] Focus indicators visible on all buttons/links
- [ ] Screen reader announces button labels correctly (test with VoiceOver/NVDA)
- [ ] Color contrast meets WCAG 2.1 AA (use browser tools to check)

### 11.2 Test Execution

**Run tests after each implementation phase** (see Section 8.2 implementation order).

**Bug Tracking**: Document bugs in a simple markdown file (`BUGS.md`) or GitHub issues.

---

## 12. Documentation Requirements

### 12.1 README.md

**File**: `README.md` (repository root)

**Required Sections**:
1. **Project Title & Description**
   - "Physical AI & Humanoid Robotics Textbook"
   - Brief description of the project
   - Author credit: "Authored by Tayyab Aziz"

2. **Tech Stack**
   - Docusaurus v3.x
   - TypeScript
   - React 18
   - npm

3. **Prerequisites**
   - Node.js 18.x or 20.x
   - npm 9.x or later

4. **Setup Instructions**
   ```bash
   # Clone repository
   git clone https://github.com/<USERNAME>/physical-ai-humanoid-textbook.git
   cd physical-ai-humanoid-textbook

   # Install dependencies
   npm install

   # Start development server
   npm start
   ```

5. **Build & Deployment**
   ```bash
   # Build for production
   npm run build

   # Serve production build locally
   npm run serve

   # Deploy to GitHub Pages
   GIT_USER=<USERNAME> npm run deploy
   ```

6. **Project Structure**
   - Brief overview of key directories (docs/, src/components/, etc.)

7. **Features** (with "Coming Soon" indicators)
   - Docusaurus textbook structure ✅
   - RAG chatbot (placeholder) 🚧
   - Personalization (placeholder) 🚧
   - Urdu translation (placeholder) 🚧

8. **Links**
   - Deployed site URL
   - GitHub repository
   - Author GitHub profile

### 12.2 Inline Code Comments

**Guidelines**:
- Add JSDoc comments to all exported components
- Explain non-obvious logic (e.g., text selection detection algorithm)
- Document props with TypeScript interfaces (self-documenting)

**Example**:
```typescript
/**
 * Detects text selection on docs pages and shows "Ask about this" button.
 * Uses native Selection API with minimum 10-character threshold.
 */
export default function TextSelectionDetector(): JSX.Element {
  // ...
}
```

---

## 13. Success Criteria (From Spec)

This implementation must satisfy all success criteria from the specification:

- **SC-001**: Developer can run `npm install && npm start` and view site at http://localhost:3000 without errors within 2 minutes. ✅
- **SC-002**: Homepage displays all required sections and "Start the Course" button navigates to `/docs/intro`. ✅
- **SC-003**: All 4 modules visible in sidebar with overview + chapter 1 accessible via clean URLs. ✅
- **SC-004**: Clicking "Personalize for Me" or "View in Urdu" triggers placeholder message. ✅
- **SC-005**: "Ask the Textbook" entry point visible, opens placeholder chat interface. ✅
- **SC-006**: Selecting text triggers "Ask about this" button, opens placeholder modal. ✅
- **SC-007**: Blog link NOT visible in navbar. ✅
- **SC-008**: Production build (`npm run build`) completes without errors, generates `build/` directory. ✅
- **SC-009**: Site responsive on 320px and 1920px without horizontal scrolling or broken layouts. ✅
- **SC-010**: README documents setup, build, and deployment steps for new contributors. ✅

---

## 14. Next Steps (Post-Implementation)

After this feature is complete and deployed:

1. **Run `/sp.tasks`** to generate atomic, testable tasks from this plan
2. **Run `/sp.implement`** to execute the tasks incrementally
3. **Create demo video** (90 seconds max) for hackathon submission
4. **Backend Integration** (separate feature):
   - FastAPI backend in `backend/` directory
   - Qdrant + Neon + OpenAI integration
   - Better-Auth signup/signin
5. **Content Creation** (separate features per module):
   - Module 1: ROS 2 detailed content
   - Module 2: Digital Twin detailed content
   - Module 3: NVIDIA Isaac detailed content
   - Module 4: VLA detailed content

---

## 15. Conclusion

This plan provides a comprehensive, actionable blueprint for implementing the Docusaurus frontend structure. The implementation is **frontend-only**, with clear separation from future backend work. All architectural decisions align with the specification, clarifications, and constitution.

**Key Principles Maintained**:
- ✅ Structure-before-content (Constitution Section II)
- ✅ Minimal dependencies (Constitution NFR-004)
- ✅ Clear separation of concerns (frontend vs backend)
- ✅ Responsive design (mobile-first, WCAG 2.1 AA)
- ✅ No premature backend integration

**Ready for Task Breakdown**: This plan contains sufficient detail (file paths, component structures, CSS examples) for `/sp.tasks` to generate concrete implementation tasks.

---

**Plan Version**: 1.0.0
**Last Updated**: 2025-12-05
**Author**: Tayyab Aziz
**Status**: Ready for `/sp.tasks` → `/sp.implement`
