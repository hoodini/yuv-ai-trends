"""HTML generator for the news digest"""

from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import List, Dict
import os
import config


class DigestGenerator:
    """Generate HTML digest from collected content"""
    
    def __init__(self):
        self.template_dir = config.TEMPLATE_DIR
        self.output_dir = config.OUTPUT_DIR
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
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
