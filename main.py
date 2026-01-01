"""Main application and CLI interface"""

import click
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fetchers import GitHubTrendingFetcher, GitHubExploreFetcher, HuggingFaceFetcher
from ranker import ContentRanker
from generator import DigestGenerator
import config


@click.command()
@click.option(
    '--range',
    'time_range',
    type=click.Choice(['daily', 'weekly', 'monthly'], case_sensitive=False),
    default='daily',
    help='Time range for trending content'
)
@click.option(
    '--days',
    type=int,
    help='Custom number of days to look back (overrides --range)'
)
@click.option(
    '--output',
    type=str,
    help='Custom output filename'
)
@click.option(
    '--limit',
    type=int,
    default=50,
    help='Maximum number of items to include in digest'
)
@click.option(
    '--open',
    'open_browser',
    is_flag=True,
    help='Open the generated HTML file in browser'
)
@click.option(
    '--no-ai',
    'disable_ai',
    is_flag=True,
    help='Disable AI-powered summaries and explanations'
)
def main(time_range, days, output, limit, open_browser, disable_ai):
    """
    Gen AI News Aggregator - Stay updated with the latest in Gen AI and ML
    
    Fetches trending content from GitHub and Hugging Face, ranks it,
    and generates a beautiful HTML digest.
    """
    click.echo("🤖 Gen AI News Aggregator")
    click.echo("=" * 50)
    
    # Determine time range
    if days:
        time_range_days = days
        time_range_label = f"{days} days"
    else:
        time_range_days = config.TIME_RANGES[time_range]
        time_range_label = time_range
    
    click.echo(f"📅 Time range: {time_range_label}")
    click.echo()
    
    # Initialize components
    github_trending = GitHubTrendingFetcher()
    github_explore = GitHubExploreFetcher()
    hf_fetcher = HuggingFaceFetcher()
    ranker = ContentRanker()
    
    # Initialize generator with AI summaries unless disabled
    use_ai = config.AI_SUMMARIES_ENABLED and not disable_ai
    generator = DigestGenerator(use_ai_summaries=use_ai)
    
    all_items = []
    
    # Fetch GitHub Trending
    click.echo("🔥 Fetching GitHub trending repositories...")
    try:
        # Map time range to GitHub's format
        gh_time_range = time_range if time_range in ['daily', 'weekly', 'monthly'] else 'daily'
        github_repos = github_trending.fetch_all_languages(since=gh_time_range)
        all_items.extend(github_repos)
        click.echo(f"   Found {len(github_repos)} repos")
    except Exception as e:
        click.echo(f"   ⚠️  Error: {e}", err=True)
    
    # Fetch GitHub Explore
    click.echo("📦 Fetching GitHub Explore collections...")
    try:
        collections = github_explore.fetch_collections()
        all_items.extend(collections)
        click.echo(f"   Found {len(collections)} collections")
    except Exception as e:
        click.echo(f"   ⚠️  Error: {e}", err=True)
    
    # Fetch Hugging Face Papers
    click.echo("📄 Fetching Hugging Face papers...")
    try:
        papers = hf_fetcher.fetch_papers(limit=20)
        all_items.extend(papers)
        click.echo(f"   Found {len(papers)} papers")
    except Exception as e:
        click.echo(f"   ⚠️  Error: {e}", err=True)
    
    # Fetch Hugging Face Spaces
    click.echo("🚀 Fetching Hugging Face trending spaces...")
    try:
        spaces = hf_fetcher.fetch_trending_spaces(limit=config.HF_SPACES_TRENDING_LIMIT)
        all_items.extend(spaces)
        click.echo(f"   Found {len(spaces)} spaces")
    except Exception as e:
        click.echo(f"   ⚠️  Error: {e}", err=True)
    
    click.echo()
    click.echo(f"📊 Total items fetched: {len(all_items)}")
    
    if not all_items:
        click.echo("❌ No items found. Please try again later.")
        return
    
    # Rank items
    click.echo("🎯 Ranking and scoring items...")
    ranked_items = ranker.rank_items(all_items, days_range=time_range_days)
    
    # Get top items
    top_items = ranker.get_top_items(ranked_items, limit=limit)
    click.echo(f"   Selected top {len(top_items)} items")
    
    # Group by source
    grouped_items = ranker.group_by_source(top_items)
    
    # Generate HTML
    click.echo("📝 Generating HTML digest...")
    try:
        output_path = generator.generate(
            items=top_items,
            grouped_items=grouped_items,
            time_range=time_range_label,
            output_filename=output
        )
        click.echo(f"✅ Digest generated: {output_path}")
        
        # Open in browser if requested
        if open_browser:
            click.echo("🌐 Opening in browser...")
            import webbrowser
            webbrowser.open(f"file:///{os.path.abspath(output_path)}")
        
    except Exception as e:
        click.echo(f"❌ Error generating digest: {e}", err=True)
        return
    
    click.echo()
    click.echo("=" * 50)
    click.echo("✨ Done! Enjoy your Gen AI news digest!")


if __name__ == '__main__':
    main()
