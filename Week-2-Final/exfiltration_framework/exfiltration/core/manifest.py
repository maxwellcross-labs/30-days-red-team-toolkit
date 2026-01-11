#!/usr/bin/env python3
"""
Exfiltration Manifest
Tracks complete exfiltration operation state and metadata
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class Manifest:
    """
    Maintains complete exfiltration operation manifest
    """
    
    def __init__(self, session_id: str):
        """
        Initialize manifest
        
        Args:
            session_id: Session identifier
        """
        self.session_id = session_id
        self.started = datetime.now()
        self.completed = None
        
        self.files = []
        self.chunks = []
        self.transfers = []
        
        self.metadata = {
            'session_id': session_id,
            'started': self.started.isoformat(),
            'version': '1.0.0'
        }
    
    def add_file(self, file_info: Dict) -> None:
        """Add file to manifest"""
        file_info['added_to_manifest'] = datetime.now().isoformat()
        self.files.append(file_info)
    
    def add_chunk(self, chunk_info: Dict) -> None:
        """Add chunk to manifest"""
        chunk_info['added_to_manifest'] = datetime.now().isoformat()
        self.chunks.append(chunk_info)
    
    def add_transfer(self, transfer_info: Dict) -> None:
        """Add transfer record to manifest"""
        transfer_info['recorded'] = datetime.now().isoformat()
        self.transfers.append(transfer_info)
    
    def update_file_status(self, original_path: str, status_updates: Dict) -> None:
        """
        Update file status
        
        Args:
            original_path: Original file path
            status_updates: Dictionary of status updates
        """
        for file_info in self.files:
            if file_info.get('original_path') == original_path:
                file_info.update(status_updates)
                break
    
    def get_file_by_path(self, original_path: str) -> Optional[Dict]:
        """Get file info by original path"""
        for file_info in self.files:
            if file_info.get('original_path') == original_path:
                return file_info
        return None
    
    def get_statistics(self) -> Dict:
        """Get manifest statistics"""
        elapsed = (datetime.now() - self.started).total_seconds()
        
        return {
            'session_id': self.session_id,
            'started': self.started.isoformat(),
            'completed': self.completed.isoformat() if self.completed else None,
            'elapsed_seconds': elapsed,
            'total_files': len(self.files),
            'total_chunks': len(self.chunks),
            'total_transfers': len(self.transfers),
            'successful_transfers': len([t for t in self.transfers if t.get('status') == 'complete']),
            'failed_transfers': len([t for t in self.transfers if t.get('status') == 'failed']),
            'pending_transfers': len([t for t in self.transfers if t.get('status') == 'pending'])
        }
    
    def finalize(self) -> None:
        """Mark manifest as complete"""
        self.completed = datetime.now()
        self.metadata['completed'] = self.completed.isoformat()
        self.metadata['duration_seconds'] = (self.completed - self.started).total_seconds()
    
    def save(self, output_path: Path) -> None:
        """
        Save manifest to JSON file
        
        Args:
            output_path: Path to save manifest
        """
        manifest_data = {
            'metadata': self.metadata,
            'statistics': self.get_statistics(),
            'files': self.files,
            'chunks': self.chunks,
            'transfers': self.transfers
        }
        
        with open(output_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
    
    @classmethod
    def load(cls, input_path: Path) -> 'Manifest':
        """
        Load manifest from JSON file
        
        Args:
            input_path: Path to manifest file
            
        Returns:
            Manifest object
        """
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        manifest = cls(session_id=data['metadata']['session_id'])
        
        if data['metadata'].get('started'):
            manifest.started = datetime.fromisoformat(data['metadata']['started'])
        
        if data['metadata'].get('completed'):
            manifest.completed = datetime.fromisoformat(data['metadata']['completed'])
        
        manifest.files = data.get('files', [])
        manifest.chunks = data.get('chunks', [])
        manifest.transfers = data.get('transfers', [])
        manifest.metadata = data.get('metadata', {})
        
        return manifest
    
    def generate_report(self) -> str:
        """Generate human-readable manifest report"""
        stats = self.get_statistics()
        
        report = f"""
{'='*60}
EXFILTRATION MANIFEST REPORT
Session: {self.session_id}
{'='*60}

TIMELINE
Started: {self.started.strftime('%Y-%m-%d %H:%M:%S')}
Completed: {self.completed.strftime('%Y-%m-%d %H:%M:%S') if self.completed else 'In Progress'}
Duration: {stats['elapsed_seconds']:.0f} seconds

FILES
Total: {stats['total_files']}
Chunks: {stats['total_chunks']}

TRANSFERS
Total: {stats['total_transfers']}
Successful: {stats['successful_transfers']}
Failed: {stats['failed_transfers']}
Pending: {stats['pending_transfers']}

"""
        
        if self.files:
            report += f"FILE DETAILS\n"
            report += "="*60 + "\n"
            for file_info in self.files:
                report += f"\n  • {file_info.get('original_path', 'Unknown')}\n"
                report += f"    Size: {file_info.get('size', 0)} bytes\n"
                report += f"    Hash: {file_info.get('hash', 'N/A')}\n"
                if file_info.get('chunks'):
                    report += f"    Chunks: {len(file_info.get('chunks', []))}\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report
