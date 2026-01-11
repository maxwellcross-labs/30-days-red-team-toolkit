#!/usr/bin/env python3
"""
WiFi Password Miner
Extract saved WiFi passwords using netsh
"""

import subprocess
import re
from typing import List, Dict


class WiFiMiner:
    """
    Extract WiFi passwords from Windows profiles
    
    Method: netsh wlan show profiles
    Privilege: Current user (own profiles) or admin (all profiles)
    """
    
    MINER_NAME = "wifi"
    REQUIRES_ADMIN = False
    
    def mine(self) -> List[Dict]:
        """
        Extract WiFi passwords
        
        Returns:
            List of credential dictionaries
        """
        print(f"\n[*] Mining WiFi passwords...")
        print(f"[*] Method: netsh wlan")
        
        credentials = []
        
        # Get WiFi profiles
        try:
            result = subprocess.run(
                "netsh wlan show profiles",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"[-] Failed to retrieve WiFi profiles")
                return credentials
            
            # Parse profile names
            profiles = []
            for line in result.stdout.split('\n'):
                if 'All User Profile' in line or 'User Profile' in line:
                    # Extract profile name after ':'
                    match = re.search(r':\s*(.+)$', line)
                    if match:
                        profile_name = match.group(1).strip()
                        profiles.append(profile_name)
            
            if not profiles:
                print(f"[-] No WiFi profiles found")
                return credentials
            
            print(f"[+] Found {len(profiles)} WiFi profile(s)")
            
            # Extract password for each profile
            for profile in profiles:
                try:
                    result_pass = subprocess.run(
                        f'netsh wlan show profile name="{profile}" key=clear',
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result_pass.returncode == 0:
                        # Look for key content line
                        for line in result_pass.stdout.split('\n'):
                            if 'Key Content' in line:
                                match = re.search(r':\s*(.+)$', line)
                                if match:
                                    password = match.group(1).strip()
                                    
                                    cred = {
                                        'source': 'WiFi',
                                        'ssid': profile,
                                        'password': password
                                    }
                                    
                                    credentials.append(cred)
                                    
                                    print(f"[+] Found WiFi password:")
                                    print(f"    SSID: {profile}")
                                    print(f"    Password: {password}")
                                    
                                    break
                
                except subprocess.TimeoutExpired:
                    print(f"[-] Timeout retrieving password for: {profile}")
                except Exception as e:
                    print(f"[-] Error retrieving password for {profile}: {e}")
        
        except subprocess.TimeoutExpired:
            print(f"[-] Timeout retrieving WiFi profiles")
        except Exception as e:
            print(f"[-] WiFi password extraction failed: {e}")
        
        return credentials
    
    @staticmethod
    def get_info() -> Dict:
        """Get information about this miner"""
        return {
            'name': 'wifi',
            'description': 'Extract saved WiFi passwords',
            'requires_admin': False,
            'requires_system': False,
            'method': 'netsh wlan show profiles',
            'credential_types': ['plaintext password'],
            'notes': [
                'Extracts WiFi passwords from saved profiles',
                'Current user profiles accessible without admin',
                'All user profiles require administrator privileges',
                'Passwords retrieved in plaintext'
            ]
        }
