# Tasks: Docusaurus Frontend Structure

**Feature**: 001-docusaurus-frontend (Docusaurus Frontend Structure)
**Based on**: `specs/docusaurus-frontend-structure/plan.md`
**Environment**: WSL (Windows Subsystem for Linux)
**Package Manager**: npm (required)
**Node Version**: 18.x or 20.x LTS

---

## Task Format

- **[P]** = Parallelizable (can run simultaneously with other [P] tasks in same phase)
- **File paths** = Exact locations as specified in plan.md
- **Sequential by default** = Tasks run in order unless marked [P]

---

## Phase 1: Initial Docusaurus Setup at Repository Root

**Goal**: Initialize Docusaurus v3.x project with TypeScript classic preset at repo root

### T001: Verify Node.js and npm versions
```bash
node --version  # Should be 18.x or 20.x
npm --version   # Should be 9.x or later
```
**Expected**: Node 18+ and npm 9+ installed

### T002: Initialize Docusaurus project at repository root
```bash
cd /mnt/e/Certified\ Cloud\ Native\ Applied\ Generative\ and\ Agentic\ AI\ Engineer/Q4\ part\ 2/Hackathon/physical-ai-humanoid-textbook
npx create-docusaurus@latest . classic --typescript
```
**Input when prompted**:
- Template: `classic`
- TypeScript: `Yes`

**Expected**: Creates `docs/`, `src/`, `static/`, `docusaurus.config.ts`, `sidebars.ts`, `package.json`, `tsconfig.json`

### T003: Add Node.js engine requirement to package.json
**File**: `package.json`

Add to root level (after `"name"` field):
```json
"engines": {
  "node": ">=18.0.0",
  "npm": ">=9.0.0"
},
```

### T004: Update tsconfig.json with path aliases
**File**: `tsconfig.json`

Replace entire file with:
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

### T005: Create .gitignore (if not exists) with proper exclusions
**File**: `.gitignore`

Append or create:
```gitignore
# Dependencies
node_modules/

# Build output
build/
.docusaurus/
.cache-loader/

# Environment variables
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

### T006: Create static/.nojekyll for GitHub Pages
**File**: `static/.nojekyll`

Create empty file:
```bash
touch static/.nojekyll
```

### T007: Install dependencies
```bash
npm install
```
**Expected**: Dependencies install without errors

### T008: Test initial build
```bash
npm start
```
**Expected**: Dev server starts on `http://localhost:3000`, default Docusaurus site loads
**Action**: Stop server with Ctrl+C after verification

---

## Phase 2: Docusaurus Configuration (Main Config)

**Goal**: Configure site metadata, navbar, footer, and deployment settings

### T009: Configure site metadata in docusaurus.config.ts
**File**: `docusaurus.config.ts`

Update config object:
```typescript
const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Bridging the gap between digital intelligence and the physical world through embodied AI',
  favicon: 'img/favicon.ico',

  // GitHub Pages deployment config (update USERNAME with actual)
  url: 'https://<USERNAME>.github.io',
  baseUrl: '/physical-ai-humanoid-textbook/',
  organizationName: '<USERNAME>',
  projectName: 'physical-ai-humanoid-textbook',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  // ... rest of config
```

**Note**: Replace `<USERNAME>` with actual GitHub username (e.g., `Psqasim`)

### T010: Configure navbar in docusaurus.config.ts
**File**: `docusaurus.config.ts`

In `themeConfig.navbar`:
```typescript
navbar: {
  title: 'Physical AI & Humanoid Robotics',
  logo: {
    alt: 'Physical AI Logo',
    src: 'img/logo.svg',
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
      href: 'https://github.com/Psqasim',
      label: 'GitHub',
      position: 'right',
    },
  ],
},
```

### T011: Configure footer in docusaurus.config.ts
**File**: `docusaurus.config.ts`

