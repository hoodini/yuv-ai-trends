"""
Persistent RSS Feed Store for Make.com Integration

This module maintains a persistent store of RSS items so that:
1. Items persist even when they fall off trending lists
2. Each item has a stable pubDate (when first discovered)
3. Make.com can detect truly NEW items via unique GUIDs
4. Items are formatted with title, url, description for Make.com
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import hashlib


class RSSStore:
    """Persistent RSS feed store with deduplication and timestamps"""
    
    def __init__(self, store_path: str = "rss_store.json", max_age_days: int = 30):
        self.store_path = store_path
        self.max_age_days = max_age_days
        self.items: Dict[str, Dict] = {}
        self._load()
    
    def _load(self):
        """Load existing store from disk"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = data.get('items', {})
                    # Clean old items on load
                    self._cleanup_old_items()
            except (json.JSONDecodeError, IOError):
                self.items = {}
    
    def _save(self):
        """Save store to disk"""
        try:
            with open(self.store_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'items': self.items,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Warning: Could not save RSS store: {e}")
    
    def _cleanup_old_items(self):
        """Remove items older than max_age_days"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.max_age_days)
        to_remove = []
        
        for guid, item in self.items.items():
            try:
                item_date = datetime.fromisoformat(item['discovered_at'].replace('Z', '+00:00'))
                if item_date < cutoff:
                    to_remove.append(guid)
            except (KeyError, ValueError):
                pass
        
        for guid in to_remove:
            del self.items[guid]
        
        if to_remove:
            self._save()
    
    def _generate_guid(self, item: Dict) -> str:
        """Generate a unique, stable GUID for an item"""
        # Use URL as primary identifier
        url = item.get('url') or item.get('html_url') or ''
        if url:
            return url
        
        # Fallback: hash of name + source
        name = item.get('name') or item.get('title') or ''
        source = item.get('source', '')
        content = f"{source}:{name}"
        return f"urn:yuv-ai:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    
    def _format_description(self, item: Dict) -> str:
        """Format description for Make.com consumption - clean text only"""
        # Return ONLY the description text, no metadata
        # Make.com template needs clean description for content generation
        desc = item.get('description', '').strip()
        return desc if desc else 'No description available'
    
    def add_items(self, items: List[Dict], digest_type: str = "daily") -> List[Dict]:
        """
        Add items to store, returning list of NEW items (not seen before)
        
        Args:
            items: List of content items from fetchers
            digest_type: 'daily', 'weekly', or 'monthly'
        
        Returns:
            List of items that are genuinely new (first time seen)
        """
        new_items = []
        now = datetime.now(timezone.utc)
        
        for item in items:
            guid = self._generate_guid(item)
            
            if guid not in self.items:
                # This is a NEW item
                # Extract clean repo name (without owner for cleaner titles)
                full_name = item.get('name') or item.get('title') or 'Untitled'
                
                stored_item = {
                    'guid': guid,
                    'title': full_name,  # Full name like "owner/repo"
                    'url': item.get('url') or item.get('html_url') or '',
                    'description': self._format_description(item),
                    'source': item.get('source', 'unknown'),
                    'digest_type': digest_type,
                    'discovered_at': now.isoformat(),
                    'score': item.get('score', 0),
                    # Additional fields for Make.com template
                    'stars': item.get('stars'),
                    'forks': item.get('forks'),
                    'language': item.get('language'),
                    'likes': item.get('likes'),
                    'upvotes': item.get('upvotes'),
                    'ai_summary': item.get('ai_summary'),
                    # Extracted repo name without owner (useful for slugs)
                    'repo_name': full_name.split('/')[-1] if '/' in full_name else full_name,
                    'owner': full_name.split('/')[0] if '/' in full_name else '',
                }
                
                self.items[guid] = stored_item
                new_items.append(stored_item)
        
        if new_items:
            self._save()
        
        return new_items
    
    def get_items(
        self,
        digest_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get items from store, sorted by discovery date (newest first)
        
        Args:
            digest_type: Filter by 'daily', 'weekly', 'monthly' or None for all
            since: Only items discovered after this date
            limit: Maximum number of items to return
        
        Returns:
            List of items sorted by discovery date
        """
        result = []
        
        for guid, item in self.items.items():
            # Filter by digest type
            if digest_type and item.get('digest_type') != digest_type:
                continue
            
            # Filter by date
            if since:
                try:
                    item_date = datetime.fromisoformat(
                        item['discovered_at'].replace('Z', '+00:00')
                    )
                    if item_date < since:
                        continue
                except (KeyError, ValueError):
                    continue
            
            result.append(item)
        
        # Sort by discovery date (newest first)
        result.sort(
            key=lambda x: x.get('discovered_at', ''),
            reverse=True
        )
        
        return result[:limit]
    
    def get_new_items_since(self, since: datetime, digest_type: Optional[str] = None) -> List[Dict]:
        """Get only items discovered after a specific time"""
        return self.get_items(digest_type=digest_type, since=since, limit=100)
    
    def get_stats(self) -> Dict:
        """Get statistics about the store"""
        total = len(self.items)
        by_source = {}
        by_digest = {}
        
        for item in self.items.values():
            source = item.get('source', 'unknown')
            by_source[source] = by_source.get(source, 0) + 1
            
            digest = item.get('digest_type', 'unknown')
            by_digest[digest] = by_digest.get(digest, 0) + 1
        
        # Find oldest and newest
        dates = [item.get('discovered_at') for item in self.items.values() if item.get('discovered_at')]
        
        return {
            'total_items': total,
            'by_source': by_source,
            'by_digest_type': by_digest,
            'oldest_item': min(dates) if dates else None,
            'newest_item': max(dates) if dates else None,
            'store_path': self.store_path
        }
    
    def clear(self):
        """Clear all items (for testing)"""
        self.items = {}
        self._save()


# Global instance
_store: Optional[RSSStore] = None


def get_rss_store() -> RSSStore:
    """Get or create the global RSS store instance"""
    global _store
    if _store is None:
        _store = RSSStore()
    return _store
