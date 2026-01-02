from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import io
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# RADICAL FIX: Suppress ALL output to prevent Windows encoding issues
# Temporarily disabled for debugging
# if sys.platform == 'win32':
#     # Redirect stdout and stderr to devnull to prevent ANY encoding errors
#     sys.stdout = open(os.devnull, 'w', encoding='utf-8')
#     sys.stderr = open(os.devnull, 'w', encoding='utf-8')

import config
from fetchers import GitHubTrendingFetcher, GitHubExploreFetcher, HuggingFaceFetcher
from ranker import ContentRanker
from generator import DigestGenerator
from utils import sanitize_dict
from summarizer import AIContentSummarizer
import uvicorn
import os

app = FastAPI(title="AI Tech News API")

# Configure JSON encoding to handle all Unicode characters
app.state.json_encoder = lambda obj: json.dumps(obj, ensure_ascii=False)

# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',') if os.getenv('ALLOWED_ORIGINS') else []
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + DEFAULT_ORIGINS if ALLOWED_ORIGINS else ["*"],  # Allow all for dev, use ALLOWED_ORIGINS in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    time_range: str = "daily"
    limit: int = 50
    disable_ai: bool = False
    # User-provided LLM settings (from browser localStorage)
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    api_key: Optional[str] = None

class APIKeyRequest(BaseModel):
    provider: str
    api_key: str

class ProviderRequest(BaseModel):
    provider: str
    model: Optional[str] = None

class PopulateRequest(BaseModel):
    items: List[Dict]
    force_refresh: bool = False
    # User-provided LLM settings (from browser localStorage)
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    api_key: Optional[str] = None

@app.post("/api/generate")
async def generate_news(request: GenerateRequest):
    try:
        # Determine time range
        if request.time_range not in config.TIME_RANGES:
            raise HTTPException(status_code=400, detail="Invalid time range")

        time_range_days = config.TIME_RANGES[request.time_range]
        
        # Initialize components
        github_trending = GitHubTrendingFetcher()
        github_explore = GitHubExploreFetcher()
        hf_fetcher = HuggingFaceFetcher()
        ranker = ContentRanker()
        
        # Initialize generator with AI summaries unless disabled
        use_ai = config.AI_SUMMARIES_ENABLED and not request.disable_ai
        
        # Pass user-provided LLM settings to generator
        generator = DigestGenerator(
            use_ai_summaries=use_ai,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model,
            api_key=request.api_key
        )
        
        all_items = []
        
        # Fetch GitHub Trending
        # print("Fetching GitHub trending repositories...")
        try:
            gh_time_range = request.time_range if request.time_range in ['daily', 'weekly', 'monthly'] else 'daily'
            github_repos = github_trending.fetch_all_languages(since=gh_time_range)
            # Sanitize immediately after fetching to prevent encoding issues
            github_repos = [sanitize_dict(repo) for repo in github_repos]
            all_items.extend(github_repos)
        except Exception as e:
            error_str = str(e).encode('ascii', 'ignore').decode('ascii')
            # print(f"WARNING: Error fetching GitHub: {error_str}")
            pass

        # Fetch GitHub Explore
        # print("Fetching GitHub Explore collections...")
        try:
            collections = github_explore.fetch_collections()
            collections = [sanitize_dict(c) for c in collections]
            all_items.extend(collections)
        except Exception as e:
            error_str = str(e).encode('ascii', 'ignore').decode('ascii')
            # print(f"WARNING: Error fetching GitHub Explore: {error_str}")
            pass

        # Fetch Hugging Face Papers
        # print("Fetching Hugging Face papers...")
        try:
            papers = hf_fetcher.fetch_papers(limit=20)
            papers = [sanitize_dict(p) for p in papers]
            all_items.extend(papers)
        except Exception as e:
            error_str = str(e).encode('ascii', 'ignore').decode('ascii')
            # print(f"WARNING: Error fetching HF Papers: {error_str}")
            pass

        # Fetch Hugging Face Spaces
        # print("Fetching Hugging Face trending spaces...")
        try:
            spaces = hf_fetcher.fetch_trending_spaces(limit=config.HF_SPACES_TRENDING_LIMIT)
            spaces = [sanitize_dict(s) for s in spaces]
            all_items.extend(spaces)
        except Exception as e:
            error_str = str(e).encode('ascii', 'ignore').decode('ascii')
            # print(f"WARNING: Error fetching HF Spaces: {error_str}")
            pass

        if not all_items:
            return {"items": [], "stats": {}}

        # Rank items
        # print("Ranking and scoring items...")
        ranked_items = ranker.rank_items(all_items, days_range=time_range_days)
        
        # Get top items
        top_items = ranker.get_top_items(ranked_items, limit=request.limit)
        
        # Group by source
        grouped_items = ranker.group_by_source(top_items)
        
        # Enrich with AI summaries if enabled
        # We use the method we just extracted in generator.py
        if use_ai:
            generator.enrich_data(grouped_items)
            
        # Flatten back to list for JSON response, but keep grouped structure if needed
        # For the UI, a flat list might be easier if we want to mix them, or grouped sections.
        # Let's return grouped items and a flat list.
        
        flat_items = []
        for source, items in grouped_items.items():
            flat_items.extend(items)
            
        # Sort flat items by score again just in case
        flat_items.sort(key=lambda x: x.get('score', 0), reverse=True)

        # Sanitize all data to remove emojis (Windows encoding fix)
        result = {
            "items": flat_items,
            "grouped_items": grouped_items,
            "stats": {
                "total": len(flat_items),
                "sources": {k: len(v) for k, v in grouped_items.items()}
            }
        }

        sanitized_result = sanitize_dict(result)

        # Return as JSON response with explicit encoding
        json_str = json.dumps(sanitized_result, ensure_ascii=True)
        return Response(content=json_str, media_type="application/json")

    except Exception as e:
        import traceback
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        traceback_str = traceback.format_exc().encode('ascii', 'ignore').decode('ascii')
        # print(f"Error: {error_msg}")
        # print(f"Traceback: {traceback_str}")

        # Log to file for debugging
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n\n=== Error at {__import__('datetime').datetime.now()} ===\n")
            f.write(f"Error: {error_msg}\n")
            f.write(f"Traceback: {traceback_str}\n")

        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/settings")
