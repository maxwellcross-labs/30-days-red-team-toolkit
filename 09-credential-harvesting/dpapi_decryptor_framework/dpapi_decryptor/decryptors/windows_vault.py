#!/usr/bin/env python3
"""
Windows Credential Vault Decryptor
Extract information from Windows Credential Manager
"""

import subprocess
from pathlib import Path
from typing import List, Dict


class WindowsVaultDecryptor:
    """
    Extract Windows Credential Vault information
    
    Method: vaultcmd.exe
    Encryption: DPAPI (requires additional tools for full decryption)
    """
    
    DECRYPTOR_NAME = "windows_vault"
    REQUIRES_ADMIN = False
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
    
    def decrypt(self) -> List[Dict]:
        """
        Extract Windows Vault credentials
        
        Note: Passwords are DPAPI-encrypted, only metadata extracted
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Extracting Windows Credential Vault information...")
        
        credentials = []
        
        try:
            # Use vaultcmd to list credentials
            cmd = 'vaultcmd /listcreds:"Windows Credentials" /all'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                print(f"[+] Windows Vault credentials found")
                print(f"\n{output}")
                
                # Save full output
                output_file = self.output_dir / "windows_vault.txt"
                with open(output_file, 'w') as f:
                    f.write("WINDOWS CREDENTIAL VAULT\n")
                    f.write("="*70 + "\n\n")
                    f.write(output)
                
                print(f"\n[+] Full output saved to: {output_file}")
                
                # Parse credentials (basic parsing)
                current_cred = None
                for line in output.split('\n'):
                    line = line.strip()
                    
                    if 'Credential' in line and ':' in line:
                        if current_cred:
                            credentials.append(current_cred)
                        current_cred = {'source': 'Windows Vault'}
                    
                    elif current_cred:
                        if 'Target:' in line:
                            current_cred['target'] = line.split(':', 1)[1].strip()
                        elif 'Type:' in line:
                            current_cred['type'] = line.split(':', 1)[1].strip()
                        elif 'User:' in line:
                            current_cred['username'] = line.split(':', 1)[1].strip()
                
                if current_cred:
                    credentials.append(current_cred)
                
                print(f"\n[!] Note: Passwords are DPAPI-encrypted")
                print(f"[!] Use mimikatz or SharpDPAPI for full decryption:")
                print(f"[!]   mimikatz# vault::list")
                print(f"[!]   mimikatz# vault::cred")
            else:
                print(f"[-] vaultcmd failed or no credentials found")
        
        except subprocess.TimeoutExpired:
            print(f"[-] vaultcmd timed out")
        
        except Exception as e:
            print(f"[-] Windows Vault extraction failed: {e}")
        
        return credentials
    
    def is_available(self) -> bool:
        """Check if vaultcmd is available"""
        try:
            result = subprocess.run(
                'vaultcmd /?',
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
            'name': 'windows_vault',
            'description': 'Extract Windows Credential Vault information',
            'requires_admin': False,
            'method': 'vaultcmd.exe',
            'encryption': 'DPAPI (full decryption requires additional tools)',
            'credential_types': [
                'Windows credentials',
                'Generic credentials',
                'Domain credentials',
                'Certificate-based credentials'
            ],
            'notes': [
                'Extracts metadata from Windows Credential Manager',
                'Passwords are DPAPI-encrypted',
                'Full decryption requires mimikatz or SharpDPAPI',
                'Current user credentials only'
            ],
            'requirements': [
                'vaultcmd.exe (built-in Windows tool)'
            ],
            'decryption_tools': [
                'mimikatz: vault::list, vault::cred',
                'SharpDPAPI: SharpDPAPI.exe vaults',
                'VaultPasswordView (NirSoft)'
            ]
        }
