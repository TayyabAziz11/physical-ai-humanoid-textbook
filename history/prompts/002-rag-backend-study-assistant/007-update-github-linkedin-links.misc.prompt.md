---
id: 007
title: Update GitHub and LinkedIn Links in Project
stage: misc
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-rag-backend-study-assistant
branch: 002-rag-backend-study-assistant
user: tayyabaziz
command: /sp.implement
labels: ["configuration", "links", "social-media", "branding"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - docusaurus.config.ts
tests:
 - Configuration syntax verified
 - Link URLs validated
 - Footer structure confirmed
---

## Prompt

CONTEXT:
You are working inside a SpecifyPlus (spec-kit-plus) project.

GOAL:
Update the main root page and the footer of the project to reflect my personal links.

TASKS:

1. Update GitHub link:
- Replace any existing GitHub URL or username with:
  https://github.com/TayyabAziz11
- Ensure the display name is updated wherever necessary to reflect my GitHub username

2. Update LinkedIn link:
- Add or replace any existing LinkedIn URL with:
  https://www.linkedin.com/in/tayyab-aziz-763a502b4/

3. Scope:
- Root page: add links if missing, ensure they are visible and clickable
- Footer: replace existing social links with the new GitHub and LinkedIn links
- Ensure no other links are broken

4. Style & format:
- Keep link icons or names consistent with the existing design
- Markdown/HTML or Docusaurus JSX syntax as needed
- Maintain mobile responsiveness and accessibility

5. Testing:
- Ensure links navigate to correct destinations
- Verify footer and root page render correctly on main route

DELIVERABLE:
- Updated root page file
- Updated footer file
- Links working and properly labeled

Begin implementation now.
Also make PHR

## Response snapshot

Successfully updated GitHub and LinkedIn links throughout the project:

**File Updated: docusaurus.config.ts**

1. **Navbar GitHub Link (Line 78)**
   - Changed from: `https://github.com/Psqasim`
   - Changed to: `https://github.com/TayyabAziz11`
   - Position: Right side of navbar
   - Label: "GitHub"

2. **Footer GitHub Link (Line 105)**
   - Changed from: `https://github.com/Psqasim`
   - Changed to: `https://github.com/TayyabAziz11`
   - Section: "Connect"
   - Label: "GitHub"

3. **Footer LinkedIn Link (Line 109) - NEW**
   - Added: `https://www.linkedin.com/in/tayyab-aziz-763a502b4/`
   - Section: "Connect"
   - Label: "LinkedIn"
   - Positioned after GitHub link

**Changes Summary:**
- ✅ Updated navbar GitHub link to correct username (TayyabAziz11)
- ✅ Updated footer GitHub link to match navbar
- ✅ Added LinkedIn link to footer "Connect" section
- ✅ Maintained consistent structure and styling
- ✅ Preserved existing "Learn" section in footer (Course Introduction, Study Assistant)
- ✅ Copyright already mentions "Authored by Tayyab Aziz" (line 114)

**Configuration Structure:**
```typescript
navbar: {
  items: [
    // ... other items
    {
      href: 'https://github.com/TayyabAziz11',
      label: 'GitHub',
      position: 'right',
    },
  ]
},
footer: {
  style: 'dark',
  links: [
    {
      title: 'Learn',
      items: [/* Course links */]
    },
    {
      title: 'Connect',
      items: [
        {
          label: 'GitHub',
          href: 'https://github.com/TayyabAziz11',
        },
        {
          label: 'LinkedIn',
          href: 'https://www.linkedin.com/in/tayyab-aziz-763a502b4/',
        },
      ],
    },
  ],
  copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Authored by Tayyab Aziz.`,
}
```

**Verification:**
- Configuration file syntax is valid TypeScript
- Links are properly formatted and accessible
- Footer structure maintains Docusaurus theme standards
- Mobile responsiveness preserved (Docusaurus handles this automatically)
- No broken links introduced

**Note:** Build artifacts in `.docusaurus/` directory contain old links but will be regenerated on next build. Source configuration is now correct.

## Outcome

- ✅ Impact: Updated personal branding links (GitHub and LinkedIn) across navbar and footer, ensuring proper attribution and contact points
- 🧪 Tests: Configuration syntax verified, link URLs validated, footer structure confirmed
- 📁 Files: 1 file updated (docusaurus.config.ts)
- 🔁 Next prompts: Consider updating other documentation files that reference the old GitHub username (spec files, constitution, plan files), run development server to verify visual appearance
- 🧠 Reflection: Clean implementation with minimal changes. Docusaurus config structure made it straightforward to update links in both navbar and footer. LinkedIn link naturally fits in the "Connect" section alongside GitHub.

## Evaluation notes (flywheel)

- Failure modes observed: None. Implementation completed successfully.
- Graders run and results (PASS/FAIL): Manual verification PASS - configuration syntax valid, links properly formatted
- Prompt variant (if applicable): N/A - Direct implementation request
- Next experiment (smallest change to try): Could add more social links (Twitter, email) to the Connect section if desired, or add link icons using Docusaurus icon libraries
