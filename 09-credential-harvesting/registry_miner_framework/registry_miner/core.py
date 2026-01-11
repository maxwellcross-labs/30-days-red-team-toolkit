#!/usr/bin/env python3
"""
Core Registry Credential Mining Framework
Orchestrates multiple credential mining operations
"""

from pathlib import Path
from typing import List, Dict, Optional
import json

from .miners import (
    AutoLogonMiner,
    RDPMiner,
    WiFiMiner,
    PuTTYMiner,
    VNCMiner,
    WinSCPMiner,
    LSASecretsMiner,
    MINER_REGISTRY,
    list_miners,
    get_miner_info
)
from .utils import check_admin_privileges, check_system_privileges, print_privilege_status


class RegistryCredentialMiner:
    """
    Main registry credential mining framework
    Coordinates multiple credential miners
    """
    
    def __init__(self, output_dir: str = "registry_creds"):
        """
        Initialize registry credential miner
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize findings storage
        self.findings = {
            'autologon': [],
            'rdp': [],
            'wifi': [],
            'putty': [],
            'vnc': [],
            'winscp': [],
            'lsa_secrets': []
        }
        
        # Initialize standard miners (no special parameters)
        self.miners = {
            'autologon': AutoLogonMiner(),
            'rdp': RDPMiner(),
            'wifi': WiFiMiner(),
            'putty': PuTTYMiner(),
            'vnc': VNCMiner(),
            'winscp': WinSCPMiner()
        }
        
        # LSA secrets miner needs output_dir
        self.lsa_miner = LSASecretsMiner(self.output_dir)
        
        print(f"[+] Registry Credential Miner initialized")
        print(f"[+] Output directory: {self.output_dir}")
        print(f"[+] Available miners: {', '.join(self.miners.keys())}, lsa_secrets")
    
    def check_privileges(self) -> Tuple[bool, bool]:
        """
        Check current privilege level
        
        Returns:
            Tuple of (is_admin: bool, is_system: bool)
        """
        is_admin, msg = check_admin_privileges()
        is_system = check_system_privileges()
        
        if is_admin:
            print(f"[+] {msg}")
        else:
            print(f"[!] {msg}")
            print(f"[*] Some miners require administrative privileges")
        
        return is_admin, is_system
    
    def mine_target(self, target: str) -> List[Dict]:
        """
        Execute specific miner
        
        Args:
            target: Miner name
            
        Returns:
            List of credentials found
        """
        if target == 'lsa_secrets':
            return self.lsa_miner.mine()
        elif target in self.miners:
            return self.miners[target].mine()
        else:
            print(f"[-] Unknown target: {target}")
            print(f"[!] Available targets: {', '.join(list(self.miners.keys()) + ['lsa_secrets'])}")
            return []
    
    def mine_all(self) -> Dict[str, List[Dict]]:
        """
        Execute all miners
        
        Returns:
            Dict of miner names to credential lists
        """
        print(f"\n" + "="*70)
        print(f"REGISTRY CREDENTIAL MINING")
        print(f"="*70)
        
        # Check privileges
        is_admin, is_system = self.check_privileges()
        
        # Mine with standard miners
        for miner_name, miner in self.miners.items():
            try:
                credentials = miner.mine()
                self.findings[miner_name] = credentials
            except Exception as e:
                print(f"[-] Error in {miner_name} miner: {e}")
        
        # Mine LSA secrets
        try:
            credentials = self.lsa_miner.mine()
            self.findings['lsa_secrets'] = credentials
        except Exception as e:
            print(f"[-] Error in lsa_secrets miner: {e}")
        
        return self.findings
    
    def generate_report(self, save_json: bool = True):
        """
        Generate comprehensive credential report
        
        Args:
            save_json: Whether to save JSON format
        """
        print(f"\n" + "="*70)
        print(f"REGISTRY CREDENTIAL MINING REPORT")
        print(f"="*70)
        
        # Calculate totals
        total_creds = sum(len(v) for v in self.findings.values())
        
        print(f"\n[+] Total credentials found: {total_creds}")
        
        if total_creds == 0:
            print(f"[-] No credentials found")
            return
        
        print(f"\nBreakdown by source:")
        
        for category, items in self.findings.items():
            if items:
                print(f"  {category}: {len(items)}")
        
        # Save text report
        report_file = self.output_dir / "credential_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("REGISTRY CREDENTIAL MINING REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total credentials found: {total_creds}\n\n")
            
            for category, items in self.findings.items():
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
            json_file = self.output_dir / "credential_report.json"
            
            with open(json_file, 'w') as f:
                json.dump(self.findings, f, indent=2)
            
            print(f"[+] JSON report saved to: {json_file}")
    
    def show_miner_info(self, miner_name: str):
        """
        Display detailed information about a miner
        
        Args:
            miner_name: Miner name
        """
        info = get_miner_info(miner_name)
        
        if not info:
            print(f"[-] Unknown miner: {miner_name}")
            return
        
        print(f"\n" + "="*70)
        print(f"MINER: {info['name'].upper()}")
        print(f"="*70)
        
        print(f"\nDescription: {info['description']}")
        print(f"Requires Admin: {'Yes' if info['requires_admin'] else 'No'}")
        print(f"Requires SYSTEM: {'Yes' if info.get('requires_system', False) else 'No'}")
        
        if 'registry_location' in info:
            print(f"\nRegistry Location: {info['registry_location']}")
        elif 'registry_locations' in info:
            print(f"\nRegistry Locations:")
            for loc in info['registry_locations']:
                print(f"  • {loc}")
        
        if 'method' in info:
            print(f"Method: {info['method']}")
        
        if 'tool_required' in info:
            print(f"Tool Required: {info['tool_required']}")
        
        print(f"\nCredential Types:")
        for cred_type in info['credential_types']:
            print(f"  • {cred_type}")
        
        if 'notes' in info:
            print(f"\nNotes:")
            for note in info['notes']:
                print(f"  • {note}")
        
        if 'decryption_tools' in info:
            print(f"\nDecryption Tools:")
            for tool in info['decryption_tools']:
                print(f"  • {tool}")
    
    def show_all_miners(self):
        """Display information about all available miners"""
        miners = list_miners()
        
        print(f"\n" + "="*70)
        print(f"AVAILABLE CREDENTIAL MINERS")
        print(f"="*70)
        
        for miner_name in miners:
            info = get_miner_info(miner_name)
            if info:
                admin_req = "✓ Admin" if info['requires_admin'] else "○ User"
                system_req = " + SYSTEM" if info.get('requires_system', False) else ""
                
                print(f"\n{miner_name.upper()} ({admin_req}{system_req})")
                print(f"  {info['description']}")


from typing import Tuple
