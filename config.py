"""Configuration settings for the Gen AI News Aggregator"""

# GitHub settings
GITHUB_TRENDING_URL = "https://github.com/trending"
GITHUB_LANGUAGES = ["python", "jupyter-notebook", "typescript"]  # AI/ML relevant languages
GITHUB_TOPICS = ["machine-learning", "deep-learning", "llm", "generative-ai", "transformers"]

# Hugging Face settings
HF_PAPERS_URL = "https://huggingface.co/papers"
HF_SPACES_TRENDING_LIMIT = 20

# Time ranges
TIME_RANGES = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
}

# Scoring weights
SCORING_WEIGHTS = {
    "stars_weight": 0.4,
    "recency_weight": 0.3,
    "velocity_weight": 0.3,
}

# Output settings
OUTPUT_DIR = "output"
TEMPLATE_DIR = "templates"
