"""AI-powered summarizer for generating summaries and explanations"""

import os
import time
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed


class AIContentSummarizer:
    """Generate summaries and trending explanations using Claude or Cohere API"""
    
    def __init__(self, api_key: str = None, provider: str = None):
        """
        Initialize with AI API key
        
        Args:
            api_key: Optional API key (will auto-detect from environment if not provided)
            provider: Optional provider name ('anthropic' or 'cohere'). Auto-detects if not provided.
        """
        # Auto-detect provider and API key
        self.provider = provider
        self.api_key = api_key
        self.client = None

        if not self.provider:
            # Check which API key is available, prefer setting from LLM_PROVIDER env var
            provider_pref = os.environ.get("LLM_PROVIDER", "").lower()
            if provider_pref in ["anthropic", "cohere", "groq"]:
                self.provider = provider_pref
            elif os.environ.get("COHERE_API_KEY"):
                self.provider = "cohere"
            elif os.environ.get("ANTHROPIC_API_KEY"):
                self.provider = "anthropic"
            elif os.environ.get("GROQ_API_KEY"):
                self.provider = "groq"
            else:
                raise ValueError("No API key found. Please set ANTHROPIC_API_KEY, COHERE_API_KEY, or GROQ_API_KEY in environment variables.")

        # Initialize the appropriate client
        if self.provider == "cohere":
            import cohere
            self.api_key = self.api_key or os.environ.get("COHERE_API_KEY")
            if not self.api_key:
                raise ValueError("COHERE_API_KEY not found. Please set it in environment variables.")
            self.client = cohere.ClientV2(api_key=self.api_key)
            print(f"Using Cohere API for AI summaries")
        elif self.provider == "anthropic":
            import anthropic
            self.api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found. Please set it in environment variables.")
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print(f"Using Anthropic Claude API for AI summaries")
        elif self.provider == "groq":
            from groq import Groq
            self.api_key = self.api_key or os.environ.get("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not found. Please set it in environment variables.")
            self.client = Groq(api_key=self.api_key)
            print(f"Using Groq API for AI summaries")
        else:
            raise ValueError(f"Unknown provider: {self.provider}. Use 'anthropic', 'cohere', or 'groq'.")
    
    def generate_summary_and_explanation(self, item: Dict) -> Dict:
        """
        Generate one-sentence summary and trending explanation for an item
        
        Args:
            item: Dict containing item data (name, description, source, etc.)
        
        Returns:
            Dict with 'summary' and 'trending_reason' keys
        """
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
            # Get model from environment or use default
            model = os.environ.get("LLM_MODEL", "")

            if self.provider == "cohere":
                # Use Cohere API
                if not model:
                    model = "command-a-03-2025"
                response = self.client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )
                response_text = response.message.content[0].text
            elif self.provider == "anthropic":
                # Use Anthropic API
                if not model:
                    model = "claude-sonnet-4-20250514"
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
                if not model:
                    model = "llama-3.3-70b-versatile"
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

            return {
                'summary': structured_summary,
                'trending_reason': f"{what.strip()} {solves.strip()}",  # Backward compatibility
                'what': what.strip(),
                'solves': solves.strip(),
                'how': how.strip()
            }
        
        except Exception as e:
            print(f"Error generating summary for {name}: {e}")
            fallback_what = description[:100] + '...' if len(description) > 100 else description
            return {
                'summary': f"**What:** {fallback_what}\n\n**Solves:** Details not available.\n\n**How:** Details not available.",
                'trending_reason': 'Trending in the AI/ML community.',
                'what': fallback_what,
                'solves': 'Details not available.',
                'how': 'Details not available.'
            }
    
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