In `themeConfig.footer`:
```typescript
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
      ],
    },
  ],
  copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Authored by Tayyab Aziz.`,
},
```

### T012: Hide blog in preset configuration
**File**: `docusaurus.config.ts`

In `presets[0][1]` (classic preset options):
```typescript
presets: [
  [
    'classic',
    {
      docs: {
        sidebarPath: './sidebars.ts',
      },
      blog: false,  // Hide blog entirely
      theme: {
        customCss: './src/css/custom.css',
      },
    } satisfies Preset.Options,
  ],
],
```

### T013: Configure Prism themes for code blocks
**File**: `docusaurus.config.ts`

In `themeConfig`:
```typescript
prism: {
  theme: prismThemes.github,
  darkTheme: prismThemes.dracula,
  additionalLanguages: ['python', 'bash', 'yaml'],
},
```

Add import at top:
```typescript
import {themes as prismThemes} from 'prism-react-renderer';
```

### T014: Configure color mode settings
**File**: `docusaurus.config.ts`

In `themeConfig`:
```typescript
colorMode: {
  defaultMode: 'light',
  disableSwitch: false,
  respectPrefersColorScheme: true,
},
```

---

## Phase 3: Sidebar Configuration

**Goal**: Configure sidebar with 4 modules and smart expansion behavior

### T015: Create sidebar structure in sidebars.ts
**File**: `sidebars.ts`

Replace entire file:
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
      collapsed: true,
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

**Note**: `collapsed: true` enables smart expansion (only current module expands)

---

## Phase 4: Docs Tree Creation (Intro + 4 Modules)

**Goal**: Create all markdown/MDX files with placeholder content

### T016 [P]: Create docs/intro.md
**File**: `docs/intro.md`

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

### T017 [P]: Create module-1-ros2 directory and overview.mdx
**Directory**: `docs/module-1-ros2/`
**File**: `docs/module-1-ros2/overview.mdx`

```bash
mkdir -p docs/module-1-ros2
```

```mdx
---
id: module-1-ros2-overview
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

**Next**: Proceed to [Chapter 1: Basics](./chapter-1-basics) to dive into ROS 2 fundamentals.
```

### T018 [P]: Create module-1-ros2/chapter-1-basics.mdx
**File**: `docs/module-1-ros2/chapter-1-basics.mdx`

```mdx
---
id: module-1-ros2-chapter-1-basics
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

### T019 [P]: Create module-2-digital-twin-gazebo-unity directory and files
**Directory**: `docs/module-2-digital-twin-gazebo-unity/`

```bash
mkdir -p docs/module-2-digital-twin-gazebo-unity
```

**File**: `docs/module-2-digital-twin-gazebo-unity/overview.mdx`
```mdx
---
id: module-2-digital-twin-overview
title: Module 2 Overview - Digital Twin
sidebar_label: Overview
---

# Module 2: Digital Twin (Gazebo & Unity)

## Overview

Digital twins allow us to simulate robots in virtual environments before deploying to the real world. This module covers Gazebo (physics simulation) and Unity (high-fidelity rendering).

## What You'll Learn

- Setting up Gazebo for robotics simulation
- Creating URDF models for humanoid robots
- Integrating Unity for realistic rendering
- Sim-to-real transfer techniques

---

**Next**: [Chapter 1: Simulation Basics](./chapter-1-simulation-basics)
```

**File**: `docs/module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics.mdx`
```mdx
---
id: module-2-digital-twin-chapter-1
title: Chapter 1 - Simulation Basics
sidebar_label: Chapter 1: Simulation Basics
---

# Chapter 1: Simulation Basics

This chapter introduces the fundamentals of robot simulation using Gazebo and Unity.

**Topics Covered:**
- Why simulate before deploying?
- Setting up Gazebo environment
- Loading robot models

---

*Note: Placeholder content. Full chapter coming soon.*
```

### T020 [P]: Create module-3-nvidia-isaac directory and files
**Directory**: `docs/module-3-nvidia-isaac/`

```bash
mkdir -p docs/module-3-nvidia-isaac
```

**File**: `docs/module-3-nvidia-isaac/overview.mdx`
```mdx
---
id: module-3-nvidia-isaac-overview
title: Module 3 Overview - NVIDIA Isaac
sidebar_label: Overview
---

# Module 3: NVIDIA Isaac (AI-Robot Brain)

## Overview

NVIDIA Isaac provides advanced AI capabilities for robotics, including perception, navigation, and manipulation powered by deep learning.

## What You'll Learn

- Isaac Sim for robot training
- Perception with Isaac SDK
- AI-powered navigation and manipulation

---

**Next**: [Chapter 1: Getting Started](./chapter-1-getting-started)
```

