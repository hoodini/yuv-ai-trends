"""Scoring and ranking system for content items"""

from datetime import datetime, timedelta
from typing import List, Dict
import config


class ContentRanker:
    """Rank and score content from different sources"""
    
    def __init__(self):
        self.weights = config.SCORING_WEIGHTS
    
    def calculate_score(self, item: Dict, days_range: int = 1) -> float:
        """
        Calculate a score for an item based on multiple factors
        
        Args:
            item: Content item dictionary
            days_range: Number of days to consider for scoring
        
        Returns:
            Normalized score between 0 and 100
        """
        source = item.get('source', '')
        
        if source == 'github_trending':
            return self._score_github_repo(item, days_range)
        elif source == 'github_explore':
            return self._score_github_collection(item)
        elif source == 'huggingface_papers':
            return self._score_paper(item)
        elif source == 'huggingface_spaces':
            return self._score_space(item)
        
        return 0.0
    
    def _score_github_repo(self, repo: Dict, days_range: int) -> float:
        """Score a GitHub repository"""
        stars = repo.get('stars', 0)
        stars_today = repo.get('stars_today', 0)
        
        # Normalize stars (log scale for better distribution)
        import math
        stars_score = math.log10(stars + 1) * 10 if stars > 0 else 0
        stars_score = min(stars_score, 50)  # Cap at 50
        
        # Velocity score (stars gained recently)
        velocity_score = min(stars_today * 2, 30)  # Cap at 30
        
        # Recency bonus (items are already from trending, so give base score)
        recency_score = 20
        
        total_score = (
            stars_score * self.weights['stars_weight'] +
            velocity_score * self.weights['velocity_weight'] +
            recency_score * self.weights['recency_weight']
        )
        
        return min(total_score, 100)
    
    def _score_github_collection(self, collection: Dict) -> float:
        """Score a GitHub collection (curated content gets consistent score)"""
        # Collections are curated by GitHub, so give them a good base score
        return 70.0
    
    def _score_paper(self, paper: Dict) -> float:
        """Score a research paper"""
        upvotes = paper.get('upvotes', 0)
        
        # Papers on HF daily page are already curated, weight upvotes
        upvote_score = min(upvotes * 3, 50)
        
        # Recency bonus
        recency_score = 30
        
        total_score = upvote_score * 0.6 + recency_score * 0.4
        
        return min(total_score, 100)
    
    def _score_space(self, space: Dict) -> float:
        """Score a Hugging Face Space"""
        likes = space.get('likes', 0)
        
        # Normalize likes
        import math
        likes_score = math.log10(likes + 1) * 15 if likes > 0 else 0
        likes_score = min(likes_score, 50)
        
        # Trending spaces get recency bonus
        recency_score = 30
        
        total_score = likes_score * 0.5 + recency_score * 0.5
        
        return min(total_score, 100)
    
    def rank_items(self, items: List[Dict], days_range: int = 1) -> List[Dict]:
        """
        Rank all items and add score to each
        
        Args:
            items: List of content items
            days_range: Number of days for scoring context
        
        Returns:
            Sorted list with scores added
        """
        # Calculate scores
        for item in items:
            score = self.calculate_score(item, days_range)
            item['score'] = score
            item['score_label'] = self._get_score_label(score)
        
        # Sort by score descending
        ranked = sorted(items, key=lambda x: x['score'], reverse=True)
        
        return ranked
    
    def _get_score_label(self, score: float) -> str:
        """Convert score to human-readable label"""
        if score >= 80:
            return "Viral"
        elif score >= 65:
            return "Hot"
        elif score >= 50:
            return "Rising"
        elif score >= 35:
            return "Growing"
        else:
            return "New"
    
    def filter_by_date_range(self, items: List[Dict], days: int) -> List[Dict]:
        """
        Filter items that are within the date range
        
        Args:
            items: List of content items
            days: Number of days to look back
        
        Returns:
            Filtered list of items
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered = []
        for item in items:
            fetched_at = item.get('fetched_at', '')
            if fetched_at:
                try:
                    item_date = datetime.fromisoformat(fetched_at)
                    if item_date >= cutoff_date:
                        filtered.append(item)
                except:
                    # If date parsing fails, include the item
                    filtered.append(item)
            else:
                # No date info, include it
                filtered.append(item)
        
        return filtered
    
    def get_top_items(self, items: List[Dict], limit: int = 50) -> List[Dict]:
        """Get top N items by score"""
        return items[:limit]
    
    def group_by_source(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """Group items by their source"""
        grouped = {}
        
        for item in items:
            source = item.get('source', 'unknown')
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(item)
        
        return grouped
