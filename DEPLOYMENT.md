# Deployment Guide for YUV.AI Trends

This guide covers deploying your AI Tech News Aggregator to production.

---

## Architecture Overview

Your app has **two parts**:
1. **Frontend** (React/Vite) - Static files, easy to deploy anywhere
2. **Backend** (Python FastAPI) - Needs a server that runs Python

**Key insight**: Vercel is great for frontend, but for the Python backend you need a different approach.

---

## 🚀 Recommended: Split Deployment

### Option A: Vercel (Frontend) + Railway (Backend)

This is the **recommended approach** for production.

#### Step 1: Deploy Backend to Railway

[Railway](https://railway.app) is perfect for Python backends (free tier available).

1. **Create Railway account** at https://railway.app

2. **Create `Procfile`** in your project root:
```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

3. **Create `railway.json`**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

4. **Push to Railway**:
   - Connect your GitHub repo
   - Railway auto-detects Python and deploys
   - Note your backend URL: `https://your-app.railway.app`

5. **Set environment variables in Railway dashboard**:
   ```
   LLM_PROVIDER=local_wasm
   ANTHROPIC_API_KEY=    (leave empty, users add their own)
   COHERE_API_KEY=       (leave empty)
   GROQ_API_KEY=         (leave empty)
   ```

#### Step 2: Deploy Frontend to Vercel

1. **Update API URL in frontend** - Create `ui/.env.production`:
   ```
   VITE_API_URL=https://your-app.railway.app
   ```

2. **Update `ui/src/App.jsx`** to use environment variable:
   ```javascript
   const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   
   // Then replace all 'http://localhost:8000' with API_URL
   ```

3. **Create Vercel project**:
   - Go to https://vercel.com/new
   - Import your GitHub repo
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `ui`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`

4. **Set Vercel environment variables**:
   ```
   VITE_API_URL=https://your-app.railway.app
   ```

---

### Option B: Vercel Serverless Functions (Frontend + Backend)

Convert your FastAPI to Vercel serverless functions. **More complex but single platform.**

#### Step 1: Restructure for Vercel

1. **Create `api/` folder in project root** (not `ui/api`):
   ```
   news/
   ├── api/
   │   ├── generate.py      <- /api/generate endpoint
   │   ├── settings.py      <- /api/settings endpoint
   │   └── ...
   ├── ui/
   │   └── ...
   └── vercel.json
   ```

2. **Create `vercel.json`** in project root:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "ui/package.json",
         "use": "@vercel/static-build",
         "config": { "distDir": "dist" }
       },
       {
         "src": "api/*.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       { "src": "/api/(.*)", "dest": "/api/$1" },
       { "src": "/(.*)", "dest": "/ui/$1" }
     ]
   }
   ```

3. **Convert endpoints to serverless** - Example `api/generate.py`:
   ```python
   from http.server import BaseHTTPRequestHandler
   import json
   
   # Import your existing logic
   from fetchers import GitHubTrendingFetcher, HuggingFaceFetcher
   from ranker import ContentRanker
   
   class handler(BaseHTTPRequestHandler):
       def do_POST(self):
           content_length = int(self.headers['Content-Length'])
           body = json.loads(self.rfile.read(content_length))
           
           # Your existing generate logic here...
           
           self.send_response(200)
           self.send_header('Content-type', 'application/json')
           self.end_headers()
           self.wfile.write(json.dumps(result).encode())
   ```

**⚠️ Limitations of Vercel Serverless:**
- 10 second timeout on free tier (your scraping may exceed this)
- No persistent file storage (can't save `.env` or cache files)
- Cold starts can be slow

---

## 🔐 Environment Variables

### For Backend (Railway/Render/Fly.io)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LLM_PROVIDER` | Default AI provider | No | `local_wasm` |
| `LLM_MODEL` | Default model ID | No | (auto-selected) |
| `ANTHROPIC_API_KEY` | Anthropic API key | No | (empty) |
| `COHERE_API_KEY` | Cohere API key | No | (empty) |
| `GROQ_API_KEY` | Groq API key | No | (empty) |

### For Frontend (Vercel)

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Yes |

---

## 📝 User API Keys Strategy

Since users should be able to add their own API keys, you have two approaches:

### Approach 1: Server-Side Storage (Current)
- API keys stored in `.env` file on server
- All users share the same keys
- **Issue**: Not ideal for multi-tenant SaaS

### Approach 2: Client-Side Storage (Recommended for Public Deploy)

Update the app to store API keys in browser localStorage:

1. **Frontend stores keys** in localStorage
2. **Frontend sends keys** with each API request
3. **Backend uses per-request keys** instead of `.env`

This way each user manages their own keys privately in their browser.

---

## 🎯 Quick Deploy: Single Click Options

### Deploy to Railway (Backend Only)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

### Deploy to Render (Backend Only)

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: yuv-ai-trends-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: LLM_PROVIDER
        value: local_wasm
```

### Deploy to Fly.io (Backend Only)

1. Install Fly CLI: `irm https://fly.io/install.ps1 | iex`
2. Run: `fly launch`
3. Deploy: `fly deploy`

---

## 🛠️ Step-by-Step: Full Vercel + Railway Deploy

### Prerequisites
- GitHub account with your repo
- Vercel account (free)
- Railway account (free)

### 1. Prepare Your Code

First, make the frontend configurable for production:

**Update `ui/src/App.jsx`:**
```javascript
// At the top of the file
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Replace all instances of 'http://localhost:8000' with API_URL
```

**Create `ui/.env.production`:**
```
VITE_API_URL=https://your-backend.railway.app
```

### 2. Deploy Backend to Railway

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your `yuv-ai-trends` repo
4. Railway detects Python automatically
5. Go to Settings → Variables → Add:
   - `LLM_PROVIDER` = `local_wasm`
6. Copy your Railway URL (e.g., `https://yuv-ai-trends-production.up.railway.app`)

### 3. Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Configure build settings:
   - **Root Directory**: `ui`
   - **Framework**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable:
   - `VITE_API_URL` = `https://your-backend.railway.app`
5. Click Deploy

### 4. Configure CORS

Update `api.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",
        "https://*.vercel.app"  # All Vercel preview deploys
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔧 Troubleshooting

### "CORS Error" in browser
- Make sure your backend CORS settings include your Vercel domain
- Check that `VITE_API_URL` is set correctly (no trailing slash)

### "504 Gateway Timeout"
- Your backend is taking too long (scraping is slow)
- Solution: Add caching, reduce number of sources

### "API Key not persisting"
- Serverless functions don't have persistent storage
- Solution: Use Railway/Render for backend, or implement client-side key storage

### "Module not found" on Vercel
- Python serverless needs all files in the `api/` folder
- Move your Python modules or adjust imports

---

## 📊 Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| **Vercel** | 100GB bandwidth | Frontend hosting |
| **Railway** | $5/month credit | Python backend |
| **Render** | 750 hours/month | Python backend |
| **Fly.io** | 3 VMs free | Docker containers |

---

## 🎉 Summary

**Easiest path to production:**

1. Deploy backend to **Railway** (free)
2. Deploy frontend to **Vercel** (free)
3. Set `VITE_API_URL` in Vercel to your Railway URL
4. Update CORS in `api.py` to allow Vercel domain
5. Users select `Local Web LLM` or add their own API keys in Settings

Total cost: **$0** (within free tiers)

---

## Need Help?

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Open an issue: https://github.com/hoodini/yuv-ai-trends/issues