**File**: `docs/module-3-nvidia-isaac/chapter-1-getting-started.mdx`
```mdx
---
id: module-3-nvidia-isaac-chapter-1
title: Chapter 1 - Getting Started with Isaac
sidebar_label: Chapter 1: Getting Started
---

# Chapter 1: Getting Started with NVIDIA Isaac

This chapter guides you through setting up the Isaac platform.

**Topics Covered:**
- Installing Isaac Sim
- Running your first simulation
- Basic perception tasks

---

*Note: Placeholder content.*
```

### T021 [P]: Create module-4-vision-language-action directory and files
**Directory**: `docs/module-4-vision-language-action/`

```bash
mkdir -p docs/module-4-vision-language-action
```

**File**: `docs/module-4-vision-language-action/overview.mdx`
```mdx
---
id: module-4-vla-overview
title: Module 4 Overview - Vision-Language-Action
sidebar_label: Overview
---

# Module 4: Vision-Language-Action (VLA)

## Overview

VLA models combine computer vision, natural language understanding, and robotic control to enable robots to understand and execute complex instructions.

## What You'll Learn

- VLA model architectures
- Training robots with language instructions
- Integrating vision and language for manipulation

---

**Next**: [Chapter 1: VLA Introduction](./chapter-1-vla-intro)
```

**File**: `docs/module-4-vision-language-action/chapter-1-vla-intro.mdx`
```mdx
---
id: module-4-vla-chapter-1
title: Chapter 1 - Introduction to VLA
sidebar_label: Chapter 1: VLA Intro
---

# Chapter 1: Introduction to Vision-Language-Action

This chapter introduces the VLA paradigm for robotic control.

**Topics Covered:**
- What are VLA models?
- Key architectures (RT-1, RT-2)
- Training with demonstrations

---

*Note: Placeholder content.*
```

### T022: Test docs structure
```bash
npm start
```
**Expected**:
- Homepage loads
- Sidebar shows Intro + 4 modules (collapsed)
- All docs pages accessible via sidebar
- Blog link NOT visible in navbar

**Action**: Navigate through all pages, verify clean URLs, then stop server

---

## Phase 5: Custom CSS Setup

**Goal**: Create global and responsive CSS files

### T023 [P]: Create src/css/custom.css with color scheme
**File**: `src/css/custom.css`

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
}

/* Ensure accessibility in modals and panels */
.modalContent, .slideoutPanel {
  color: #333;
}

[data-theme='dark'] .modalContent,
[data-theme='dark'] .slideoutPanel {
  background-color: #1c1e21;
  color: #e3e3e3;
}
```

### T024 [P]: Create src/css/responsive.css with breakpoints
**File**: `src/css/responsive.css`

```css
/* Mobile base styles (≤640px) */
@media (max-width: 640px) {
  button {
    min-width: 44px;
    min-height: 44px;
  }

  body {
    font-size: 16px;  /* Prevent iOS zoom on input focus */
  }
}

/* Tablet (641px - 1024px) */
@media (min-width: 641px) and (max-width: 1024px) {
  /* Tablet-specific styles if needed */
}

/* Desktop (>1024px) */
@media (min-width: 1025px) {
  /* Desktop-specific styles if needed */
}
```

### T025: Import responsive.css into custom.css
**File**: `src/css/custom.css`

Add at top:
```css
@import './responsive.css';
```

---

## Phase 6: Homepage Implementation

**Goal**: Create custom homepage with hero, features, and author sections

### T026: Create homepage directory structure
```bash
mkdir -p src/components/homepage
```

### T027 [P]: Create src/components/homepage/Hero.tsx
**File**: `src/components/homepage/Hero.tsx`

```typescript
import React from 'react';
import Link from '@docusaurus/Link';
import styles from './Hero.module.css';

