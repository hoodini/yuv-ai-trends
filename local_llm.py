"""Local WebLLM fallback for when API calls fail"""

import os
from typing import Dict, Optional


class LocalLLMFallback:
    """Provides local LLM inference as fallback when API fails"""
    
    def __init__(self):
        """Initialize local LLM (always available as fallback)"""
        # Always mark as available - will provide basic fallback summaries
        self.available = True
        self.model_name = os.environ.get("LLM_MODEL", "phi-3-mini")
        self.client = None
        print("Local LLM fallback initialized (basic mode)")
    
    def generate_summary(self, item: Dict) -> Optional[Dict]:
        """
        Generate summary using local LLM (basic fallback mode)
        
        Args:
            item: Item dictionary
            
        Returns:
            Summary dict with basic information from item description
        """
        name = item.get('name', '')
        description = item.get('description', '')
        source = item.get('source', '')
        language = item.get('language', '')
        sdk = item.get('sdk', '')
        likes = item.get('likes', 0)
        stars = item.get('stars', 0)
        upvotes = item.get('upvotes', 0)
        
        # Build a comprehensive "What" description
        if description and description.strip():
            # Use the full description for What
            what_text = description.strip()
        else:
            # If no description, create one from metadata
            parts = []
            
            # Format name nicely
            display_name = name.split('/')[-1] if '/' in name else name
            
            if source == 'github_trending':
                parts.append(f"{display_name} - A trending GitHub repository")
                if language:
                    parts.append(f"written in {language}")
                if stars:
                    parts.append(f"with {stars:,} stars")
            elif source == 'huggingface_papers':
                parts.append(f"{name} - A research paper")
                if upvotes:
                    parts.append(f"with {upvotes} upvotes on Hugging Face")
            elif source == 'huggingface_spaces':
                parts.append(f"{display_name} - A Hugging Face Space")
                if sdk:
                    parts.append(f"built with {sdk}")
                if likes:
                    parts.append(f"({likes:,} likes)")
            else:
                parts.append(name)
                
            what_text = ' '.join(parts) if parts else name
        
        # Infer purpose from description or name with better logic
        solves_text = "Details not available in source material."
        
        # Use description or name for inference
        text_to_analyze = description.lower() if description else name.lower()
        
        if text_to_analyze:
            # More sophisticated keyword matching
            if any(word in text_to_analyze for word in ['train', 'training', 'fine-tune', 'finetune']):
                solves_text = "Helps train and fine-tune machine learning models."
            elif any(word in text_to_analyze for word in ['dataset', 'data processing', 'data pipeline']):
                solves_text = "Manages and processes data for ML workflows."
            elif any(word in text_to_analyze for word in ['inference', 'deploy', 'serve', 'production']):
                solves_text = "Deploys and serves models in production environments."
            elif any(word in text_to_analyze for word in ['framework', 'library', 'sdk']):
                solves_text = "Provides reusable components and tools for developers."
            elif any(word in text_to_analyze for word in ['leaderboard', 'benchmark', 'eval']):
                solves_text = "Provides benchmarking and evaluation for ML models."
            elif any(word in text_to_analyze for word in ['diffusion', 'flux', 'stable', 'image', 'vision', 'video', 'visual', 'comic', 'art', 'dalle', 'midjourney']):
                solves_text = "Generates or processes visual content using AI."
            elif any(word in text_to_analyze for word in ['music', 'audio', 'sound', 'voice', 'speech', 'tts']):
                solves_text = "Generates or processes audio content using AI."
            elif any(word in text_to_analyze for word in ['chat', 'assistant', 'agent', 'bot', 'llm', 'gpt', 'claude']):
                solves_text = "Enables conversational AI and intelligent assistance."
            elif any(word in text_to_analyze for word in ['try-on', 'virtual', 'fashion', 'clothing']):
                solves_text = "Provides virtual try-on or fashion visualization."
            elif any(word in text_to_analyze for word in ['model', 'ai', 'ml', 'neural', 'transformer']):
                solves_text = "Advances AI/ML capabilities and research."
            elif any(word in text_to_analyze for word in ['api', 'server', 'backend', 'service']):
                solves_text = "Provides backend services and API infrastructure."
            elif any(word in text_to_analyze for word in ['ui', 'interface', 'frontend', 'web app', 'dashboard']):
                solves_text = "Delivers user interface and visualization capabilities."
            elif any(word in text_to_analyze for word in ['text', 'nlp', 'language', 'translation']):
                solves_text = "Handles natural language processing tasks."
            elif source == 'huggingface_spaces':
                # Default for spaces without other hints
                solves_text = "Provides an interactive demo of AI/ML capabilities."
            elif source == 'github_trending':
                solves_text = "Open-source project gaining traction in the developer community."
        
        # Try to extract technical approach from description, name, and metadata
        how_text = "Technical details not provided in source material."
        tech_keywords = []
        
        # Use description or name for inference
        text_to_analyze = (description.lower() if description else '') + ' ' + name.lower()
        
        if 'pytorch' in text_to_analyze or 'torch' in text_to_analyze:
            tech_keywords.append('PyTorch')
        if 'tensorflow' in text_to_analyze or 'keras' in text_to_analyze:
            tech_keywords.append('TensorFlow')
        if 'transformers' in text_to_analyze or 'huggingface' in text_to_analyze:
            tech_keywords.append('Transformers')
        if 'docker' in text_to_analyze or 'container' in text_to_analyze:
            tech_keywords.append('Docker')
        if 'api' in text_to_analyze:
            tech_keywords.append('REST API')
        if 'react' in text_to_analyze:
            tech_keywords.append('React')
        if 'python' in text_to_analyze or language == 'Python':
            tech_keywords.append('Python')
        if 'typescript' in text_to_analyze or language == 'TypeScript':
            tech_keywords.append('TypeScript')
        if 'gradio' in text_to_analyze or sdk == 'gradio':
            tech_keywords.append('Gradio')
        if 'streamlit' in text_to_analyze or sdk == 'streamlit':
            tech_keywords.append('Streamlit')
        if sdk == 'docker':
            tech_keywords.append('Docker')
        if 'diffusion' in text_to_analyze:
            tech_keywords.append('Diffusion models')
        if 'llm' in text_to_analyze or 'gpt' in text_to_analyze:
            tech_keywords.append('Large Language Models')
        
        if tech_keywords:
            # Remove duplicates while preserving order
            seen = set()
            unique_keywords = []
            for kw in tech_keywords:
                if kw.lower() not in seen:
                    seen.add(kw.lower())
                    unique_keywords.append(kw)
            how_text = f"Built using {', '.join(unique_keywords[:3])} and related technologies."
        elif source == 'huggingface_spaces':
            how_text = "Deployed as an interactive demo on Hugging Face Spaces."
        elif source == 'huggingface_papers':
            how_text = "Academic research paper with peer-reviewed methodology."
        elif source == 'github_trending':
            how_text = "Open-source implementation available on GitHub."
        
        return {
            'what': what_text,
            'solves': solves_text,
            'how': how_text,
            'summary': f"**What:** {what_text}\n\n**Solves:** {solves_text}\n\n**How:** {how_text}",
            'trending_reason': what_text[:150] if len(what_text) > 150 else what_text,
            'fallback': True,
            'fallback_reason': 'Local LLM fallback (API unavailable or rate limited)'
        }
    
    def is_available(self) -> bool:
        """Check if local LLM is available"""
        return self.available
