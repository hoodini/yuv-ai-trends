# 🤖 YUV.AI Developers AI Trends

> **Your personal AI news assistant - get the latest AI/ML trends with smart summaries, no API key required!**

A privacy-first news aggregator that fetches trending AI content from GitHub and Hugging Face, then explains what each project does using AI. Works out-of-the-box with a built-in local summarizer, or connect your favorite AI provider for enhanced summaries.

**🔒 Privacy First**: All your settings and API keys are stored locally in your browser - never on any server!

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![AI-Powered](https://img.shields.io/badge/AI-Powered-purple.svg)

---

## 📋 Release Notes (v2.2.0 - RSS & Automation Ready)

### 🆕 What's New

- **📡 RSS Feed Support** - Full RSS 2.0 and JSON Feed endpoints for automation tools
- **🔄 Make.com Integration** - Built-in RSS triggers for automated content workflows
- **💾 Persistent RSS Store** - Tracks discovery timestamps for proper "new item" detection
- **❤️ Health Endpoints** - Keep-alive endpoints for Render free tier (`/health`, `/ping`)
- **🚀 GitHub Pages + Render** - Optimized split deployment architecture
- **🔒 Browser-Based Storage** - API keys stored in localStorage, never on server
- **No Database Required** - Fully stateless backend, perfect for serverless
- **No API Key Required!** - `local_wasm` mode generates summaries without any external API
- **4 AI Providers** - Choose from Local, Groq (free), Cohere, or Anthropic Claude
- **Smart Caching** - Summaries cached locally, auto-cleans invalid entries

### 🏗️ Architecture Changes

- GitHub Pages for static frontend + Render for Python backend
- RSS feed with persistent store for automation tools
- API keys sent per-request from browser (not stored on server)
- Removed server-side settings management
- Added `/api/validate-key` endpoint for key verification
- Added health/keep-alive endpoints for free tier hosting
- Frontend uses localStorage for all user preferences

---

## 📡 RSS Feed & Make.com Integration

### RSS Endpoints

| Endpoint | Format | Description |
|----------|--------|-------------|
| `/rss.xml` | RSS 2.0 | Standard RSS feed for most readers |
| `/feed.json` | JSON Feed | JSON format for programmatic access |
| `/api/rss/stats` | JSON | Feed statistics and item counts |
| `/api/rss/refresh` | POST | Force refresh RSS items |
| `/api/rss/clear` | POST | Clear all stored RSS items |

### Query Parameters

```
?time_range=daily    # daily, weekly, or monthly
?limit=50            # Max items to return (default: 50)
```

### Example URLs

```bash
# Daily RSS feed
https://your-api.onrender.com/rss.xml?time_range=daily

# Weekly JSON feed with 20 items
https://your-api.onrender.com/feed.json?time_range=weekly&limit=20
```

### Make.com Integration

Perfect for automated content workflows! Use the RSS trigger to detect new AI trends:

#### Step 1: Create RSS Trigger
1. Add **RSS** module → "Watch RSS feed items"
2. URL: `https://your-api.onrender.com/rss.xml?time_range=daily`
3. Set schedule (e.g., every 6 hours)

#### Step 2: Field Mapping

The RSS feed provides clean fields for your templates:

| Make.com Variable | Field | Example |
|-------------------|-------|---------|
| `{{1.title}}` | Item title | "microsoft/autogen - Multi-Agent Conversation Framework" |
| `{{1.url}}` | Direct URL | "https://github.com/microsoft/autogen" |
| `{{1.description}}` | Clean description | "Enable next-gen LLM applications with multi-agent conversation" |
| `{{1.pubDate}}` | Discovery timestamp | "2026-01-04T12:30:00Z" |
| `{{1.category}}` | Source category | "GitHub Trending" / "HuggingFace Papers" |
| `{{1.guid}}` | Unique ID | "github_microsoft_autogen" |

#### Step 3: Example Workflow

```
RSS Trigger → Filter (score > 50) → OpenAI (expand summary) → Discord/Slack/Email
```

#### Content Generation Template

Use these fields in your Make.com HTTP/AI modules:

```
New AI Trend: {{1.title}}

{{1.description}}

Source: {{1.category}}
Link: {{1.url}}
```

### Keep RSS Store Fresh

The RSS store tracks when items were discovered, not when they were created. This ensures Make.com detects them as "new":

```bash
# Reset and refresh (run after updates)
curl -X POST https://your-api.onrender.com/api/rss/clear
curl -X POST https://your-api.onrender.com/api/rss/refresh?time_range=daily
```

---

## 📸 Screenshots

### Main Interface
![App with Data](screenshots/app_with_data.png)

### Settings (Privacy-First)
![Tabs Section](screenshots/app_tabs_section.png)

---

## 🏗️ Architecture

```mermaid
flowchart TB
    subgraph Browser["🖥️ Browser (Your Device)"]
        UI[React UI]
        LS[(localStorage<br/>API Keys & Settings)]
    end

    subgraph Backend["⚙️ Backend (Stateless)"]
        API[FastAPI Server]
        
        subgraph Fetchers["📡 Data Fetchers"]
            GH[GitHub Trending]
            HFP[HuggingFace Papers]
            HFS[HuggingFace Spaces]
        end
        
        subgraph AI["🤖 AI Summarization"]
            Summarizer[summarizer.py]
            LocalLLM[local_llm.py<br/>No API needed]
            Cache[summary_cache.json]
        end
    end

    subgraph Providers["☁️ AI Providers (Optional)"]
        Groq[Groq API<br/>Free]
        Cohere[Cohere API]
        Anthropic[Anthropic Claude]
    end

    subgraph Sources["🌐 Data Sources"]
        GitHub[(GitHub)]
        HuggingFace[(HuggingFace)]
    end

    UI <--> LS
    UI -->|"Request + API Key"| API
    API --> GH & HFP & HFS
    API --> Summarizer
    
    Summarizer --> LocalLLM
    Summarizer -.->|"With User's Key"| Groq & Cohere & Anthropic
    Summarizer <--> Cache
    
    GH --> GitHub
    HFP & HFS --> HuggingFace

    style LS fill:#10b981,color:#fff
    style LocalLLM fill:#10b981,color:#fff
    style UI fill:#3b82f6,color:#fff
```

**Key Privacy Feature**: Your API keys never leave your browser except when making AI requests directly to the provider you choose.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+ 
- Node.js 18+
- Git

### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/hoodini/yuv-ai-trends.git
cd yuv-ai-trends

# Create Python virtual environment
python -m venv .venv

# Activate it (Windows)
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd ui
npm install
cd ..
```

### Step 2: Start the App

**Option A: One-click (Windows)**
```powershell
.\start_app.ps1
```

**Option B: Manual**
```bash
# Terminal 1 - Backend
python api.py

# Terminal 2 - Frontend
cd ui
npm run dev
```

### Step 3: Open and Use

1. Open http://localhost:5173
2. Click **"Generate"** to fetch AI news
3. It works immediately with Local Web LLM!
4. (Optional) Go to **Settings** to add your own API keys

---

## ⚙️ AI Provider Options

| Provider | Cost | Speed | Quality | API Key Required |
|----------|------|-------|---------|------------------|
| **Local Web LLM** | Free | Fast | Good | ❌ No |
| **Groq** | Free tier | Very Fast | Great | ✅ Yes |
| **Cohere** | Free tier | Fast | Great | ✅ Yes |
| **Anthropic** | Paid | Medium | Excellent | ✅ Yes |

### Get Free API Keys

- **Groq** (Recommended): https://console.groq.com/keys
- **Cohere**: https://dashboard.cohere.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys

---

## 🌐 Deploy to Production

### Deploy to GitHub Pages + Render (Free)

This app is designed for split deployment:
- **Frontend** → GitHub Pages (static hosting, free)
- **Backend** → Render (Python server, free tier)

#### Step 1: Deploy Backend to Render

1. Go to [render.com/new](https://render.com/new)
2. Click "New Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Copy your Render URL (e.g., `https://your-app.onrender.com`)

#### Step 2: Deploy Frontend to GitHub Pages

1. Update `ui/.env.production`:
   ```
   VITE_API_URL=https://your-app.onrender.com
   ```

2. Build and deploy:
   ```bash
   cd ui
   npm run build
   # Copy dist contents to repo root or gh-pages branch
   ```

3. Enable GitHub Pages in repo settings

#### Step 3: Keep Render Awake (Free Tier)

Render free tier sleeps after 15 min of inactivity. Use UptimeRobot:

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add HTTP monitor: `https://your-app.onrender.com/ping`
3. Set interval: 10 minutes

### Alternative: Vercel + Railway

For higher performance, use paid services:

#### Deploy Backend to Railway

1. Go to [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo"
3. Railway auto-detects Python
4. Copy your Railway URL

#### Deploy Frontend to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repo
3. Configure:
   - **Root Directory**: `ui`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_URL` = `https://your-railway-app.up.railway.app`
5. Deploy!

#### Vercel Settings Summary

| Setting | Value |
|---------|-------|
| Root Directory | `ui` |
| Framework | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Node.js Version | 18.x |

| Environment Variable | Value |
|---------------------|-------|
| `VITE_API_URL` | Your Railway backend URL |

That's it! Your app is now live. Users can:
1. Use Local Web LLM (no API key needed)
2. Add their own API keys in Settings (stored in their browser)

---

## 🔒 Privacy & Security

### How API Keys Are Handled

1. **Storage**: Keys stored in browser's `localStorage` only
2. **Transmission**: Keys sent only when making AI requests
3. **Server**: Backend is stateless - no keys stored server-side
4. **Validation**: Keys validated via `/api/validate-key` endpoint

### What Data is Collected

- **Nothing!** This app collects no user data
- No analytics, no tracking, no cookies
- Summary cache is stored locally on your machine

---

## 🛠️ API Reference

### `GET /rss.xml`
Get RSS 2.0 feed of AI trends.

```
GET /rss.xml?time_range=daily&limit=50
```

### `GET /feed.json`
Get JSON Feed of AI trends.

```
GET /feed.json?time_range=weekly&limit=20
```

### `POST /api/rss/refresh`
Force refresh RSS items from sources.

### `POST /api/rss/clear`
Clear all stored RSS items (reset the store).

### `GET /api/rss/stats`
Get RSS feed statistics.

### `GET /health` & `GET /ping`
Health check endpoints for monitoring services.

### `POST /api/generate`
Generate AI news digest with summaries.

```json
{
  "time_range": "daily",
  "limit": 50,
  "disable_ai": false,
  "llm_provider": "local_wasm",
  "llm_model": "",
  "api_key": null
}
```

### `POST /api/validate-key`
Validate an API key without storing it.

```json
{
  "provider": "groq",
  "api_key": "gsk_..."
}
```

### `GET /api/settings`
Get available providers and models.

### `POST /api/populate-summaries`
Populate AI summaries for items.

```json
{
  "items": [...],
  "force_refresh": false,
  "llm_provider": "groq",
  "api_key": "gsk_..."
}
```

---

## 📁 Project Structure

```
yuv-ai-trends/
├── api.py              # FastAPI backend (stateless)
├── rss_store.py        # Persistent RSS item storage
├── summarizer.py       # AI summary generation
├── local_llm.py        # Built-in summarizer (no API)
├── cache_manager.py    # Summary caching
├── fetchers.py         # GitHub & HuggingFace scrapers
├── ranker.py           # Content scoring
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
├── Procfile            # Render deployment
├── render.yaml         # Render config
└── ui/                 # React frontend
    ├── src/
    │   ├── App.jsx     # Main app (uses localStorage)
    │   ├── config.js   # API URL configuration
    │   └── components/
    │       ├── Settings.jsx  # localStorage-based settings
    │       └── Header.jsx    # Header with RSS button
    ├── package.json
    └── .env.production # Production API URL
```

---

## 🐛 Troubleshooting

### "Failed to connect to neural network"
- Make sure backend is running: `python api.py`
- Check it's on port 8000: http://localhost:8000/api/settings

### "API key invalid"
- Go to Settings → API Keys
- Make sure you copied the full key
- Try the "Validate & Save" button

### Summaries show "Details not available"
- This happens for items without descriptions
- Local LLM does its best with available info
- Try a different AI provider for better results

### CORS errors in production
- Make sure `VITE_API_URL` is set correctly in Vercel
- Backend should allow your Vercel domain (uses `*` by default)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - use it however you want!

---

## 👤 Author

**Yuval Avidani** - [YUV.AI](https://yuv.ai)

---

**Made with ❤️ for the AI/ML community**
