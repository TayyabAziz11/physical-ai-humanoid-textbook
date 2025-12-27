# Deployment Guide

This guide covers deploying the Physical AI Humanoid Textbook to production.

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                       │
│                                                             │
│  ┌──────────────┐              ┌──────────────┐           │
│  │   Backend    │              │   Frontend   │           │
│  │  (FastAPI)   │              │ (Docusaurus) │           │
│  └──────┬───────┘              └──────┬───────┘           │
│         │                             │                    │
└─────────┼─────────────────────────────┼────────────────────┘
          │                             │
          │ Push to main                │ npm run deploy
          ↓                             ↓
┌─────────────────┐          ┌─────────────────────┐
│                 │          │                     │
│     Railway     │          │   GitHub Pages      │
│                 │          │                     │
│  Auto-deploys   │          │  Static site host   │
│  from main      │          │  gh-pages branch    │
│                 │          │                     │
└─────────────────┘          └─────────────────────┘
          │                             │
          │ Backend API                 │ Website
          ↓                             ↓
┌─────────────────────────────────────────────────────────────┐
│                          Users                              │
│  Website: https://[user].github.io/physical-ai-humanoid-   │
│           textbook/                                         │
│  API: https://physical-ai-humanoid-textbook-production.    │
│       up.railway.app                                        │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- GitHub account with repository access
- Railway account (for backend)
- OpenAI API key
- Node.js 18+ installed locally
- Python 3.11+ installed locally

## Backend Deployment (Railway)

### Initial Setup

1. **Create Railway Project**
   ```bash
   # Install Railway CLI (if needed)
   npm install -g @railway/cli

   # Login to Railway
   railway login

   # Link project (from repo root)
   railway link
   ```

2. **Configure Environment Variables**

   In Railway dashboard, add:
   ```
   OPENAI_API_KEY=sk-...
   PORT=8000
   ```

3. **Configure Build Settings**

   Railway auto-detects Python. Verify:
   - **Root Directory**: `backend/`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Deployment Process

Railway automatically deploys on push to `main` branch.

**Manual Deploy**:
```bash
# From repo root
railway up
```

### Verify Deployment

1. **Health Check**
   ```bash
   curl https://[your-project].up.railway.app/health
   ```

   Should return: `{"status": "healthy"}`

2. **API Documentation**

   Visit: `https://[your-project].up.railway.app/docs`

3. **Test Translation Endpoint**
   ```bash
   curl -X POST https://[your-project].up.railway.app/api/v1/translate/text \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello world",
       "target_language": "spanish"
     }'
   ```

### Production Configuration

**File**: `backend/app/main.py`

Ensure CORS is configured correctly:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://[your-user].github.io",  # GitHub Pages
        "http://localhost:3000",          # Local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Frontend Deployment (GitHub Pages)

### Configuration

**File**: `docusaurus.config.js`

Update these fields:
```javascript
const config = {
  // GitHub Pages configuration
  url: 'https://[your-username].github.io',
  baseUrl: '/physical-ai-humanoid-textbook/',

  // Organization/user pages use different baseUrl:
  // For [username].github.io: baseUrl: '/'
  // For [username].github.io/repo: baseUrl: '/repo/'

  organizationName: '[your-username]',
  projectName: 'physical-ai-humanoid-textbook',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,
};
```

### Build for Production

```bash
# Clean previous builds
rm -rf build/

# Build production bundle
npm run build
```

**Verify Build**:
```bash
# Serve production build locally
npm run serve
```

Visit `http://localhost:3000` and test:
- Translation feature works
- All pages load correctly
- No console errors
- Dark mode switches correctly

### Deploy to GitHub Pages

```bash
# Deploy to gh-pages branch
npm run deploy
```

This command:
1. Builds the production bundle
2. Pushes to `gh-pages` branch
3. GitHub Pages auto-deploys from that branch

### Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Set **Source** to `gh-pages` branch
3. Click **Save**
4. Wait 1-2 minutes for deployment

### Verify Deployment

Visit: `https://[your-username].github.io/physical-ai-humanoid-textbook/`

**Checklist**:
- [ ] Homepage loads
- [ ] Navigation works
- [ ] Search works
- [ ] Translation feature appears on text selection
- [ ] Language selector shows all 7 languages
- [ ] Translation modal displays correctly
- [ ] RTL languages (Arabic, Urdu) render right-to-left
- [ ] Dark mode works
- [ ] Mobile responsive
- [ ] Chatbot opens and works

## Environment Variables

### Backend (Railway)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API key for GPT-4o-mini |
| `PORT` | No | 8000 | Port for FastAPI server |
| `BACKEND_URL` | No | - | Backend URL for CORS (optional) |

### Frontend (Optional)

Set custom backend URL in `docusaurus.config.js`:

```javascript
customFields: {
  translationAPIBaseURL: 'https://your-custom-backend.com',
},
```

Or via window object in `src/theme/Root.tsx`:
```typescript
if (typeof window !== 'undefined') {
  (window as any).__TRANSLATION_API_BASE_URL__ = 'https://your-backend.com';
}
```

## Troubleshooting

### Backend Issues

**Problem**: Railway build fails

**Solutions**:
- Check `requirements.txt` is up to date
- Verify Python version in `runtime.txt` (if present)
- Check Railway build logs for specific errors

**Problem**: API returns 500 errors

