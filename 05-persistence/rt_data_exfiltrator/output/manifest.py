"""
Manifest generator for tracking exfiltrated data.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import hashlib


class ManifestGenerator:
    """Generates manifests for data exfiltration tracking."""
    
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
    
    def add_entry(self, filepath: str, size: int, checksum: str, 
                  metadata: Optional[Dict] = None) -> None:
        """Add a file entry to the manifest."""
        entry = {
            'filepath': filepath,
            'size': size,
            'checksum': checksum,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.entries.append(entry)
    
    def generate(self) -> Dict[str, Any]:
        """Generate the complete manifest."""
        return {
            'manifest_version': '1.0',
            'created_at': self.created_at.isoformat(),
            'total_files': len(self.entries),
            'total_size': sum(e['size'] for e in self.entries),
            'entries': self.entries
        }
    
    def to_json(self) -> str:
        """Export manifest as JSON."""
        return json.dumps(self.generate(), indent=2)
    
    def save(self, filepath: str) -> None:
        """Save manifest to file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @staticmethod
    def calculate_checksum(filepath: str) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
