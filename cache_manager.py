"""Persistent cache manager for AI summaries and item descriptions"""

import json
import os
import hashlib
from typing import Dict, Optional, List
from datetime import datetime


class CacheManager:
    """Manages persistent caching of AI-generated summaries"""
    
    def __init__(self, cache_file: str = "summary_cache.json"):
        """
        Initialize cache manager
        
        Args:
            cache_file: Path to the JSON cache file
        """
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            # Create a copy to avoid "dictionary changed size during iteration" error
            cache_copy = dict(self.cache)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_copy, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def _generate_key(self, item: Dict) -> str:
        """
        Generate a unique cache key for an item
        
        Args:
            item: Item dictionary
            
        Returns:
            Unique hash key
        """
        # Use source + name/id as the unique identifier
        source = item.get('source', '')
        name = item.get('name', '')
        url = item.get('url', '')
        
        # Create a unique string
        unique_str = f"{source}:{name}:{url}"
        
        # Generate hash
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()
    
    def get_summary(self, item: Dict) -> Optional[Dict]:
        """
        Get cached summary for an item
        
        Args:
            item: Item dictionary
            
        Returns:
            Cached summary dict or None if not found/invalid
        """
        key = self._generate_key(item)
        cached = self.cache.get(key)
        
        if cached:
            # Skip cached entries with empty 'what' field (bad cache entries)
            what_value = cached.get('what', '')
            if not what_value or what_value.strip() == '':
                # Remove invalid cache entry
                del self.cache[key]
                self._save_cache()
                return None
            
            # Return the summary data
            return {
                'what': what_value,
                'solves': cached.get('solves', ''),
                'how': cached.get('how', ''),
                'summary': cached.get('summary', ''),
                'trending_reason': cached.get('trending_reason', ''),
                'cached': True,
                'cached_at': cached.get('cached_at', '')
            }
        
        return None
    
    def set_summary(self, item: Dict, summary_data: Dict):
        """
        Cache a summary for an item
        
        Args:
            item: Item dictionary
            summary_data: Summary data to cache
        """
        key = self._generate_key(item)
        
        # Store with timestamp
        self.cache[key] = {
            'what': summary_data.get('what', ''),
            'solves': summary_data.get('solves', ''),
            'how': summary_data.get('how', ''),
            'summary': summary_data.get('summary', ''),
            'trending_reason': summary_data.get('trending_reason', ''),
            'cached_at': datetime.now().isoformat(),
            'source': item.get('source', ''),
            'name': item.get('name', ''),
            'url': item.get('url', '')
        }
        
        self._save_cache()
    
    def has_summary(self, item: Dict) -> bool:
        """
        Check if item has a cached summary
        
        Args:
            item: Item dictionary
            
        Returns:
            True if cached summary exists
        """
        key = self._generate_key(item)
        return key in self.cache
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the cache"""
        return {
            'total_cached': len(self.cache),
            'sources': self._count_by_source()
        }
    
    def _count_by_source(self) -> Dict[str, int]:
        """Count cached items by source"""
        counts = {}
        for entry in self.cache.values():
            source = entry.get('source', 'unknown')
            counts[source] = counts.get(source, 0) + 1
        return counts
    
    def clear_cache(self):
        """Clear all cached summaries"""
        self.cache = {}
        self._save_cache()
    
    def get_items_without_summary(self, items: List[Dict]) -> List[Dict]:
        """
        Filter items that don't have cached summaries
        
        Args:
            items: List of item dictionaries
            
        Returns:
            List of items without cached summaries
        """
        return [item for item in items if not self.has_summary(item)]
