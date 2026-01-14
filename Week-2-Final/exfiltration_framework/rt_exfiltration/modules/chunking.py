#!/usr/bin/env python3
"""
File Chunking Module
Splits files into manageable chunks for exfiltration
"""

import hashlib
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class FileChunk:
    """Represents a file chunk"""
    chunk_index: int
    chunk_path: Path
    size: int
    hash: str
    original_file: str


class FileChunker:
    """
    Splits files into chunks for exfiltration
    """
    
    def __init__(self, chunk_size_mb: int = 10):
        """
        Initialize chunker
        
        Args:
            chunk_size_mb: Chunk size in megabytes
        """
        self.chunk_size_mb = chunk_size_mb
        self.chunk_size_bytes = chunk_size_mb * 1024 * 1024
    
    def chunk_file(self, input_path: Path, output_dir: Path) -> List[FileChunk]:
        """
        Split file into chunks
        
        Args:
            input_path: Path to input file
            output_dir: Directory for chunk output
            
        Returns:
            List of FileChunk objects
        """
        chunks = []
        chunk_index = 0
        
        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Read and split file
        with open(input_path, 'rb') as f:
            while True:
                chunk_data = f.read(self.chunk_size_bytes)
                
                if not chunk_data:
                    break
                
                # Create chunk file
                chunk_filename = f"{input_path.name}.chunk{chunk_index}"
                chunk_path = output_dir / chunk_filename
                
                # Write chunk
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                
                # Calculate chunk hash
                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                
                # Create chunk object
                chunk = FileChunk(
                    chunk_index=chunk_index,
                    chunk_path=chunk_path,
                    size=len(chunk_data),
                    hash=chunk_hash,
                    original_file=str(input_path)
                )
                
                chunks.append(chunk)
                chunk_index += 1
        
        return chunks
    
    def reassemble_file(self, chunks: List[FileChunk], output_path: Path) -> None:
        """
        Reassemble chunks into original file
        
        Args:
            chunks: List of FileChunk objects
            output_path: Path for reassembled file
        """
        # Sort chunks by index
        sorted_chunks = sorted(chunks, key=lambda x: x.chunk_index)
        
        # Reassemble
        with open(output_path, 'wb') as output_file:
            for chunk in sorted_chunks:
                with open(chunk.chunk_path, 'rb') as chunk_file:
                    output_file.write(chunk_file.read())
    
    def verify_chunks(self, chunks: List[FileChunk]) -> bool:
        """
        Verify chunk integrity
        
        Args:
            chunks: List of FileChunk objects
            
        Returns:
            True if all chunks are valid
        """
        for chunk in chunks:
            # Recalculate hash
            with open(chunk.chunk_path, 'rb') as f:
                data = f.read()
                calculated_hash = hashlib.sha256(data).hexdigest()
            
            if calculated_hash != chunk.hash:
                return False
        
        return True
    
    def get_chunk_info(self, chunks: List[FileChunk]) -> Dict:
        """
        Get information about chunks
        
        Args:
            chunks: List of FileChunk objects
            
        Returns:
            Dictionary with chunk information
        """
        total_size = sum(chunk.size for chunk in chunks)
        
        return {
            'total_chunks': len(chunks),
            'chunk_size_mb': self.chunk_size_mb,
            'total_size': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'chunks': [
                {
                    'index': chunk.chunk_index,
                    'size': chunk.size,
                    'hash': chunk.hash,
                    'path': str(chunk.chunk_path)
                }
                for chunk in chunks
            ]
        }
