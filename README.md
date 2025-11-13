# 🤖 YUV.AI Developers AI Trends

> **Stay ahead of the curve with curated Gen AI & Machine Learning trends, delivered in a beautiful digest.**

A personalized news aggregator that fetches, ranks, and presents the latest trending content from the AI/ML ecosystem in a stunning, Apple Newsroom-inspired layout.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

---

## ✨ Features

### 📊 **Multi-Source Aggregation**
- 🔥 **GitHub Trending** - Hottest repos with star velocity tracking
- 📄 **Hugging Face Papers** - Latest research from arXiv & HF Daily Papers
- 🚀 **Hugging Face Spaces** - Trending interactive ML demos
- 📦 **GitHub Explore** - Curated collections (coming soon)

### 🎨 **Beautiful Design**
- Clean, modern card-based layout inspired by Apple Newsroom
- Responsive design that works on all devices
- Smart typography and spacing
- Smooth animations and hover effects

### 🎯 **Smart Ranking**
- Popularity metrics (stars, likes, upvotes)
- Growth velocity (stars/day)
- Real-time trending indicators
- Topic categorization and tags

### ⚙️ **Flexible & Customizable**
- Multiple time ranges: daily, weekly, monthly, or custom
- Configurable sources and filters
- Language-specific trending (Python, TypeScript, Jupyter, etc.)
- Easy branding customization

### 🤖 **Automation Ready**
- CLI interface for easy scripting
- Supports Windows Task Scheduler, cron, GitHub Actions
- One-command digest generation
- Optional auto-open in browser

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/yuv-ai-trends.git
cd yuv-ai-trends
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Generate your first digest**
```bash
python main.py --range daily --open
```

That's it! Your browser will open with today's AI trends digest. 🎉

---

## 📖 Usage

### Basic Commands

```bash
# Daily digest (default)
python main.py --range daily

# Weekly digest
python main.py --range weekly

# Monthly digest
python main.py --range monthly

# Custom date range (14 days)
python main.py --days 14

# Limit number of items
python main.py --range daily --limit 30

# Auto-open in browser
python main.py --range daily --open

# Custom output filename
python main.py --range daily --output my_digest.html
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--range` | Time range: daily, weekly, monthly | `--range weekly` |
| `--days` | Custom number of days | `--days 7` |
| `--limit` | Max items in digest | `--limit 50` |
| `--open` | Open in browser after generation | `--open` |
| `--output` | Custom output filename | `--output weekly.html` |

---

## ⚙️ Configuration

Edit `config.py` to customize your digest:

```python
# GitHub settings
GITHUB_LANGUAGES = ["python", "jupyter-notebook", "typescript"]
GITHUB_TOPICS = ["machine-learning", "deep-learning", "llm", "generative-ai"]

# Hugging Face settings
HF_SPACES_TRENDING_LIMIT = 20

# Scoring weights (adjust to your preference)
SCORING_WEIGHTS = {
    "stars_weight": 0.4,      # GitHub stars importance
    "recency_weight": 0.3,    # How recent matters
    "velocity_weight": 0.3,   # Growth rate importance
}
```

---

## 🤖 Automation

### Windows (Task Scheduler)

**PowerShell command:**
```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\news\main.py --range daily --open"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AITrendsDaily"
```

### Linux/Mac (Cron)

```bash
# Edit crontab
crontab -e

# Add this line for daily 8am execution
0 8 * * * cd /path/to/news && python main.py --range daily
```

### GitHub Actions

Create `.github/workflows/daily-digest.yml`:

```yaml
name: Daily AI Trends
on:
  schedule:
    - cron: '0 8 * * *'  # 8am UTC daily
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python main.py --range daily
```

See `AUTOMATION.md` for more detailed automation options.

---

## 📁 Project Structure

```
yuv-ai-trends/
├── main.py              # CLI entry point
├── config.py            # Configuration settings
├── fetchers.py          # Data collection from sources
├── ranker.py            # Scoring & ranking algorithms
├── generator.py         # HTML digest generation
├── hf_mcp.py           # Hugging Face MCP integration
├── templates/
│   └── digest.html      # Beautiful HTML template
├── output/              # Generated digests
├── requirements.txt     # Python dependencies
├── README.md           # You are here!
└── AUTOMATION.md       # Automation guides
```

---

## 🎨 Customization

### Branding

Edit `templates/digest.html` header section to customize branding:

```html
<header>
    <div>
        <strong>Your Name</strong> • Your Title • <a href="https://yoursite.com">YourSite</a>
    </div>
    <h1>🤖 Your AI Trends Title</h1>
</header>
```

### Styling

The template uses clean, modern CSS. Key classes to customize:

- `.item` - Card styling
- `.item-title` - Title appearance
- `.section-title` - Section headers
- `header` - Top banner gradient

---

## 🔧 Technical Details

### Data Sources

1. **GitHub Trending**: Web scraping with BeautifulSoup
2. **Hugging Face Papers**: HF Papers page scraping + arXiv metadata
3. **Hugging Face Spaces**: Official HF Hub API
4. **GitHub Explore**: Web scraping (limited availability)

### Ranking Algorithm

Items are scored based on:
- **Popularity**: Stars, likes, upvotes (40%)
- **Velocity**: Recent growth rate (30%)
- **Recency**: How recent the item is (30%)

Scores are normalized to 0-100 and items are sorted accordingly.

### Technologies

- **Python 3.8+**: Core language
- **Requests**: HTTP client
- **BeautifulSoup4**: HTML parsing
- **Hugging Face Hub**: Official API client
- **Jinja2**: HTML templating
- **Click**: CLI interface

---

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- 🐛 Report bugs and issues
- 💡 Suggest new features or data sources
- 🎨 Improve the design/layout
- 📖 Improve documentation
- 🔧 Submit pull requests

### Development Setup

```bash
# Fork and clone the repo
git clone https://github.com/yourusername/yuv-ai-trends.git

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Make your changes and test
python main.py --range daily --open
```

---

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 👤 Author

**Yuval Avidani**
- 🌐 Website: [YUV.AI](https://yuv.ai)
- 💼 AI Builder & Speaker
- 🚀 Passionate about democratizing AI knowledge

---

## 🙏 Acknowledgments

- GitHub for trending data
- Hugging Face for Papers and Spaces API
- The amazing open-source AI/ML community

---

## 📊 Sample Output

The digest includes:
- **Total Items**: Count of all trending content
- **GitHub Repos**: With stars, velocity, topics, forks, contributors
- **Papers**: With authors, arXiv IDs, upvotes, publication dates
- **Spaces**: With likes, SDKs, creation dates

All organized in a beautiful, clickable layout with smooth scrolling and responsive design.

---

## 🔮 Roadmap

- [ ] Add more data sources (Papers with Code, Reddit, Twitter)
- [ ] Email digest delivery
- [ ] RSS feed generation
- [ ] User accounts and preferences
- [ ] Mobile app
- [ ] AI-powered summaries

---

**Made with ❤️ for the AI/ML community**
