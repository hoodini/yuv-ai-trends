"""AI-powered summarizer for generating summaries and explanations"""

import os
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from cache_manager import CacheManager
from local_llm import LocalLLMFallback


class AIContentSummarizer:
    """Generate summaries and trending explanations using various AI providers"""
    
    def __init__(self, api_key: str = None, provider: str = None, model: str = None):
        """
        Initialize with AI API key
        
        Args:
            api_key: Optional API key (can be passed per-request for user-provided keys)
            provider: Optional provider name ('anthropic', 'cohere', 'groq', or 'local_wasm')
            model: Optional model name to use
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.client = None
        
        # Initialize cache manager
        self.cache = CacheManager()
        
        # Initialize local LLM fallback
        self.local_llm = LocalLLMFallback()

        # Determine provider
        if not self.provider:
            provider_pref = os.environ.get("LLM_PROVIDER", "local_wasm").lower()
            if provider_pref in ["anthropic", "cohere", "groq", "local_wasm"]:
                self.provider = provider_pref
            else:
                self.provider = "local_wasm"

        # Initialize the appropriate client
        self._init_client()
    
    def _init_client(self):
        """Initialize the AI client based on provider and API key"""
        if self.provider == "local_wasm" or not self.api_key:
            # Use local LLM - no client needed
            self.client = None
            if self.provider != "local_wasm" and not self.api_key:
                print(f"No API key provided for {self.provider}, falling back to local LLM")
                self.provider = "local_wasm"
            return
            
        try:
            if self.provider == "cohere":
                import cohere
                self.client = cohere.ClientV2(api_key=self.api_key)
            elif self.provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            elif self.provider == "groq":
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
        except Exception as e:
            print(f"Failed to initialize {self.provider} client: {e}")
            self.provider = "local_wasm"
            self.client = None
    
    def generate_summary_and_explanation(self, item: Dict, force_refresh: bool = False) -> Dict:
        """
        Generate one-sentence summary and trending explanation for an item
        
        Args:
            item: Dict containing item data (name, description, source, etc.)
            force_refresh: If True, bypass cache and regenerate summary
        
        Returns:
            Dict with 'summary' and 'trending_reason' keys
        """
        # Check cache first unless force refresh
        if not force_refresh:
            cached_summary = self.cache.get_summary(item)
            if cached_summary:
                return cached_summary
        
        # Build context based on item type
        source = item.get('source', '')
        name = item.get('name', '')
        description = item.get('description', '')
        
        # Additional context based on source
        context_info = []
        if source == 'github_trending':
            stars = item.get('stars', 0)
            stars_today = item.get('stars_today', 0)
            language = item.get('language', '')
            topics = ', '.join(item.get('topics', [])[:5])
            context_info.append(f"GitHub repository with {stars:,} stars (+{stars_today} today)")
            if language:
                context_info.append(f"Language: {language}")
            if topics:
                context_info.append(f"Topics: {topics}")
        
        elif source == 'huggingface_papers':
            upvotes = item.get('upvotes', 0)
            published_date = item.get('published_date', '')
            context_info.append(f"Research paper with {upvotes} upvotes")
            if published_date:
                context_info.append(f"Published: {published_date}")
        
        elif source == 'huggingface_spaces':
            likes = item.get('likes', 0)
            sdk = item.get('sdk', '')
            context_info.append(f"Hugging Face Space with {likes} likes")
            if sdk:
                context_info.append(f"SDK: {sdk}")
        
        context = '\n'.join(context_info)
        
        prompt = f"""You are analyzing trending AI/ML content. Based ONLY on the provided information below, generate a practical, structured analysis:

Project: {name}
Description: {description}
Context: {context}

Generate three sections:

1. WHAT: A clear, concise description (1-2 sentences) of what this project/paper/space actually is - its core technology, framework, or research focus. Be specific and technical.

2. SOLVES: Explain (1-2 sentences) what problem this solves, what use case it addresses, or what gap it fills in the AI/ML ecosystem. Focus on practical applications.

3. HOW: Briefly describe (1-2 sentences) the key technical approach, methodology, or innovative aspect that makes it work or stand out. Include technical details if mentioned in the description.

IMPORTANT: Only describe what is explicitly stated in the description and context. Do not invent or assume features, capabilities, or purposes not mentioned above. If a section cannot be answered from the provided information, state "Details not provided in source material."

