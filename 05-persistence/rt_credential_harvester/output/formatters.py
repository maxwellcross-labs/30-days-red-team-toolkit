"""
Output formatters for displaying and exporting results.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class OutputFormatter:
    """Base class for output formatting."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def format_header(self, title: str) -> str:
        """Format a section header."""
        return f"\n{'='*60}\n  {title}\n{'='*60}\n"
    
    def format_item(self, key: str, value: Any) -> str:
        """Format a key-value item."""
        return f"  {key}: {value}"
    
    def format_list(self, items: List[Any]) -> str:
        """Format a list of items."""
        return "\n".join(f"  - {item}" for item in items)
    
    def format_table(self, headers: List[str], rows: List[List[Any]]) -> str:
        """Format data as a table."""
        if not rows:
            return "  No data"
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))
        
        # Build table
        lines = []
        header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        for row in rows:
            row_line = " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            lines.append(row_line)
        
        return "\n".join(lines)


class JSONFormatter(OutputFormatter):
    """Format output as JSON."""
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """Format results as JSON string."""
        import json
        return json.dumps(results, indent=2, default=str)


class TextFormatter(OutputFormatter):
    """Format output as plain text."""
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """Format results as text."""
        lines = []
        for key, value in results.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                lines.append(self.format_list(value))
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


# Convenience function
def get_formatter(format_type: str = 'text', verbose: bool = False) -> OutputFormatter:
    """Get a formatter instance by type."""
    formatters = {
        'text': TextFormatter,
        'json': JSONFormatter,
    }
    formatter_class = formatters.get(format_type.lower(), TextFormatter)
    return formatter_class(verbose=verbose)
