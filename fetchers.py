"""Fetchers for different content sources"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import config


class GitHubTrendingFetcher:
    """Fetch trending repositories from GitHub"""
    
    def __init__(self):
        self.base_url = config.GITHUB_TRENDING_URL
        
    def fetch(self, language: Optional[str] = None, since: str = "daily") -> List[Dict]:
        """
        Fetch trending repos
        
        Args:
            language: Programming language filter (e.g., 'python')
            since: Time range - 'daily', 'weekly', or 'monthly'
        """
        url = self.base_url
        if language:
            url = f"{url}/{language}"
        
        params = {"since": since}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = []
            
            # Find all repository articles
            for article in soup.find_all('article', class_='Box-row'):
                repo_data = self._parse_repo(article, since)
                if repo_data:
                    repos.append(repo_data)
            
            return repos
            
        except Exception as e:
            # print(f"Error fetching GitHub trending: {e}")
            return []
    
    def _parse_repo(self, article, since: str) -> Optional[Dict]:
        """Parse a single repository from HTML"""
        try:
            # Repo name and URL
            h2 = article.find('h2', class_='h3')
            if not h2:
                return None
            
            link = h2.find('a')
            if not link:
                return None
                
            repo_name = link.get('href', '').strip('/')
            repo_url = f"https://github.com{link.get('href', '')}"
            
            # Description
            description_elem = article.find('p', class_='col-9')
            description = description_elem.text.strip() if description_elem else ""
            
            # Stars
            stars_elem = article.find('svg', class_='octicon-star')
            stars = 0
            if stars_elem:
                parent = stars_elem.find_parent('a')
                if parent:
                    stars_text = parent.text.strip().replace(',', '')
                    stars = int(re.search(r'\d+', stars_text).group()) if re.search(r'\d+', stars_text) else 0
            
            # Today's stars (velocity)
            stars_today = 0
            stars_today_elem = article.find('span', class_='d-inline-block float-sm-right')
            if stars_today_elem:
                stars_text = stars_today_elem.text.strip().replace(',', '')
                match = re.search(r'(\d+)', stars_text)
                if match:
                    stars_today = int(match.group(1))
            
            # Language
            language_elem = article.find('span', attrs={'itemprop': 'programmingLanguage'})
            language = language_elem.text.strip() if language_elem else "Unknown"
            
            # Extract topics/tags
            topics = []
            topic_elems = article.find_all('a', class_='topic-tag')
            for topic in topic_elems:
                topics.append(topic.text.strip())
            
            # Get forks count
            forks = 0
            forks_elem = article.find('svg', class_='octicon-repo-forked')
            if forks_elem:
                parent = forks_elem.find_parent('a')
                if parent:
                    forks_text = parent.text.strip().replace(',', '')
                    match = re.search(r'(\d+)', forks_text)
                    if match:
                        forks = int(match.group(1))
            
            # Built by section (contributors)
            built_by = 0
            built_by_elem = article.find('span', text=re.compile(r'Built by'))
            if built_by_elem:
                imgs = built_by_elem.find_parent().find_all('img')
                built_by = len(imgs)
            
            return {
                'source': 'github_trending',
                'name': repo_name,
                'url': repo_url,
                'description': description,
                'stars': stars,
                'stars_today': stars_today,
                'forks': forks,
                'language': language,
                'topics': topics,
                'built_by': built_by,
                'fetched_at': datetime.now().isoformat(),
                'time_range': since,
            }
            
        except Exception as e:
            # print(f"Error parsing repo: {e}")
            return None
    
    def fetch_all_languages(self, since: str = "daily") -> List[Dict]:
        """Fetch trending repos for all configured languages"""
        all_repos = []
        
        # Fetch overall trending
        all_repos.extend(self.fetch(since=since))
        
        # Fetch for specific languages
        for lang in config.GITHUB_LANGUAGES:
            repos = self.fetch(language=lang, since=since)
            all_repos.extend(repos)
        
        # Deduplicate by URL
        seen = set()
        unique_repos = []
        for repo in all_repos:
            if repo['url'] not in seen:
                seen.add(repo['url'])
                unique_repos.append(repo)
        
        return unique_repos


class GitHubExploreFetcher:
    """Fetch collections from GitHub Explore"""
    
    def __init__(self):
        self.base_url = "https://github.com/explore"
    
    def fetch_collections(self) -> List[Dict]:
        """Fetch featured collections"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            collections = []
            
            # Find collection articles
            for article in soup.find_all('article', class_='col-md-6'):
                collection = self._parse_collection(article)
                if collection:
                    collections.append(collection)
            
            return collections[:10]  # Limit to top 10
            
        except Exception as e:
            # print(f"Error fetching GitHub Explore: {e}")
            return []
    
    def _parse_collection(self, article) -> Optional[Dict]:
        """Parse a single collection"""
        try:
            # Title and URL
            h3 = article.find('h3')
            if not h3:
                return None
            
            link = h3.find('a')
            if not link:
                return None
            
            title = link.text.strip()
            url = f"https://github.com{link.get('href', '')}"
            
            # Description
            description_elem = article.find('p')
            description = description_elem.text.strip() if description_elem else ""
            
            return {
                'source': 'github_explore',
                'name': title,
                'url': url,
                'description': description,
                'fetched_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            # print(f"Error parsing collection: {e}")
            return None


class HuggingFaceFetcher:
    """Fetch content from Hugging Face"""
    
    def __init__(self):
        self.papers_url = config.HF_PAPERS_URL
        
    def fetch_papers(self, limit: int = 20) -> List[Dict]:
        """Fetch trending papers from Hugging Face"""
        try:
            response = requests.get(self.papers_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            papers = []
            
            # Find paper articles
            for article in soup.find_all('article')[:limit]:
                paper = self._parse_paper(article)
                if paper:
                    papers.append(paper)
            
            return papers
            
        except Exception as e:
            # print(f"Error fetching HF papers: {e}")
            return []
    
    def _parse_paper(self, article) -> Optional[Dict]:
        """Parse a single paper"""
        try:
            # Title and URL
            h3 = article.find('h3')
            if not h3:
                return None
            
            link = h3.find('a')
            if not link:
                return None
            
            title = h3.text.strip()
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"https://huggingface.co{url}"
            
            # Authors
            authors_elem = article.find('p', class_='text-sm')
            authors = authors_elem.text.strip() if authors_elem else ""
            
            # Upvotes
            upvotes_elem = article.find('div', class_='leading-none')
            upvotes = 0
            if upvotes_elem:
                upvotes_text = upvotes_elem.text.strip()
                match = re.search(r'(\d+)', upvotes_text)
                if match:
                    upvotes = int(match.group(1))
            
            # Extract arXiv ID or paper metadata
            arxiv_id = ""
            published_date = ""
            if 'arxiv.org' in url or '/papers/' in url:
                match = re.search(r'(\d+\.\d+)', url)
                if match:
                    arxiv_id = match.group(1)
                    # arXiv ID format: YYMM.NNNNN (e.g., 2311.12345 = Nov 2023)
                    year_month = arxiv_id.split('.')[0]
                    if len(year_month) == 4:
                        year = '20' + year_month[:2]
                        month = year_month[2:]
                        published_date = f"{year}-{month}"
            
            # Try to find publish date in the article
            date_elem = article.find('time')
            if date_elem and not published_date:
                published_date = date_elem.get('datetime', '')
            
            return {
                'source': 'huggingface_papers',
                'name': title,
                'url': url,
                'description': authors,
                'upvotes': upvotes,
                'arxiv_id': arxiv_id,
                'published_date': published_date,
                'fetched_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            # print(f"Error parsing paper: {e}")
            return None
    
    def fetch_trending_spaces(self, limit: int = 20) -> List[Dict]:
        """Fetch trending Spaces from Hugging Face using API"""
        # Use HF Hub API to get spaces sorted by likes
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            
            # List spaces sorted by likes (trending alternative)
            spaces_list = list(api.list_spaces(sort="likes", limit=limit))
            spaces = []
            
            for space_info in spaces_list:
                # Get description from various sources
                description = ""
                
                # Try card_data first
                if hasattr(space_info, 'card_data') and space_info.card_data:
                    description = (
                        space_info.card_data.get('short_description') or
                        space_info.card_data.get('description') or
                        space_info.card_data.get('title') or
                        ''
                    )
                
                # If still empty, construct from space ID
                if not description and space_info.id:
                    owner = space_info.id.split('/')[0] if '/' in space_info.id else ''
                    sdk_info = f" ({space_info.sdk})" if hasattr(space_info, 'sdk') and space_info.sdk else ""
                    if owner:
                        description = f"Interactive AI demo{sdk_info} by {owner}"
                
                # Get creation date
                created_at = ""
                if hasattr(space_info, 'created_at'):
                    created_at = space_info.created_at.strftime('%Y-%m-%d') if space_info.created_at else ""
                
                space_data = {
                    'source': 'huggingface_spaces',
                    'name': space_info.id,
                    'url': f"https://huggingface.co/spaces/{space_info.id}",
                    'description': description,
                    'likes': space_info.likes,
                    'sdk': space_info.sdk if hasattr(space_info, 'sdk') else 'Unknown',
                    'created_at': created_at,
                    'fetched_at': datetime.now().isoformat(),
                }
                spaces.append(space_data)
            
            return spaces
            
        except Exception as e:
            # print(f"Error fetching HF spaces via API: {e}")
            # Fallback to empty list
            return []
    
    def _parse_space(self, article) -> Optional[Dict]:
        """Parse a single Space"""
        try:
            # Title and URL
            h4 = article.find('h4')
            if not h4:
                return None
            
            link = h4.find('a')
            if not link:
                return None
            
            title = h4.text.strip()
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"https://huggingface.co{url}"
            
            # Description
            description_elem = article.find('p', class_='text-sm')
            description = description_elem.text.strip() if description_elem else ""
            
            # Likes
            likes_elem = article.find('svg', class_='text-yellow-500')
            likes = 0
            if likes_elem:
                parent = likes_elem.find_parent()
                if parent:
                    likes_text = parent.text.strip()
                    match = re.search(r'(\d+)', likes_text)
                    if match:
                        likes = int(match.group(1))
            
            # Extract SDK/framework from Space
            sdk = ""
            sdk_elem = article.find('span', class_='text-xs')
            if sdk_elem:
                sdk_text = sdk_elem.text.strip()
                if 'gradio' in sdk_text.lower():
                    sdk = 'Gradio'
                elif 'streamlit' in sdk_text.lower():
                    sdk = 'Streamlit'
                elif 'docker' in sdk_text.lower():
                    sdk = 'Docker'
            
            return {
                'source': 'huggingface_spaces',
                'name': title,
                'url': url,
                'description': description,
                'likes': likes,
                'sdk': sdk,
                'fetched_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            # print(f"Error parsing space: {e}")
            return None
