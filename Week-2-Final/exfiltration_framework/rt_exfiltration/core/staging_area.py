#!/usr/bin/env python3
"""
Staging Area Management
Manages temporary staging directory for exfiltration operations
"""

import os
import shutil
from pathlib import Path
from typing import Optional


class StagingArea:
    """
    Manages staging directory for data exfiltration
    """
    
    def __init__(self, session_id: str, base_dir: str = "/tmp"):
        """
        Initialize staging area
        
        Args:
            session_id: Session identifier
            base_dir: Base directory for staging
        """
        self.session_id = session_id
        self.base_dir = Path(base_dir)
        self.staging_dir = self.base_dir / f"exfil_{session_id}"
        
        # Subdirectories
        self.raw_dir = self.staging_dir / "raw"
        self.encrypted_dir = self.staging_dir / "encrypted"
        self.chunks_dir = self.staging_dir / "chunks"
        self.keys_dir = self.staging_dir / "keys"
    
    def create(self) -> None:
        """Create staging directory structure"""
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        self.encrypted_dir.mkdir(exist_ok=True)
        self.chunks_dir.mkdir(exist_ok=True)
        self.keys_dir.mkdir(exist_ok=True)
    
    def get_raw_path(self, filename: str) -> Path:
        """Get path for raw file"""
        return self.raw_dir / filename
    
    def get_encrypted_path(self, filename: str) -> Path:
        """Get path for encrypted file"""
        return self.encrypted_dir / filename
    
    def get_chunk_path(self, filename: str, chunk_index: int) -> Path:
        """Get path for chunk file"""
        return self.chunks_dir / f"{filename}.chunk{chunk_index}"
    
    def get_key_path(self, filename: str) -> Path:
        """Get path for encryption key file"""
        return self.keys_dir / f"{filename}.key"
    
    def list_files(self, directory: str = "raw") -> list:
        """List files in specific directory"""
        if directory == "raw":
            target_dir = self.raw_dir
        elif directory == "encrypted":
            target_dir = self.encrypted_dir
        elif directory == "chunks":
            target_dir = self.chunks_dir
        elif directory == "keys":
            target_dir = self.keys_dir
        else:
            target_dir = self.staging_dir
        
        if target_dir.exists():
            return [f.name for f in target_dir.iterdir() if f.is_file()]
        return []
    
    def get_size(self) -> int:
        """Get total size of staging directory"""
        total = 0
        for root, dirs, files in os.walk(self.staging_dir):
            for file in files:
                filepath = Path(root) / file
                if filepath.exists():
                    total += filepath.stat().st_size
        return total
    
    def cleanup(self, secure: bool = True) -> None:
        """
        Clean up staging directory
        
        Args:
            secure: Perform secure deletion (overwrite before delete)
        """
        if not self.staging_dir.exists():
            return
        
        if secure:
            self._secure_delete_directory(self.staging_dir)
        else:
            shutil.rmtree(self.staging_dir)
    
    def _secure_delete_file(self, filepath: Path) -> None:
        """
        Securely delete a file by overwriting
        
        Args:
            filepath: Path to file
        """
        if not filepath.exists():
            return
        
        # Get file size
        size = filepath.stat().st_size
        
        # Overwrite with random data
        with open(filepath, 'wb') as f:
            f.write(os.urandom(size))
        
        # Delete
        filepath.unlink()
    
    def _secure_delete_directory(self, directory: Path) -> None:
        """
        Securely delete entire directory
        
        Args:
            directory: Path to directory
        """
        # Recursively delete files
        for item in directory.rglob('*'):
            if item.is_file():
                self._secure_delete_file(item)
        
        # Remove empty directories
        shutil.rmtree(directory)
    
    def get_statistics(self) -> dict:
        """Get staging area statistics"""
        return {
            'staging_dir': str(self.staging_dir),
            'exists': self.staging_dir.exists(),
            'total_size': self.get_size(),
            'total_size_mb': self.get_size() / (1024 * 1024),
            'raw_files': len(self.list_files('raw')),
            'encrypted_files': len(self.list_files('encrypted')),
            'chunk_files': len(self.list_files('chunks')),
            'key_files': len(self.list_files('keys'))
        }
