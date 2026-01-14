#!/usr/bin/env python3
"""
Example: Mine All Credential Sources
Demonstrates comprehensive credential mining
"""

from rt_registry_miner import RegistryCredentialMiner

def main():
    """Comprehensive mining example"""
    print("[*] Example: Mine All Credential Sources")
    print("="*60)
    
    # Initialize framework
    miner = RegistryCredentialMiner(output_dir="example_output")
    
    # Check privileges
    is_admin, is_system = miner.check_privileges()
    
    if not is_admin:
        print("\n[!] Note: Running without admin privileges")
        print("[!] Some credential sources require administrative access")
        print("[*] Continuing with available miners...")
    
    # Mine all credential sources
    print("\n[*] Mining all credential sources...")
    findings = miner.mine_all()
    
    # Display summary
    print(f"\n" + "="*60)
    print(f"MINING SUMMARY")
    print(f"="*60)
    
    total_found = 0
    
    for source, credentials in findings.items():
        count = len(credentials)
        total_found += count
        
        if count > 0:
            print(f"\n{source.upper()}: {count} credential(s)")
            
            # Show sample of what was found
            for cred in credentials[:2]:  # Show first 2 from each source
                if 'username' in cred:
                    print(f"  • {cred.get('source', 'Unknown')}: {cred['username']}")
                elif 'ssid' in cred:
                    print(f"  • WiFi: {cred['ssid']}")
                elif 'session_name' in cred:
                    print(f"  • Session: {cred['session_name']}")
            
            if count > 2:
                print(f"  ... and {count - 2} more")
    
    print(f"\n[+] Total credentials found: {total_found}")
    
    # Generate report
    miner.generate_report(save_json=True)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
