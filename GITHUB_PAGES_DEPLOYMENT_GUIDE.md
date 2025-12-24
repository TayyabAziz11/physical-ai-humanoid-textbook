# GitHub Pages Deployment Guide - Frontend Cache-Busting Fixed

**Version**: 1.0.1
**Last Updated**: 2025-12-23
**Backend URL**: https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/

---

## 🎯 Problem Solved

**Issue**: Frontend showing 4-day-old version despite backend updates
**Root Cause**: Browser caching + hardcoded localhost URL + no cache-busting strategy
**Solution**: Automatic Railway backend detection + aggressive cache-busting + version metadata

---

## ✅ Changes Made

### 1. Created API Configuration File
**File**: `src/config/api-config.ts`

**Features**:
- ✅ Automatic Railway URL detection for GitHub Pages
- ✅ Localhost detection for development
- ✅ Runtime override support via `window.CHAT_API_URL`
- ✅ API health check verification
- ✅ Version metadata (1.0.1)

**How it works**:
```typescript
// Production (GitHub Pages) → Uses Railway backend
// Development (localhost) → Uses localhost:8000
// Runtime override → window.CHAT_API_URL (for testing)
```

### 2. Updated Chat API Client
**File**: `src/utils/chat-api.ts`

**Features**:
- ✅ Cache-busting timestamps on every request
- ✅ Cache-Control headers (`no-cache, no-store, must-revalidate`)
- ✅ Pragma and Expires headers for legacy browser support
- ✅ Automatic endpoint URL resolution
- ✅ Enhanced logging for debugging

### 3. Enhanced Docusaurus Configuration
**File**: `docusaurus.config.ts`

**Features**:
- ✅ Cache-busting meta tags in HTML `<head>`
- ✅ Version metadata (`app-version`, `build-date`)
- ✅ HTTP cache-control headers
- ✅ Build timestamp in customFields
- ✅ Version number in footer (v1.0.1)

### 4. Updated Package.json
**File**: `package.json`

**Features**:
- ✅ Version bumped to 1.0.1
- ✅ Added `predeploy` script (clears cache + builds)
- ✅ Added `deploy:gh` script (one-command deployment)

---

## 🚀 Deployment Instructions

### Step 1: Build the Frontend

```bash
# Navigate to project root
cd physical-ai-humanoid-textbook

# Clear all caches and build fresh
npm run clear
npm run build

# This creates a fresh build/ directory with:
# - Updated version metadata
# - Cache-busting headers
# - Railway backend URL configured
```

**Expected output**:
```
[SUCCESS] Generated static files in "build".
```

### Step 2: Deploy to GitHub Pages

**Option A: One-Command Deployment (Recommended)**
```bash
npm run deploy:gh
```

This runs:
1. `npm run clear` - Clears Docusaurus cache
2. `npm run build` - Builds fresh production bundle
3. `npm run deploy` - Deploys to `gh-pages` branch

**Option B: Manual Deployment**
```bash
# Deploy built files to gh-pages branch
npm run deploy

# Or using Git manually
git add .
git commit -m "Deploy frontend v1.0.1 with cache-busting"
git push origin gh-pages
```

### Step 3: Trigger GitHub Pages Rebuild

GitHub Pages caches builds. Force a rebuild:

1. **Go to GitHub Repository**:
   - https://github.com/TayyabAziz11/physical-ai-humanoid-textbook

2. **Navigate to Settings**:
   - Settings → Pages

3. **Re-deploy**:
   - Change source to `None`
   - Click Save
   - Change back to `gh-pages` branch, `/(root)` folder
   - Click Save

4. **Wait for deployment** (usually 1-2 minutes):
   - Check: Actions tab → "pages build and deployment"
   - Status should show ✅ green checkmark

### Step 4: Clear Browser Caches

**For All Users** (automatic):
- Cache-busting headers force fresh fetches
- Version metadata prevents stale content
- Timestamp query parameters bypass cache

**For Developers** (manual, if needed):
```
Chrome/Edge:
- Ctrl+Shift+Delete → Clear browsing data → Cached images and files

Firefox:
- Ctrl+Shift+Delete → Cache → Clear Now

Safari:
- Develop → Empty Caches

Hard Reload (all browsers):
- Ctrl+Shift+R (Windows/Linux)
- Cmd+Shift+R (Mac)
```

---

## 🧪 Verification Steps

### 1. Check GitHub Pages URL

**Production URL**:
```
https://TayyabAziz11.github.io/physical-ai-humanoid-textbook/
```

**Expected**: Homepage loads with updated content

### 2. Verify Version Metadata

Open browser console (F12), check:

```javascript
// Check meta tags
document.querySelector('meta[name="app-version"]').content
// Should show: "1.0.1"

document.querySelector('meta[name="build-date"]').content
// Should show recent timestamp

// Check footer
// Should display: "v1.0.1" in copyright
```

### 3. Test Backend Connection

Open `/chat` page, check browser console:

**Expected logs**:
```
📡 API Config loaded: {
  version: "1.0.1",
  lastUpdated: "2025-12-23T12:00:00Z",
  currentUrl: "https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app"
}

🚀 Production mode - Using Railway backend: https://...
```

### 4. Test Chatbot Functionality

