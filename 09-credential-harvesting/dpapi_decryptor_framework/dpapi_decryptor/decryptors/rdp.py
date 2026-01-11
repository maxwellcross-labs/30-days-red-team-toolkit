#!/usr/bin/env python3
"""
RDP Credential Decryptor
Extract saved RDP credentials from Windows
"""

import subprocess
from typing import List, Dict
from pathlib import Path


class RDPDecryptor:
    """
    Extract RDP saved credentials
    
    Method: cmdkey.exe
    Location: Windows Credential Manager
    Encryption: DPAPI (passwords not directly accessible)
    """
    
    DECRYPTOR_NAME = "rdp"
    REQUIRES_ADMIN = False
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
    
    def decrypt(self) -> List[Dict]:
        """
        Extract RDP credentials
        
        Note: Only lists targets, passwords require additional tools
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Extracting RDP saved credentials...")
        
        credentials = []
        
        try:
            # Use cmdkey to list saved credentials
            cmd = "cmdkey /list"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse RDP credentials (TERMSRV entries)
                rdp_found = False
                
                for line in output.split('\n'):
                    if 'Target:' in line and 'TERMSRV' in line:
                        target = line.split('Target:')[1].strip()
                        
                        cred = {
                            'source': 'RDP Saved Connection',
                            'target': target,
                            'type': 'Domain:target=TERMSRV',
                            'password_status': 'DPAPI-encrypted in Credential Manager'
                        }
                        
                        credentials.append(cred)
                        rdp_found = True
                        
                        print(f"[+] Found RDP credential:")
                        print(f"    Target: {target}")
                
                if not rdp_found:
                    print(f"[-] No RDP credentials found")
                else:
                    # Save output
                    output_file = self.output_dir / "rdp_credentials.txt"
                    with open(output_file, 'w') as f:
                        f.write("RDP SAVED CREDENTIALS\n")
                        f.write("="*70 + "\n\n")
                        f.write(output)
                    
                    print(f"\n[+] Full output saved to: {output_file}")
                    
                    print(f"\n[!] Note: RDP passwords are DPAPI-encrypted")
                    print(f"[!] Use mimikatz for full decryption:")
                    print(f"[!]   mimikatz# dpapi::cred /in:<cred_file>")
                    print(f"[!]   or SharpDPAPI.exe credentials")
            else:
                print(f"[-] cmdkey failed")
        
        except subprocess.TimeoutExpired:
            print(f"[-] cmdkey timed out")
        
        except Exception as e:
            print(f"[-] RDP credential extraction failed: {e}")
        
        return credentials
    
    def is_available(self) -> bool:
        """Check if cmdkey is available"""
        try:
            result = subprocess.run(
                'cmdkey /?',
                shell=True,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this decryptor"""
        return {
            'name': 'rdp',
            'description': 'Extract RDP saved credentials',
            'requires_admin': False,
            'method': 'cmdkey.exe',
            'location': 'Windows Credential Manager',
            'encryption': 'DPAPI (passwords not directly accessible)',
            'credential_types': ['RDP connection credentials'],
            'notes': [
                'Lists RDP saved connections',
                'Passwords stored in Credential Manager',
                'Passwords are DPAPI-encrypted',
                'Full decryption requires mimikatz or SharpDPAPI',
                'Current user credentials only'
            ],
            'requirements': [
                'cmdkey.exe (built-in Windows tool)'
            ],
            'decryption_tools': [
                'mimikatz: dpapi::cred',
                'SharpDPAPI: SharpDPAPI.exe credentials',
                'Manual: Credential files in %USERPROFILE%\\AppData\\Local\\Microsoft\\Credentials'
            ]
        }
