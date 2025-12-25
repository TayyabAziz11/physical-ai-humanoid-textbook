---
id: 0001
title: "Fix Missing Frontmatter Dependency"
stage: general
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.implement
labels: ["dependency", "railway", "deployment", "bugfix", "python-frontmatter"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - DEPENDENCY_AUDIT_REPORT.md
tests:
  - Local import verification tests
  - Application startup test
---

## Prompt

```text
You are acting as a senior Python backend + DevOps engineer.

Context:
- FastAPI backend deployed on Railway
- Frontend on GitHub Pages
- Railway deployment is currently failing at startup

Current Railway error:
ModuleNotFoundError: No module named 'frontmatter'

Stack trace shows:
- app/services/parser.py imports `frontmatter`
- This dependency is missing from requirements.txt
- Similar issues already happened with `tiktoken` and config imports

Your tasks (do ALL of them, do not skip anything):

1. Dependency Audit & Fix
   - Scan the entire backend codebase for ALL third-party imports
   - Identify any dependency that is used but missing from requirements.txt
   - Add the correct PyPI packages (with safe pinned versions) to requirements.txt
     - Example: `python-frontmatter` (NOT `frontmatter`)
   - Ensure no unused or incorrect package names are added

2. Fix the Current Error
   - Confirm that the correct package for `import frontmatter` is installed
   - Update requirements.txt accordingly
   - Explain briefly why the error happened

3. Local Verification (MANDATORY)
   - Test all imports work locally
   - Verify application startup succeeds
   - Document the fix for Railway deployment
```

## Response snapshot

### Issue Diagnosed

**Root Cause**: The code imports `frontmatter` in `app/services/parser.py:7` but the PyPI package `python-frontmatter` was missing from `requirements.txt`.

**Why It Happened**:
- Package was installed locally during development
- Not documented in requirements.txt
- Railway builds from clean environment, causing ModuleNotFoundError

### Fix Applied

**File**: `backend/requirements.txt`

**Added Line 16**:
```txt
python-frontmatter==1.0.1
```

**Package Details**:
- **Import**: `import frontmatter`
- **PyPI Package**: `python-frontmatter`
- **Version**: 1.0.1 (latest stable)
- **Purpose**: Parse markdown files with YAML frontmatter (metadata)
- **Used In**: `app/services/parser.py` for textbook markdown parsing

### Dependency Audit Results

**Scanned**: All `*.py` files in backend codebase
**Found**: 12 third-party packages in use

**All Dependencies Accounted For**:
1. ✅ fastapi
2. ✅ uvicorn[standard]
3. ✅ sqlalchemy>=2.0
4. ✅ asyncpg
5. ✅ psycopg2-binary
6. ✅ pydantic>=2.0
7. ✅ pydantic-settings
8. ✅ qdrant-client
9. ✅ openai
10. ✅ python-dotenv
11. ✅ tiktoken==0.4.0
12. ✅ python-frontmatter==1.0.1 (NEWLY ADDED)

**No Additional Missing Dependencies Found**

### Local Verification

All tests passed:
```bash
✅ import frontmatter - Success
✅ from app.services.parser import MarkdownParser - Success
✅ from main import app - Success
✅ Backend startup - Success
```

**Application Logs**:
```
✅ API v1 router included: /api/v1/query/global, /api/v1/query/selection
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Documentation Created

**File**: `DEPENDENCY_AUDIT_REPORT.md`

**Contents**:
- Complete dependency audit results
- Root cause analysis
- Fix details with code examples
- Local verification steps
- Railway deployment instructions
- Dependency management best practices
- Common import-to-package mappings

## Outcome

- ✅ Impact: Fixed critical Railway deployment blocker, backend will now start successfully
- 🧪 Tests: Local import tests passed, application startup verified
- 📁 Files: Updated backend/requirements.txt (1 line added), created DEPENDENCY_AUDIT_REPORT.md
- 🔁 Next prompts: Commit changes and push to trigger Railway deployment
- 🧠 Reflection: This is the third dependency issue (tiktoken, settings, frontmatter). Should implement automated dependency scanning in CI/CD to catch these before deployment.

## Evaluation notes (flywheel)

- Failure modes observed: Missing dependencies not caught before Railway deployment. Local environment had packages installed that weren't in requirements.txt. Pattern of development-time installations not being documented.
- Graders run and results (PASS/FAIL): PASS - All imports verified, application startup successful, comprehensive audit completed
- Prompt variant (if applicable): N/A - Standard implementation request
- Next experiment (smallest change to try): Add pre-commit hook or CI check to scan Python imports and validate against requirements.txt automatically. Example: `pip install pipreqs` and run `pipreqs --savepath requirements-check.txt` in CI, compare with actual requirements.txt
