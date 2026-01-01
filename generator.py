"""HTML generator for the news digest"""

from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import List, Dict
import os
import config


class DigestGenerator:
    """Generate HTML digest from collected content"""
    
    def __init__(self, use_ai_summaries: bool = True):
        self.template_dir = config.TEMPLATE_DIR
        self.output_dir = config.OUTPUT_DIR
        self.use_ai_summaries = use_ai_summaries
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Initialize AI summarizer if enabled
        self.summarizer = None
        if use_ai_summaries:
            try:
                from summarizer import AIContentSummarizer
                self.summarizer = AIContentSummarizer()
            except Exception as e:
                print(f"WARNING: AI summarizer not available: {e}")
                self.use_ai_summaries = False
    
    def generate(
        self,
        items: List[Dict],
        grouped_items: Dict[str, List[Dict]],
        time_range: str = "daily",
        output_filename: str = None
    ) -> str:
        """
        Generate HTML digest
        
        Args:
            items: All items (for stats)
            grouped_items: Items grouped by source
            time_range: Time range label (daily/weekly/monthly)
            output_filename: Optional custom output filename
        
        Returns:
            Path to the generated HTML file
        """
        # Enrich items with AI summaries if enabled
        if self.use_ai_summaries and self.summarizer:
            self.enrich_data(grouped_items)
        
        # Calculate statistics
        stats = self._calculate_stats(grouped_items)
        
        # Prepare template data
        template_data = {
            'date': datetime.now().strftime('%B %d, %Y'),
            'time_range': time_range.capitalize(),
            'stats': stats,
            'grouped_items': grouped_items,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Render template
        template = self.env.get_template('digest.html')
        html_content = template.render(**template_data)
        
        # Generate output filename
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"digest_{time_range}_{timestamp}.html"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def enrich_data(self, grouped_items: Dict[str, List[Dict]]) -> None:
        """Enrich items with AI summaries in-place"""
        if not self.use_ai_summaries or not self.summarizer:
            return

        print("Generating AI summaries and explanations...")
        all_items_flat = []
        for source_items in grouped_items.values():
            all_items_flat.extend(source_items)
        
        enriched = self.summarizer.enrich_items_batch(all_items_flat, max_workers=5)
        
        # Update grouped_items with enriched data
        enriched_map = {item['url']: item for item in enriched}
        for source, source_items in grouped_items.items():
            for item in source_items:
                if item['url'] in enriched_map:
                    item.update(enriched_map[item['url']])
    
    def _calculate_stats(self, grouped_items: Dict[str, List[Dict]]) -> Dict:
        """Calculate statistics from grouped items"""
        stats = {
            'total_items': sum(len(items) for items in grouped_items.values()),
            'github_repos': len(grouped_items.get('github_trending', [])),
            'github_collections': len(grouped_items.get('github_explore', [])),
            'papers': len(grouped_items.get('huggingface_papers', [])),
            'spaces': len(grouped_items.get('huggingface_spaces', [])),
        }
        
        return stats
