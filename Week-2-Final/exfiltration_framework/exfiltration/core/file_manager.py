#!/usr/bin/env python3
"""
File Manager
Handles file collection, hashing, and tracking
"""

import os
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict


@dataclass
class TrackedFile:
    """Represents a tracked file for exfiltration"""
    original_path: str
    local_path: str
    size: int
    hash: str
    collected: datetime = field(default_factory=datetime.now)
    
    # Processing status
    encrypted: bool = False
    chunked: bool = False
    transferred: bool = False
    
    # Chunk information
    chunks: list = field(default_factory=list)
    encryption_key_file: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'original_path': self.original_path,
            'local_path': self.local_path,
            'size': self.size,
            'hash': self.hash,
            'collected': self.collected.isoformat(),
            'encrypted': self.encrypted,
            'chunked': self.chunked,
            'transferred': self.transferred,
            'chunks': self.chunks,
            'encryption_key_file': self.encryption_key_file
        }


class FileManager:
    """
    Manages file collection and tracking
    """
    
    def __init__(self, staging_dir: str):
        """
        Initialize file manager
        
        Args:
            staging_dir: Directory for staging files
        """
        self.staging_dir = staging_dir
        self.tracked_files = []
    
    def calculate_hash(self, filepath: str, algorithm: str = 'sha256') -> str:
        """
        Calculate file hash for integrity verification
        
        Args:
            filepath: Path to file
            algorithm: Hash algorithm (sha256, md5, sha1)
            
        Returns:
            Hex digest of file hash
        """
        if algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha1':
            hasher = hashlib.sha1()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        with open(filepath, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                hasher.update(byte_block)
        
        return hasher.hexdigest()
    
    def collect_file(self, original_path: str) -> TrackedFile:
        """
        Collect a file to staging area
        
        Args:
            original_path: Original file path
            
        Returns:
            TrackedFile object
        """
        # Determine local path in staging
        filename = os.path.basename(original_path)
        local_path = os.path.join(self.staging_dir, filename)
        
        # In production, this would download via C2
        # For now, assume file is already in staging
        
        # Calculate file size and hash
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            file_hash = self.calculate_hash(local_path)
        else:
            # Simulated for files not yet downloaded
            size = 0
            file_hash = "pending"
        
        # Create tracked file
        tracked = TrackedFile(
            original_path=original_path,
            local_path=local_path,
            size=size,
            hash=file_hash
        )
        
        self.tracked_files.append(tracked)
        return tracked
    
    def collect_files(self, file_list: list) -> list:
        """
        Collect multiple files
        
        Args:
            file_list: List of file paths
            
        Returns:
            List of TrackedFile objects
        """
        collected = []
        for filepath in file_list:
            tracked = self.collect_file(filepath)
            collected.append(tracked)
        
        return collected
    
    def get_tracked_file(self, original_path: str) -> Optional[TrackedFile]:
        """Get tracked file by original path"""
        for tracked in self.tracked_files:
            if tracked.original_path == original_path:
                return tracked
        return None
    
    def get_all_files(self) -> list:
        """Get all tracked files"""
        return self.tracked_files
    
    def get_total_size(self) -> int:
        """Get total size of all tracked files"""
        return sum(f.size for f in self.tracked_files)
    
    def get_statistics(self) -> Dict:
        """Get file collection statistics"""
        return {
            'total_files': len(self.tracked_files),
            'total_size': self.get_total_size(),
            'total_size_mb': self.get_total_size() / (1024 * 1024),
            'encrypted': len([f for f in self.tracked_files if f.encrypted]),
            'chunked': len([f for f in self.tracked_files if f.chunked]),
            'transferred': len([f for f in self.tracked_files if f.transferred])
        }