**Solutions**:
- Check Railway logs for error details
- Verify `OPENAI_API_KEY` is set correctly
- Test OpenAI key locally first

**Problem**: CORS errors in browser

**Solutions**:
- Add frontend URL to `allow_origins` in `backend/app/main.py`
- Redeploy backend after CORS changes
- Clear browser cache and retry

### Frontend Issues

**Problem**: GitHub Pages shows 404

**Solutions**:
- Verify `baseUrl` matches repository name
- Check `gh-pages` branch exists and has content
- Wait 2-3 minutes for GitHub Pages to update
- Check GitHub Actions for deployment status

**Problem**: Translation feature not working in production

**Solutions**:
- Open browser DevTools → Network tab
- Check if API requests are reaching backend
- Verify backend URL is correct
- Check for CORS errors in console

**Problem**: Assets not loading (images, CSS)

**Solutions**:
- Verify `baseUrl` is correct in `docusaurus.config.js`
- Check asset paths are relative, not absolute
- Rebuild and redeploy

## Custom Domain (Optional)

### GitHub Pages Custom Domain

1. Buy domain from provider (e.g., Namecheap, Google Domains)

2. Add DNS records:
   ```
   Type: A
   Host: @
   Value: 185.199.108.153
   Value: 185.199.109.153
   Value: 185.199.110.153
   Value: 185.199.111.153

   Type: CNAME
   Host: www
   Value: [your-username].github.io
   ```

3. In repository, create file `static/CNAME`:
   ```
   your-domain.com
   ```

4. In GitHub Settings → Pages, add custom domain

5. Update `docusaurus.config.js`:
   ```javascript
   url: 'https://your-domain.com',
   baseUrl: '/',
   ```

### Railway Custom Domain

1. In Railway dashboard, go to project Settings → Domains
2. Click **Add Custom Domain**
3. Enter your domain (e.g., `api.your-domain.com`)
4. Add CNAME record to DNS:
   ```
   Type: CNAME
   Host: api
   Value: [your-project].up.railway.app
   ```

5. Update frontend to use new backend URL

## Monitoring

### Backend Health

**Health Check Endpoint**: `GET /health`

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T12:00:00Z"
}
```

**Railway Monitoring**:
- CPU usage
- Memory usage
- Response times
- Error rates

**Alerts** (Railway Pro):
- Set up alerts for high error rates
- Monitor API response times

### Frontend Monitoring

**Google Analytics** (optional):

Add to `docusaurus.config.js`:
```javascript
themeConfig: {
  gtag: {
    trackingID: 'G-XXXXXXXXXX',
  },
},
```

**Metrics to Track**:
- Page views
- Translation usage (via analytics events)
- Error rates
- Geographic distribution

## Rollback Procedure

### Backend Rollback (Railway)

1. Go to Railway dashboard
2. Click on deployment history
3. Select previous working deployment
4. Click **Redeploy**

**Or via CLI**:
```bash
railway rollback
```

### Frontend Rollback (GitHub Pages)

```bash
# Check out previous version
git checkout <previous-commit-hash>

# Redeploy
npm run deploy

# Or reset gh-pages branch
git checkout gh-pages
git reset --hard <previous-commit-hash>
git push --force
```

## Performance Optimization

### Backend

**Current Setup**:
- Async I/O (FastAPI)
- In-memory rate limiting
- Retry logic with backoff

**Future Optimizations**:
- Redis for distributed rate limiting
- CDN for API responses
- Database connection pooling (if needed)

### Frontend

**Current Setup**:
- Static site generation (Docusaurus)
- Code splitting
- CSS minification
- Image optimization

**Future Optimizations**:
- Lazy loading for translation components
- Service worker for offline support
- Brotli compression

## Security Best Practices

### Backend

- ✅ API key stored in environment variables
- ✅ Rate limiting enabled (10 req/min/IP)
- ✅ CORS configured for specific origins
- ✅ HTTPS enforced by Railway
- ✅ No sensitive data logging

### Frontend

- ✅ Static site (no server-side code)
- ✅ HTTPS enforced by GitHub Pages
- ✅ No hardcoded secrets
- ✅ XSS protection via React

## CI/CD (Optional)

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest
```

## Maintenance

### Regular Tasks

**Weekly**:
- Check Railway logs for errors
- Monitor translation usage/costs
- Review GitHub Issues

**Monthly**:
- Update dependencies (`npm outdated`, `pip list --outdated`)
- Review and rotate API keys if needed
- Check for security updates

**Quarterly**:
- Review and optimize costs
- Update documentation
- Plan new features

## Cost Management

### OpenAI API Costs

**Current Usage** (estimated):
- Model: GPT-4o-mini ($0.15 / 1M input tokens, $0.60 / 1M output tokens)
- Average translation: ~150 input + 150 output tokens
- Cost per translation: ~$0.0001

**Monthly Estimates**:
- 1,000 translations: ~$0.10
- 10,000 translations: ~$1.00
- 100,000 translations: ~$10.00

**Rate Limiting** (10 req/min) helps control costs:
- Max requests/day: 14,400
- Max cost/day: ~$1.44

### Railway Costs

- **Hobby Plan**: $5/month (500 hours)
- **Pro Plan**: $20/month + usage

### GitHub Pages

- **Free** for public repositories
- Bandwidth: 100GB/month
- Build time: Unlimited

---

**Ready to Deploy!**

Follow the steps above to get your Physical AI Humanoid Textbook live in production. 🚀