async def get_settings():
    """Get available providers and models (no API key status - keys stored in browser)"""
    try:
        settings = {
            'llm_provider': 'local_wasm',  # Default provider
            'available_providers': {
                'local_wasm': {
                    'name': 'Local Web LLM',
                    'enabled': True,
                    'description': 'Privacy-focused, runs without any API key',
                    'requiresKey': False
                },
                'groq': {
                    'name': 'Groq (Free)',
                    'enabled': True,
                    'description': 'Ultra-fast inference with free API tier',
                    'requiresKey': True,
                    'keyUrl': 'https://console.groq.com/keys'
                },
                'cohere': {
                    'name': 'Cohere',
                    'enabled': True,
                    'description': 'Fast and accurate with Command models',
                    'requiresKey': True,
                    'keyUrl': 'https://dashboard.cohere.com/api-keys'
                },
                'anthropic': {
                    'name': 'Anthropic Claude',
                    'enabled': True,
                    'description': 'High-quality AI summaries with Claude',
                    'requiresKey': True,
                    'keyUrl': 'https://console.anthropic.com/settings/keys'
                }
            },
            'models': {
                'local_wasm': [
                    {'id': 'local', 'name': 'Built-in Summarizer', 'recommended': True}
                ],
                'groq': [
                    {'id': 'llama-3.3-70b-versatile', 'name': 'Llama 3.3 70B', 'recommended': True},
                    {'id': 'llama-3.1-70b-versatile', 'name': 'Llama 3.1 70B', 'recommended': False},
                    {'id': 'mixtral-8x7b-32768', 'name': 'Mixtral 8x7B', 'recommended': False}
                ],
                'cohere': [
                    {'id': 'command-a-03-2025', 'name': 'Command-A (Latest)', 'recommended': True},
                    {'id': 'command-r-plus', 'name': 'Command R+', 'recommended': False},
                    {'id': 'command-r', 'name': 'Command R', 'recommended': False}
                ],
                'anthropic': [
                    {'id': 'claude-sonnet-4-20250514', 'name': 'Claude Sonnet 4.5', 'recommended': True},
                    {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet', 'recommended': False}
                ]
            }
        }
        return Response(content=json.dumps(settings, ensure_ascii=True), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validate-key")
async def validate_api_key(request: APIKeyRequest):
    """Validate an API key without storing it (keys stored in browser localStorage)"""
    try:
        provider = request.provider
        api_key = request.api_key
        
        if not api_key or not api_key.strip():
            return Response(
                content=json.dumps({'valid': False, 'message': 'API key cannot be empty'}, ensure_ascii=True),
                media_type="application/json"
            )
        
        # Test the API key
        try:
            if provider == 'anthropic':
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                
            elif provider == 'cohere':
                import cohere
                client = cohere.ClientV2(api_key=api_key)
                client.chat(
                    model="command-a-03-2025",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                
            elif provider == 'groq':
                from groq import Groq
                client = Groq(api_key=api_key)
                client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
            else:
                return Response(
                    content=json.dumps({'valid': False, 'message': f'Unknown provider: {provider}'}, ensure_ascii=True),
                    media_type="application/json"
                )
            
            return Response(
                content=json.dumps({'valid': True, 'message': 'API key is valid!'}, ensure_ascii=True),
                media_type="application/json"
            )
            
        except Exception as e:
            error_msg = str(e)
            if '401' in error_msg or 'unauthorized' in error_msg.lower() or 'invalid' in error_msg.lower():
                return Response(
                    content=json.dumps({'valid': False, 'message': 'Invalid API key'}, ensure_ascii=True),
                    media_type="application/json"
                )
            elif '429' in error_msg or 'rate limit' in error_msg.lower():
                return Response(
                    content=json.dumps({'valid': True, 'message': 'API key valid (rate limited but working)'}, ensure_ascii=True),
                    media_type="application/json"
                )
            else:
                return Response(
                    content=json.dumps({'valid': False, 'message': f'Validation error: {error_msg[:100]}'}, ensure_ascii=True),
                    media_type="application/json"
                )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/populate-summaries")
async def populate_summaries(request: PopulateRequest):
    """Populate AI summaries for items that don't have them"""
    try:
        # Check if AI is enabled
        if not config.AI_SUMMARIES_ENABLED:
            return Response(
                content=json.dumps({
                    'success': False,
                    'message': 'AI summaries are disabled in configuration'
                }, ensure_ascii=True),
                media_type="application/json"
            )
        
        # Initialize summarizer with user-provided settings
        summarizer = AIContentSummarizer(
            provider=request.llm_provider,
            api_key=request.api_key,
            model=request.llm_model
        )
        
        # If force_refresh, regenerate all summaries
        if request.force_refresh:
            enriched_items = summarizer.enrich_items_batch(request.items, max_workers=3)
            result = {
                'success': True,
                'total_items': len(request.items),
                'populated': len([item for item in enriched_items if item.get('ai_summary')]),
                'message': f'Refreshed summaries for {len(enriched_items)} items'
            }
        else:
            # Only populate missing summaries
            stats = summarizer.populate_missing_summaries(request.items, max_workers=3)
            result = {
                'success': True,
                **stats,
                'message': f'Populated {stats["newly_populated"]} new summaries ({stats["already_cached"]} already cached)'
            }
        
        return Response(content=json.dumps(result, ensure_ascii=True), media_type="application/json")
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/cache-stats")
async def get_cache_stats():
    """Get statistics about the summary cache"""
    try:
        summarizer = AIContentSummarizer()
        stats = summarizer.get_cache_stats()
        return Response(content=json.dumps(stats, ensure_ascii=True), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-summaries")
async def check_summaries(request: PopulateRequest):
    """Check which items are missing summaries"""
    try:
        summarizer = AIContentSummarizer()
        items_without = summarizer.get_items_without_summary(request.items)
        
        result = {
            'total_items': len(request.items),
            'with_summary': len(request.items) - len(items_without),
            'without_summary': len(items_without),
            'missing_items': [
                {
                    'name': item.get('name', ''),
                    'source': item.get('source', ''),
                    'url': item.get('url', '')
                }
                for item in items_without
            ]
        }
        
        return Response(content=json.dumps(result, ensure_ascii=True), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run uvicorn server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
