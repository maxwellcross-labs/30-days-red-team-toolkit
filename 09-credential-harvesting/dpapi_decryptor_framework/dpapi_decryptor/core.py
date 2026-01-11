#!/usr/bin/env python3
"""
Core DPAPI Credential Decryption Framework
Orchestrates browser password and credential decryption
"""

from pathlib import Path
from typing import List, Dict, Optional
import json

from .decryptors import (
    ChromeDecryptor,
    EdgeDecryptor,
    FirefoxDecryptor,
    WindowsVaultDecryptor,
    RDPDecryptor,
    DECRYPTOR_REGISTRY,
    list_decryptors,
    get_decryptor_info
)
from .utils import (
    check_admin_privileges,
    check_current_user_context,
    print_privilege_status,
    is_dpapi_available
)


class DPAPIDecryptor:
    """
    Main DPAPI credential decryption framework
    Coordinates multiple credential decryptors
    """
    
    def __init__(self, output_dir: str = "dpapi_creds"):
        """
        Initialize DPAPI decryptor framework
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize findings storage
        self.credentials = {
            'chrome': [],
            'edge': [],
            'firefox': [],
            'windows_vault': [],
            'rdp': []
        }
        
        # Initialize decryptors (all need output_dir)
        self.decryptors = {
            'chrome': ChromeDecryptor(self.output_dir),
            'edge': EdgeDecryptor(self.output_dir),
            'firefox': FirefoxDecryptor(self.output_dir),
            'windows_vault': WindowsVaultDecryptor(self.output_dir),
            'rdp': RDPDecryptor(self.output_dir)
        }
        
        print(f"[+] DPAPI Decryptor Framework initialized")
        print(f"[+] Output directory: {self.output_dir}")
        print(f"[+] Available decryptors: {', '.join(self.decryptors.keys())}")
    
    def check_environment(self):
        """
        Check environment and dependencies
        
        Returns:
            Dict with environment status
        """
        username = check_current_user_context()
        is_admin, msg = check_admin_privileges()
        dpapi_available = is_dpapi_available()
        
        status = {
            'username': username,
            'is_admin': is_admin,
            'dpapi_available': dpapi_available
        }
        
        print(f"[*] Environment Status:")
        print(f"    User: {username}")
        print(f"    Admin: {'✓' if is_admin else '✗'}")
        print(f"    DPAPI Available: {'✓' if dpapi_available else '✗'}")
        
        if not dpapi_available:
            print(f"\n[!] pywin32 not installed - some decryptors will fail")
            print(f"[!] Install: pip install pywin32")
        
        print(f"\n[!] Important: Can only decrypt data encrypted by {username}")
        
        return status
    
    def list_available_decryptors(self) -> List[str]:
        """
        List decryptors that are actually available
        
        Returns:
            List of available decryptor names
        """
        available = []
        
        print(f"\n[*] Checking decryptor availability...")
        
        for name, decryptor in self.decryptors.items():
            is_avail = decryptor.is_available()
            status = "✓" if is_avail else "✗"
            
            print(f"    {status} {name}: {'Available' if is_avail else 'Not available'}")
            
            if is_avail:
                available.append(name)
        
        return available
    
    def decrypt_target(self, target: str) -> List[Dict]:
        """
        Execute specific decryptor
        
        Args:
            target: Decryptor name
            
        Returns:
            List of credentials found
        """
        if target not in self.decryptors:
            print(f"[-] Unknown target: {target}")
            print(f"[!] Available targets: {', '.join(self.decryptors.keys())}")
            return []
        
        decryptor = self.decryptors[target]
        
        if not decryptor.is_available():
            print(f"[-] Decryptor '{target}' is not available")
            return []
        
        return decryptor.decrypt()
    
    def decrypt_all(self) -> Dict[str, List[Dict]]:
        """
        Execute all available decryptors
        
        Returns:
            Dict of decryptor names to credential lists
        """
        print(f"\n" + "="*70)
        print(f"DPAPI CREDENTIAL DECRYPTION")
        print(f"="*70)
        
        # Check environment
        self.check_environment()
        
        # Decrypt with all decryptors
        for decryptor_name, decryptor in self.decryptors.items():
            try:
                credentials = decryptor.decrypt()
                self.credentials[decryptor_name] = credentials
            except Exception as e:
                print(f"[-] Error in {decryptor_name} decryptor: {e}")
        
        return self.credentials
    
    def generate_report(self, save_json: bool = True):
        """
        Generate comprehensive credential report
        
        Args:
            save_json: Whether to save JSON format
        """
        print(f"\n" + "="*70)
        print(f"DPAPI CREDENTIAL DECRYPTION REPORT")
        print(f"="*70)
        
        # Calculate totals
        total_creds = sum(len(v) for v in self.credentials.values())
        
        print(f"\n[+] Total credentials found: {total_creds}")
        
        if total_creds == 0:
            print(f"[-] No credentials decrypted")
            return
        
        print(f"\nBreakdown by source:")
        
        for category, items in self.credentials.items():
            if items:
                print(f"  {category}: {len(items)}")
        
        # Save text report
        report_file = self.output_dir / "dpapi_credentials.txt"
        
        with open(report_file, 'w') as f:
            f.write("DPAPI CREDENTIAL DECRYPTION REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total credentials found: {total_creds}\n\n")
            
            for category, items in self.credentials.items():
                if items:
                    f.write(f"\n{category.upper()}\n")
                    f.write("-"*70 + "\n")
                    
                    for item in items:
                        for key, value in item.items():
                            f.write(f"{key}: {value}\n")
                        f.write("\n")
        
        print(f"\n[+] Text report saved to: {report_file}")
        
        # Save JSON report
        if save_json:
            json_file = self.output_dir / "dpapi_credentials.json"
            
            with open(json_file, 'w') as f:
                json.dump(self.credentials, f, indent=2)
            
            print(f"[+] JSON report saved to: {json_file}")
    
    def show_decryptor_info(self, decryptor_name: str):
        """
        Display detailed information about a decryptor
        
        Args:
            decryptor_name: Decryptor name
        """
        info = get_decryptor_info(decryptor_name)
        
        if not info:
            print(f"[-] Unknown decryptor: {decryptor_name}")
            return
        
        print(f"\n" + "="*70)
        print(f"DECRYPTOR: {info['name'].upper()}")
        print(f"="*70)
        
        print(f"\nDescription: {info['description']}")
        print(f"Requires Admin: {'Yes' if info['requires_admin'] else 'No'}")
        
        if 'location' in info:
            print(f"\nLocation: {info['location']}")
        
        if 'method' in info:
            print(f"Method: {info['method']}")
        
        print(f"Encryption: {info['encryption']}")
        
        print(f"\nCredential Types:")
        for cred_type in info['credential_types']:
            print(f"  • {cred_type}")
        
        if 'requirements' in info:
            print(f"\nRequirements:")
            for req in info['requirements']:
                print(f"  • {req}")
        
        if 'notes' in info:
            print(f"\nNotes:")
            for note in info['notes']:
                print(f"  • {note}")
        
        if 'decryption_tools' in info:
            print(f"\nAdditional Decryption Tools:")
            for tool in info['decryption_tools']:
                print(f"  • {tool}")
    
    def show_all_decryptors(self):
        """Display information about all available decryptors"""
        decryptors = list(self.decryptors.keys())
        
        print(f"\n" + "="*70)
        print(f"AVAILABLE CREDENTIAL DECRYPTORS")
        print(f"="*70)
        
        for decryptor_name in decryptors:
            info = get_decryptor_info(decryptor_name)
            if info:
                avail = "✓" if self.decryptors[decryptor_name].is_available() else "✗"
                admin_req = " (Admin)" if info['requires_admin'] else ""
                
                print(f"\n{avail} {decryptor_name.upper()}{admin_req}")
                print(f"  {info['description']}")
                print(f"  Encryption: {info['encryption']}")