Format your response exactly as:
WHAT: [description]
SOLVES: [problem/use case]
HOW: [approach/methodology]"""

        try:
            # If using local_wasm provider, use local LLM directly
            if self.provider == "local_wasm":
                result = self.local_llm.generate_summary(item)
                self.cache.set_summary(item, result)
                return result
            
            if self.provider == "cohere":
                # Use Cohere API
                model = self.model or "command-a-03-2025"
                response = self.client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
                response_text = response.message.content[0].text
            elif self.provider == "anthropic":
                # Use Anthropic API
                model = self.model or "claude-sonnet-4-20250514"
                message = self.client.messages.create(
                    model=model,
                    max_tokens=300,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = message.content[0].text
            elif self.provider == "groq":
                # Use Groq API
                model = self.model or "llama-3.3-70b-versatile"
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7
                )
                response_text = completion.choices[0].message.content
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Parse response
            what = ""
            solves = ""
            how = ""

            lines = response_text.strip().split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if line.startswith('WHAT:'):
                    current_section = 'what'
                    what = line.replace('WHAT:', '').strip()
                elif line.startswith('SOLVES:'):
                    current_section = 'solves'
                    solves = line.replace('SOLVES:', '').strip()
                elif line.startswith('HOW:'):
                    current_section = 'how'
                    how = line.replace('HOW:', '').strip()
                elif current_section == 'what' and line and not line.startswith('SOLVES:') and not line.startswith('HOW:'):
                    what += ' ' + line
                elif current_section == 'solves' and line and not line.startswith('HOW:'):
                    solves += ' ' + line
                elif current_section == 'how' and line:
                    how += ' ' + line

            # Combine into structured summary
            structured_summary = f"**What:** {what.strip()}\n\n**Solves:** {solves.strip()}\n\n**How:** {how.strip()}"

            result = {
                'summary': structured_summary,
                'trending_reason': f"{what.strip()} {solves.strip()}",
                'what': what.strip(),
                'solves': solves.strip(),
                'how': how.strip()
            }
            
            # Cache the result
            self.cache.set_summary(item, result)
            return result
        
        except Exception as e:
            error_str = str(e)
            is_rate_limit = "429" in error_str or "rate limit" in error_str.lower()
            
            if is_rate_limit:
                print(f"Rate limit hit for {name}, using local fallback")
            else:
                print(f"Error generating summary for {name}: {e}")
            
            # Try local LLM fallback
            if self.local_llm.is_available():
                if not is_rate_limit:
                    print(f"  Trying local LLM fallback for {name}...")
                local_result = self.local_llm.generate_summary(item)
                if local_result:
                    self.cache.set_summary(item, local_result)
                    return local_result
            
            # Final fallback
            fallback_what = description[:100] + '...' if len(description) > 100 else description
            fallback_result = {
                'summary': f"**What:** {fallback_what}\n\n**Solves:** Details not available.\n\n**How:** Details not available.",
                'trending_reason': 'Trending in the AI/ML community.',
                'what': fallback_what,
                'solves': 'Details not available.',
                'how': 'Details not available.'
            }
            self.cache.set_summary(item, fallback_result)
            return fallback_result
    
    def enrich_items_batch(self, items: List[Dict], max_workers: int = 3) -> List[Dict]:
        """
        Enrich multiple items with summaries and explanations in parallel
        
        Args:
            items: List of items to enrich
            max_workers: Max number of parallel API calls (reduced for rate limiting)
        
        Returns:
            List of enriched items
        """
        enriched_items = []
        total = len(items)
        processed = 0
        
        # For Cohere trial keys, use very conservative rate limiting
        delay_between_batches = 1.5 if self.provider == "cohere" else 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(self.generate_summary_and_explanation, item): item 
                for item in items
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    item['ai_summary'] = result['summary']
                    item['ai_trending_reason'] = result['trending_reason']
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "rate limit" in error_msg.lower():
                        print(f"⚠️  Rate limit reached. Slowing down...")
                        time.sleep(3)
                    item['ai_summary'] = item.get('description', '')[:100]
                    item['ai_trending_reason'] = 'Trending in the AI/ML community.'
                
                enriched_items.append(item)
                processed += 1
                
                # Show progress
                if processed % 5 == 0:
                    print(f"   Processed {processed}/{total} items...")
                
                # Add delay between batches for rate limiting
                if delay_between_batches > 0 and processed % max_workers == 0:
                    time.sleep(delay_between_batches)
        
        return enriched_items
    
    def get_items_without_summary(self, items: List[Dict]) -> List[Dict]:
        """Get list of items that don't have cached summaries"""
        return self.cache.get_items_without_summary(items)
    
    def populate_missing_summaries(self, items: List[Dict], max_workers: int = 3) -> Dict:
        """Populate summaries for items that don't have them"""
        items_without_summary = self.get_items_without_summary(items)
        
        if not items_without_summary:
            return {
                'total_items': len(items),
                'already_cached': len(items),
                'newly_populated': 0,
                'failed': 0
            }
        
        print(f"Populating {len(items_without_summary)} items without summaries...")
        enriched = self.enrich_items_batch(items_without_summary, max_workers=max_workers)
        successful = sum(1 for item in enriched if item.get('ai_summary'))
        
        return {
            'total_items': len(items),
            'already_cached': len(items) - len(items_without_summary),
            'newly_populated': successful,
            'failed': len(items_without_summary) - successful
        }
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache.get_cache_stats()
