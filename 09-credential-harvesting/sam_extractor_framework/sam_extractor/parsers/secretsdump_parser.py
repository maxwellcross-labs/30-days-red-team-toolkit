#!/usr/bin/env python3
"""
Parse SAM/SYSTEM hives using Impacket secretsdump
Extract local account password hashes
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional


class SecretsdumpParser:
    """
    Parse SAM and SYSTEM hives using Impacket's secretsdump
    Extracts local account password hashes
    """
    
    def __init__(self):
        """Initialize parser"""
        self.secretsdump_available = self._check_secretsdump()
    
    def _check_secretsdump(self) -> bool:
        """Check if secretsdump is available"""
        try:
            result = subprocess.run(
                'secretsdump.py -h',
                shell=True,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def is_available(self) -> bool:
        """Check if parser is available"""
        return self.secretsdump_available
    
    def parse_hives(self, sam_file: str, system_file: str, security_file: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Parse SAM/SYSTEM hives and extract hashes
        
        Args:
            sam_file: Path to SAM hive file
            system_file: Path to SYSTEM hive file
            security_file: Optional path to SECURITY hive file
            
        Returns:
            List of credential dictionaries or None on failure
        """
        if not self.is_available():
            print(f"[-] secretsdump not available")
            print(f"[!] Install: pip install impacket")
            return None
        
        print(f"\n[*] Parsing SAM hashes with secretsdump...")
        print(f"[*] SAM: {sam_file}")
        print(f"[*] SYSTEM: {system_file}")
        
        if security_file:
            print(f"[*] SECURITY: {security_file}")
        
        try:
            # Build secretsdump command
            cmd = f'secretsdump.py -sam "{sam_file}" -system "{system_file}"'
            
            if security_file:
                cmd += f' -security "{security_file}"'
            
            cmd += ' LOCAL'
            
            # Execute secretsdump
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"[-] secretsdump failed")
                
                if result.stderr:
                    print(f"    Error: {result.stderr}")
                
                return None
            
            # Parse output
            output = result.stdout
            
            print(f"\n[+] secretsdump completed")
            
            # Extract credentials
            credentials = self._parse_secretsdump_output(output)
            
            if credentials:
                print(f"[+] Extracted {len(credentials)} account hashes")
            else:
                print(f"[-] No hashes extracted")
            
            return credentials
        
        except subprocess.TimeoutExpired:
            print(f"[-] secretsdump timed out")
            return None
        
        except Exception as e:
            print(f"[-] Parse failed: {e}")
            return None
    
    def _parse_secretsdump_output(self, output: str) -> List[Dict]:
        """
        Parse secretsdump output and extract credentials
        
        Args:
            output: secretsdump stdout
            
        Returns:
            List of credential dictionaries
        """
        credentials = []
        
        # Split output into lines
        lines = output.split('\n')
        
        for line in lines:
            # Look for hash lines
            # Format: Username:RID:LMHash:NTHash:::
            if ':' in line and ':::' in line:
                # Skip headers and informational lines
                if any(x in line.lower() for x in ['impacket', 'target', 'retrieving', '[*]']):
                    continue
                
                # Parse hash line
                parts = line.split(':')
                
                if len(parts) >= 4:
                    username = parts[0].strip()
                    rid = parts[1].strip()
                    lm_hash = parts[2].strip()
                    nt_hash = parts[3].strip()
                    
                    # Skip empty or invalid entries
                    if not username or username == '':
                        continue
                    
                    # Create credential entry
                    cred = {
                        'username': username,
                        'rid': rid,
                        'lm_hash': lm_hash if lm_hash else 'aad3b435b51404eeaad3b435b51404ee',
                        'nt_hash': nt_hash if nt_hash else '31d6cfe0d16ae931b73c59d7e0c089c0',
                        'full_hash': f"{username}:{rid}:{lm_hash}:{nt_hash}:::"
                    }
                    
                    credentials.append(cred)
        
        return credentials
    
    def display_credentials(self, credentials: List[Dict]):
        """
        Display extracted credentials in readable format
        
        Args:
            credentials: List of credential dictionaries
        """
        if not credentials:
            print(f"\n[-] No credentials to display")
            return
        
        print(f"\n" + "="*70)
        print(f"EXTRACTED SAM HASHES")
        print(f"="*70)
        
        for i, cred in enumerate(credentials, 1):
            username = cred.get('username', 'Unknown')
            rid = cred.get('rid', '?')
            lm = cred.get('lm_hash', '')
            nt = cred.get('nt_hash', '')
            
            print(f"\n[{i}] {username} (RID: {rid})")
            print(f"    LM Hash: {lm}")
            print(f"    NT Hash: {nt}")
            
            # Check for empty/default hashes
            if nt == '31d6cfe0d16ae931b73c59d7e0c089c0':
                print(f"    Status: Empty password")
            elif lm == 'aad3b435b51404eeaad3b435b51404ee':
                print(f"    Status: LM hash disabled")
    
    def save_credentials(self, credentials: List[Dict], output_file: str, format: str = 'text'):
        """
        Save credentials to file
        
        Args:
            credentials: List of credential dictionaries
            output_file: Output file path
            format: Output format ('text', 'hashcat', 'john')
        """
        output_path = Path(output_file)
        
        if format == 'hashcat':
            # Hashcat format: username:hash
            with open(output_path, 'w') as f:
                for cred in credentials:
                    username = cred.get('username', '')
                    nt_hash = cred.get('nt_hash', '')
                    
                    if username and nt_hash:
                        f.write(f"{username}:{nt_hash}\n")
            
            print(f"[+] Hashes saved: {output_path} (Hashcat format)")
        
        elif format == 'john':
            # John the Ripper format: username:rid:lm:nt:::
            with open(output_path, 'w') as f:
                for cred in credentials:
                    f.write(f"{cred.get('full_hash', '')}\n")
            
            print(f"[+] Hashes saved: {output_path} (John format)")
        
        else:
            # Text format
            with open(output_path, 'w') as f:
                f.write("SAM Hash Dump\n")
                f.write("=" * 70 + "\n\n")
                
                for cred in credentials:
                    f.write(f"Username: {cred.get('username', '')}\n")
                    f.write(f"RID: {cred.get('rid', '')}\n")
                    f.write(f"LM Hash: {cred.get('lm_hash', '')}\n")
                    f.write(f"NT Hash: {cred.get('nt_hash', '')}\n")
                    f.write(f"Full: {cred.get('full_hash', '')}\n")
                    f.write("\n")
            
            print(f"[+] Hashes saved: {output_path} (Text format)")
    
    def parse_and_display(self, sam_file: str, system_file: str, 
                         security_file: Optional[str] = None,
                         save_to: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Parse hives and display/save credentials
        
        Args:
            sam_file: Path to SAM file
            system_file: Path to SYSTEM file
            security_file: Optional SECURITY file
            save_to: Optional output file base name
            
        Returns:
            List of credentials or None
        """
        # Parse hives
        credentials = self.parse_hives(sam_file, system_file, security_file)
        
        if not credentials:
            return None
        
        # Display credentials
        self.display_credentials(credentials)
        
        # Save if requested
        if save_to:
            sam_path = Path(sam_file)
            output_dir = sam_path.parent
            
            base_name = Path(save_to).stem
            
            # Save in multiple formats
            self.save_credentials(
                credentials,
                output_dir / f"{base_name}.txt",
                format='text'
            )
            
            self.save_credentials(
                credentials,
                output_dir / f"{base_name}_hashcat.txt",
                format='hashcat'
            )
            
            self.save_credentials(
                credentials,
                output_dir / f"{base_name}_john.txt",
                format='john'
            )
        
        return credentials