export default function Hero(): JSX.Element {
  return (
    <div className={styles.hero}>
      <div className={styles.heroContent}>
        <h1 className={styles.heroTitle}>Physical AI & Humanoid Robotics</h1>
        <p className={styles.heroSubtitle}>
          Bridging the gap between digital intelligence and the physical world through embodied AI
        </p>
        <Link
          className={styles.heroButton}
          to="/docs/intro">
          Start the Course
        </Link>
      </div>
    </div>
  );
}
```

**File**: `src/components/homepage/Hero.module.css`
```css
.hero {
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.heroContent {
  max-width: 800px;
  margin: 0 auto;
}

.heroTitle {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.heroSubtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.95;
}

.heroButton {
  display: inline-block;
  padding: 1rem 2rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
  background-color: #0066cc;
  border-radius: 0.5rem;
  text-decoration: none;
  transition: transform 0.2s;
}

.heroButton:hover {
  transform: translateY(-2px);
  color: white;
  text-decoration: none;
}

@media (max-width: 640px) {
  .heroTitle {
    font-size: 2rem;
  }
  .heroSubtitle {
    font-size: 1rem;
  }
}
```

### T028 [P]: Create src/components/homepage/Features.tsx
**File**: `src/components/homepage/Features.tsx`

```typescript
import React from 'react';
import styles from './Features.module.css';

const FeatureList = [
  {
    title: 'Physical AI & Embodied Intelligence',
    description: 'Learn how AI systems interact with the physical world through sensors, actuators, and embodied reasoning.',
  },
  {
    title: 'Sim-to-Real Robotics',
    description: 'Master digital twins using Gazebo and Unity to simulate and train robots before real-world deployment.',
  },
  {
    title: 'Integrated AI Tutor',
    description: 'RAG-powered chatbot coming soon to answer your questions about the textbook content.',
  },
  {
    title: 'Adaptive Learning',
    description: 'Content adapts to your skill level: beginner, intermediate, or advanced (feature in development).',
  },
];

export default function Features(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className={styles.container}>
        <div className={styles.featureGrid}>
          {FeatureList.map((feature, idx) => (
            <div key={idx} className={styles.featureCard}>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
```

**File**: `src/components/homepage/Features.module.css`
```css
.features {
  padding: 4rem 2rem;
  background-color: #f5f5f5;
}

[data-theme='dark'] .features {
  background-color: #1c1e21;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.featureGrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.featureCard {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

[data-theme='dark'] .featureCard {
  background: #2a2a2a;
}

.featureCard h3 {
  margin-bottom: 0.75rem;
  color: #0066cc;
}

.featureCard p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

[data-theme='dark'] .featureCard p {
  color: #ccc;
}
```

### T029 [P]: Create src/components/homepage/AuthorSection.tsx
**File**: `src/components/homepage/AuthorSection.tsx`

```typescript
import React from 'react';
import styles from './AuthorSection.module.css';

export default function AuthorSection(): JSX.Element {
  return (
    <section className={styles.authorSection}>
      <div className={styles.container}>
        <h2>About the Author</h2>
        <p>
          <strong>Authored by Tayyab Aziz</strong>
        </p>
        <p>
          Connect on{' '}
          <a
            href="https://github.com/Psqasim"
            target="_blank"
            rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </div>
    </section>
  );
}
```

**File**: `src/components/homepage/AuthorSection.module.css`
```css
.authorSection {
  padding: 3rem 2rem;
  text-align: center;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

[data-theme='dark'] .authorSection {
  background-color: #1c1e21;
  border-top-color: #444;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.authorSection h2 {
  margin-bottom: 1rem;
}

.authorSection p {
  font-size: 1.125rem;
  margin: 0.5rem 0;
}

.authorSection a {
  color: #0066cc;
  text-decoration: underline;
}

.authorSection a:hover {
  color: #0052a3;
}
```

### T030: Create src/pages/index.tsx (custom homepage)
**File**: `src/pages/index.tsx`

```typescript
import React from 'react';
import Layout from '@theme/Layout';
import Hero from '@site/src/components/homepage/Hero';
import Features from '@site/src/components/homepage/Features';
import AuthorSection from '@site/src/components/homepage/AuthorSection';

export default function Home(): JSX.Element {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics Textbook"
      description="Learn to bridge digital intelligence and the physical world through embodied AI">
      <Hero />
      <Features />
      <AuthorSection />
    </Layout>
  );
}
```

### T031: Test homepage
```bash
npm start
```
**Expected**:
- Custom homepage loads with hero, features, author sections
- "Start the Course" button navigates to `/docs/intro`
- Responsive layout on different screen sizes

---

## Phase 7: ChapterActionsBar Component

**Goal**: Create reusable component with "Personalize for Me" and "View in Urdu" buttons

### T032: Create learning components directory
```bash
mkdir -p src/components/learning
```

### T033: Create src/components/learning/ChapterActionsBar.tsx
**File**: `src/components/learning/ChapterActionsBar.tsx`

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

### T034: Create src/components/learning/ChapterActionsBar.module.css
**File**: `src/components/learning/ChapterActionsBar.module.css`

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
  font-weight: 600;
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

/* Mobile: stack vertically at 640px breakpoint */
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

[data-theme='dark'] .modalContent {
  background-color: #2a2a2a;
}

.modalContent h3 {
  margin-top: 0;
}

.modalContent button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #0066cc;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}
```

### T035: Integrate ChapterActionsBar into module MDX files
**Files to edit**: All 8 module content files (4 modules × 2 pages: overview + chapter-1)

**For each file**, add import at top and component after frontmatter:

**Example for `docs/module-1-ros2/overview.mdx`**:
```mdx
---
id: module-1-ros2-overview
title: Module 1 Overview - ROS 2
sidebar_label: Overview
---

import ChapterActionsBar from '@site/src/components/learning/ChapterActionsBar';

<ChapterActionsBar />

# Module 1: ROS 2 – The Robotic Nervous System

[rest of content...]
```

**Apply to**:
- `docs/module-1-ros2/overview.mdx`
- `docs/module-1-ros2/chapter-1-basics.mdx`
- `docs/module-2-digital-twin-gazebo-unity/overview.mdx`
- `docs/module-2-digital-twin-gazebo-unity/chapter-1-simulation-basics.mdx`
- `docs/module-3-nvidia-isaac/overview.mdx`
- `docs/module-3-nvidia-isaac/chapter-1-getting-started.mdx`
- `docs/module-4-vision-language-action/overview.mdx`
- `docs/module-4-vision-language-action/chapter-1-vla-intro.mdx`

**Note**: Do NOT add to `docs/intro.md` (intro is not part of a module)

### T036: Test ChapterActionsBar
```bash
npm start
```
**Expected**:
- Buttons appear on all module content pages (not on intro)
- Buttons horizontal on desktop, vertical on mobile ≤640px
- Clicking buttons shows placeholder modals
- Console logs appear when buttons clicked

---

## Phase 8: RAG Chat Placeholder (Floating Button + Slide-out Panel)

**Goal**: Add "Ask the Textbook" floating button with slide-out chat panel

### T037 [P]: Create src/components/learning/AskTextbookButton.tsx
**File**: `src/components/learning/AskTextbookButton.tsx`

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
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    </button>
  );
}
```

**File**: `src/components/learning/AskTextbookButton.module.css`
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

@media (max-width: 640px) {
  .floatingButton {
    bottom: 1rem;
    right: 1rem;
    width: 50px;
    height: 50px;
  }
}
```

### T038 [P]: Create src/components/learning/ChatSlideoutPanel.tsx
**File**: `src/components/learning/ChatSlideoutPanel.tsx`

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
      <div className={styles.overlay} onClick={onClose} />
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

**File**: `src/components/learning/ChatSlideoutPanel.module.css`
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
  right: -400px;
  width: 400px;
  height: 100%;
  background-color: white;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease-in-out;
  z-index: 1001;
  display: flex;
  flex-direction: column;
}

[data-theme='dark'] .slideoutPanel {
  background-color: #1c1e21;
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

[data-theme='dark'] .header {
  border-bottom-color: #444;
}

.closeButton {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
}

[data-theme='dark'] .closeButton {
  color: #ccc;
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

[data-theme='dark'] .placeholder {
  background-color: #2a2a2a;
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

@media (max-width: 640px) {
  .slideoutPanel {
    width: 100%;
    right: -100%;
  }
}
```

### T039: Create src/pages/chat.tsx (placeholder page)
**File**: `src/pages/chat.tsx`

```typescript
import React from 'react';
import Layout from '@theme/Layout';

export default function Chat(): JSX.Element {
  return (
    <Layout
      title="Study Assistant"
      description="RAG-powered chatbot for the Physical AI textbook">
      <div style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <h1>Study Assistant</h1>
        <p style={{ fontSize: '1.25rem', maxWidth: '600px', margin: '0 auto' }}>
          The RAG-powered chatbot is coming soon. This feature will help you ask questions about the entire textbook and get AI-powered answers.
        </p>
        <p style={{ marginTop: '2rem' }}>
          For now, use the floating "Ask the Textbook" button on any docs page to see the placeholder interface.
        </p>
      </div>
    </Layout>
  );
}
```

### T040: Swizzle Docusaurus Layout to integrate chat globally
```bash
npm run swizzle @docusaurus/theme-classic Layout -- --eject
```
**Expected**: Creates `src/theme/Layout/index.tsx`

### T041: Edit src/theme/Layout/index.tsx to add chat components
**File**: `src/theme/Layout/index.tsx`

Add imports at top:
```typescript
import AskTextbookButton from '@site/src/components/learning/AskTextbookButton';
import ChatSlideoutPanel from '@site/src/components/learning/ChatSlideoutPanel';
import { useState } from 'react';
```

Update component body:
```typescript
export default function LayoutWrapper(props: Props): JSX.Element {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      <Layout {...props} />
      <AskTextbookButton onClick={() => setChatOpen(true)} />
      <ChatSlideoutPanel isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </>
  );
}
```

### T042: Test chat UI
```bash
npm start
```
**Expected**:
- Floating button visible bottom-right on all pages
- Clicking button opens slide-out panel from right
- Panel closable via X, ESC, or clicking overlay
- Panel full width on mobile, 400px on desktop
- /chat page accessible via navbar

---

## Phase 9: Text Selection Detection + Selection-Based Q&A Modal

**Goal**: Implement text selection detection with "Ask about this" button and modal

### T043 [P]: Create src/components/learning/SelectionModal.tsx
**File**: `src/components/learning/SelectionModal.tsx`

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

**File**: `src/components/learning/SelectionModal.module.css`
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
  z-index: 2000;
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

[data-theme='dark'] .modalContent {
  background-color: #1c1e21;
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

[data-theme='dark'] .closeButton {
  color: #ccc;
}

.selectedText {
  background-color: #fff8e1;
  padding: 1rem;
  border-left: 4px solid #ff9500;
  margin: 1rem 0;
  border-radius: 0.25rem;
}

[data-theme='dark'] .selectedText {
  background-color: #3a3000;
}

.selectedText blockquote {
  margin: 0.5rem 0 0 0;
  font-style: italic;
  color: #333;
}

[data-theme='dark'] .selectedText blockquote {
  color: #e3e3e3;
}

.placeholder {
  background-color: #f0f0f0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

[data-theme='dark'] .placeholder {
  background-color: #2a2a2a;
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
  background-color: #ff9500;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: not-allowed;
  opacity: 0.5;
  font-weight: 600;
}
```

### T044 [P]: Create src/components/learning/TextSelectionDetector.tsx
**File**: `src/components/learning/TextSelectionDetector.tsx`

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

**File**: `src/components/learning/TextSelectionDetector.module.css`
```css
.askButton {
  position: absolute;
  background-color: #ff9500;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1500;
  transition: transform 0.2s;
  font-weight: 600;
}

.askButton:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
```

### T045: Integrate TextSelectionDetector into Layout
**File**: `src/theme/Layout/index.tsx`

Add import:
```typescript
import TextSelectionDetector from '@site/src/components/learning/TextSelectionDetector';
```

Update component:
```typescript
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

### T046: Test text selection detection
```bash
npm start
```
**Expected**:
- Select 10+ characters in any docs page → "Ask about this" button appears
- Click button → centered modal opens with selected text
- Modal shows amber color scheme (distinct from blue chat)
- Modal closable via X, ESC, or click outside
- Select < 10 characters → button does NOT appear

---

## Phase 10: Final Testing & Documentation

**Goal**: Comprehensive testing and README documentation

### T047: Update README.md with setup instructions
**File**: `README.md`

Replace or update with:
```markdown
# Physical AI & Humanoid Robotics Textbook

**Authored by Tayyab Aziz**

A Docusaurus-based interactive textbook for learning Physical AI, humanoid robotics, ROS 2, digital twins, NVIDIA Isaac, and vision-language-action models.

## Tech Stack

- **Docusaurus** v3.x (TypeScript, classic preset)
- **React** 18
- **npm** (package manager)
- **Node.js** 18.x or 20.x LTS

## Prerequisites

- Node.js 18.x or 20.x ([Download](https://nodejs.org/))
- npm 9.x or later (included with Node.js)

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/<USERNAME>/physical-ai-humanoid-textbook.git
cd physical-ai-humanoid-textbook
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm start
```

The site will open at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

Output: `build/` directory with static assets

### 5. Serve Production Build Locally

```bash
npm run serve
```

### 6. Deploy to GitHub Pages

```bash
GIT_USER=<USERNAME> npm run deploy
```

## Project Structure

```
physical-ai-humanoid-textbook/
├── docs/                   # Course content (intro + 4 modules)
├── src/
│   ├── components/         # React components
│   │   ├── homepage/       # Homepage sections
│   │   └── learning/       # ChapterActionsBar, chat, selection
│   ├── css/                # Global styles
│   └── pages/              # Custom pages (homepage, /chat)
├── static/                 # Static assets
├── docusaurus.config.ts    # Main configuration
└── sidebars.ts             # Sidebar structure
```

## Features

- ✅ **Docusaurus Textbook Structure** - 4 modules with hierarchical navigation
- 🚧 **RAG Chatbot** - Placeholder UI (backend integration coming soon)
- 🚧 **Personalization** - Placeholder buttons (adaptive content coming soon)
- 🚧 **Urdu Translation** - Placeholder UI (translation feature coming soon)

## Links

- **Deployed Site**: (Add URL after deployment)
- **GitHub Repository**: https://github.com/Psqasim/physical-ai-humanoid-textbook
- **Author GitHub**: https://github.com/Psqasim

## License

[Specify license]
```

### T048: Run full responsive test matrix
Open DevTools and test each breakpoint:
- [ ] 320px (iPhone SE) - no horizontal scroll, vertical button stacking
- [ ] 375px (iPhone 12) - all elements visible
- [ ] 640px - verify button breakpoint (vertical ≤640px, horizontal >640px)
- [ ] 768px (iPad) - sidebar hamburger menu works
- [ ] 1024px - desktop layout looks good
- [ ] 1920px - no excessive stretching

### T049: Run browser compatibility tests
- [ ] Chrome (latest) - all features work
- [ ] Firefox (latest) - all features work
- [ ] Safari (latest) - all features work
- [ ] Edge (latest) - all features work

### T050: Verify all success criteria from spec.md
- [ ] SC-001: `npm install && npm start` completes in < 2 minutes
- [ ] SC-002: Homepage displays hero, features, author; CTA navigates to /docs/intro
- [ ] SC-003: Sidebar shows 4 modules with clean URLs
- [ ] SC-004: Placeholder buttons trigger visible messages (modals + console.log)
- [ ] SC-005: "Ask the Textbook" entry point opens chat placeholder
- [ ] SC-006: Text selection triggers "Ask about this" button and modal
- [ ] SC-007: Blog link NOT visible in navbar
- [ ] SC-008: `npm run build` completes without errors
- [ ] SC-009: Site responsive on 320px and 1920px
- [ ] SC-010: README documents setup clearly

### T051: Run production build test
```bash
npm run build
npm run serve
```
**Expected**:
- Build completes without errors
- All routes work in production build
- No console errors in browser

### T052: Create final commit
```bash
git add .
git status  # Review changes
git commit -m "feat: complete Docusaurus frontend structure

- Initialize Docusaurus v3.x with TypeScript
- Configure navbar, footer, sidebar (4 modules)
- Create docs tree (intro + 4 modules × 2 pages each)
- Implement homepage (Hero, Features, AuthorSection)
- Add ChapterActionsBar with personalization/translation placeholders
- Add RAG chatbot placeholder (floating button + slide-out panel)
- Add text selection detection with selection-based Q&A modal
- Implement responsive design (640px breakpoint)
- All features frontend-only with placeholder messages

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task Summary

**Total Tasks**: 52
**Estimated Time**: 30-40 hours
**Parallelizable Tasks**: 15 marked with [P]

**Execution Strategy**:
1. **MVP Path** (Tasks T001-T031): ~12-16 hours → Navigable textbook with homepage
2. **Placeholder UIs** (Tasks T032-T046): ~15-20 hours → Interactive placeholders
3. **Polish & Deploy** (Tasks T047-T052): ~3-4 hours → Production ready

**Key Milestones**:
- After T022: Docs structure complete (can navigate entire textbook)
- After T031: Homepage complete (can demo landing page)
- After T036: Personalization buttons functional
- After T042: Chat UI complete
- After T046: Selection detection complete
- After T052: Ready for deployment

**WSL-Safe Commands**:
- All npm commands run in WSL environment
- Paths use `/mnt/e/...` for Windows drive access
- File creation uses bash commands where appropriate
- All commands tested for WSL compatibility

**Next Steps After Completion**:
- Deploy to GitHub Pages: `GIT_USER=<USERNAME> npm run deploy`
- Test deployed site at: `https://<USERNAME>.github.io/physical-ai-humanoid-textbook/`
- Begin backend integration feature (FastAPI + RAG)