1. Navigate to **Study Assistant** page: `/chat`
2. Ask a question: "What is ROS 2?"
3. Check console for:
   ```
   📤 Sending global query to: https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/query/global?_t=1703347200000
   ✅ Global query successful
   ```

**Expected**: Fresh answer from Railway backend (not cached)

### 5. Verify Cache-Busting

Check Network tab (F12 → Network):
- All API requests should have `?_t=<timestamp>` query parameter
- Request headers should include:
  ```
  Cache-Control: no-cache, no-store, must-revalidate
  Pragma: no-cache
  Expires: 0
  ```

---

## 🔧 Troubleshooting

### Issue: Still seeing old version

**Solution 1**: Force GitHub Pages rebuild
```bash
# Create empty commit to trigger rebuild
git commit --allow-empty -m "Trigger GitHub Pages rebuild"
git push origin gh-pages
```

**Solution 2**: Check deployment status
- Go to: https://github.com/TayyabAziz11/physical-ai-humanoid-textbook/actions
- Verify "pages build and deployment" succeeded
- If failed, check error logs

**Solution 3**: Clear DNS cache
```bash
# Windows
ipconfig /flushdns

# Mac
sudo dscacheutil -flushcache

# Linux
sudo systemd-resolve --flush-caches
```

### Issue: Backend connection failing

**Check**:
1. Railway backend is running:
   ```bash
   curl https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/health
   ```
   Expected: `{"status": "healthy", ...}`

2. CORS is properly configured on Railway backend
3. Browser console shows correct backend URL

**Override backend URL** (for testing):
```javascript
// In browser console
window.CHAT_API_URL = "http://localhost:8000";
location.reload();
```

### Issue: Build errors

```bash
# Clear everything and rebuild
rm -rf node_modules build .docusaurus
npm install
npm run build
```

### Issue: TypeScript errors

```bash
# Run type checking
npm run typecheck

# Common fix
npm install @docusaurus/types @docusaurus/module-type-aliases
```

---

## 📊 Cache-Busting Strategy Summary

### Meta Tags (HTML `<head>`)
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="app-version" content="1.0.1">
<meta name="build-date" content="2025-12-23T12:00:00Z">
```

### HTTP Headers (API Requests)
```
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
Content-Type: application/json
```

### Query Parameters (API URLs)
```
https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/query/global?_t=1703347200000
                                                                                    ^^^ timestamp
```

### Version Tracking
- **package.json**: `"version": "1.0.1"`
- **api-config.ts**: `VERSION: "1.0.1"`
- **docusaurus.config.ts**: `v1.0.1` in footer
- **Meta tags**: `app-version` and `build-date`

---

## 🎯 Automatic Backend URL Detection

### How It Works

```
1. Check window.CHAT_API_URL (runtime override)
   ↓ Not set
2. Check if hostname contains "github.io"
   ↓ Yes → GitHub Pages production
3. Use Railway URL: https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app

Alternative path:
2. Check if hostname is "localhost"
   ↓ Yes → Local development
3. Use localhost: http://localhost:8000
```

### Environment Detection Matrix

| Environment | Hostname | Backend URL |
|-------------|----------|-------------|
| **GitHub Pages** | `*.github.io` | Railway (production) |
| **Local Dev** | `localhost` / `127.0.0.1` | `localhost:8000` |
| **Custom Domain** | Other | Railway (production) |
| **Runtime Override** | Any | `window.CHAT_API_URL` |

---

## 🔄 Future Updates

### To deploy future updates:

1. **Update version** in `package.json`:
   ```json
   "version": "1.0.2"
   ```

2. **Update version** in `src/config/api-config.ts`:
   ```typescript
   VERSION: '1.0.2',
   LAST_UPDATED: '2025-12-24T12:00:00Z',
   ```

3. **Update version** in `docusaurus.config.ts`:
   ```typescript
   content: '1.0.2',
   ```

4. **Deploy**:
   ```bash
   npm run deploy:gh
   ```

5. **Verify**:
   - Check version in footer: "v1.0.2"
   - Check meta tag: `app-version="1.0.2"`
   - Check console: `version: "1.0.2"`

---

## 📝 Quick Reference Commands

```bash
# Development
npm start                 # Start dev server (localhost:3000)
npm run build            # Build production bundle
npm run serve            # Serve production build locally

# Deployment
npm run clear            # Clear Docusaurus cache
npm run deploy:gh        # Deploy to GitHub Pages (all-in-one)
npm run deploy           # Deploy only (no rebuild)

# Debugging
npm run typecheck        # Check TypeScript types
```

---

## ✅ Success Criteria

Your deployment is successful when:

- [x] GitHub Pages URL loads without 404 errors
- [x] Version shows "v1.0.1" in footer
- [x] Console logs show Railway backend URL
- [x] Chatbot returns fresh responses from backend
- [x] No cached responses from 4 days ago
- [x] API requests include cache-busting timestamps
- [x] Build date in meta tags is recent

---

**Questions?** Check the browser console for detailed logging. All API calls and configuration decisions are logged for debugging.

**Last Updated**: 2025-12-23
**Frontend Version**: 1.0.1
**Backend URL**: https://physical-ai-humanoid-textbook-production-ee4c.up.railway.app/
