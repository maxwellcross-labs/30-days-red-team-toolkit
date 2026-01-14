#!/usr/bin/env python3
"""
RDP Credential Miner
Extract saved RDP connection information
"""

import winreg
from typing import List, Dict

from ..utils import safe_open_key, safe_query_value, enumerate_subkeys


class RDPMiner:
    """
    Extract saved RDP connection information
    
    Location: HKCU\Software\Microsoft\Terminal Server Client\Servers
    Privilege: Current user access
    """
    
    MINER_NAME = "rdp"
    REQUIRES_ADMIN = False
    
    def __init__(self):
        self.key_path = r"Software\Microsoft\Terminal Server Client\Servers"
    
    def mine(self) -> List[Dict]:
        """
        Extract RDP saved connections
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Mining RDP saved connections...")
        print(f"[*] Location: HKCU\\{self.key_path}")
        
        credentials = []
        
        key = safe_open_key(winreg.HKEY_CURRENT_USER, self.key_path)
        
        if not key:
            print(f"[-] No RDP connections found")
            return credentials
        
        try:
            # Enumerate server names (subkeys)
            server_names = enumerate_subkeys(key)
            
            if not server_names:
                print(f"[-] No saved RDP servers found")
                return credentials
            
            print(f"[+] Found {len(server_names)} saved RDP connection(s)")
            
            for server_name in server_names:
                server_key = safe_open_key(key, server_name)
                
                if not server_key:
                    continue
                
                try:
                    # Extract username hint
                    username_result = safe_query_value(server_key, "UsernameHint")
                    
                    if username_result:
                        username = username_result[0]
                        
                        cred = {
                            'source': 'RDP Saved Connection',
                            'location': f'HKCU\\{self.key_path}\\{server_name}',
                            'server': server_name,
                            'username': username
                        }
                        
                        credentials.append(cred)
                        
                        print(f"[+] Found RDP connection:")
                        print(f"    Server: {server_name}")
                        print(f"    Username: {username}")
                        print(f"    Note: Password stored in Credential Manager")
                
                finally:
                    winreg.CloseKey(server_key)
        
        finally:
            winreg.CloseKey(key)
        
        return credentials
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this miner"""
        return {
            'name': 'rdp',
            'description': 'Extract saved RDP connection information',
            'requires_admin': False,
            'requires_system': False,
            'registry_location': r'HKCU\Software\Microsoft\Terminal Server Client\Servers',
            'credential_types': ['username hints'],
            'notes': [
                'RDP connections store username hints in registry',
                'Actual passwords stored in Windows Credential Manager',
                'Use "cmdkey /list" to view stored credentials',
                'Current user access only'
            ]
        }
