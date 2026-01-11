#!/usr/bin/env python3
"""
Command-line interface for DPAPI Decryptor Framework
"""

import argparse
import sys
from pathlib import Path

from .core import DPAPIDecryptor
from .utils import print_privilege_status, is_dpapi_available


def print_banner():
    """Print framework banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║              DPAPI DECRYPTOR FRAMEWORK v1.0                       ║
║        Browser Password & Credential Decryption                   ║
║                                                                   ║
║  WARNING: For authorized security testing only                    ║
║  Unauthorized access to computer systems is illegal               ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_decrypt(args):
    """Execute decrypt command"""
    decryptor = DPAPIDecryptor(output_dir=args.output)
    
    if args.target == 'all':
        decryptor.decrypt_all()
    else:
        result = decryptor.decrypt_target(args.target)
        decryptor.credentials[args.target] = result
    
    # Generate report
    decryptor.generate_report(save_json=not args.no_json)
    
    return 0


def cmd_list(args):
    """List available decryptors"""
    decryptor = DPAPIDecryptor()
    
    if args.available:
        available = decryptor.list_available_decryptors()
        print(f"\n[*] {len(available)} decryptor(s) ready to use")
    else:
        decryptor.show_all_decryptors()
    
    return 0


def cmd_info(args):
    """Show decryptor information"""
    decryptor = DPAPIDecryptor()
    decryptor.show_decryptor_info(args.decryptor)
    return 0


def cmd_check(args):
    """Check environment and dependencies"""
    print_banner()
    
    print(f"\n[*] Environment Check")
    print(f"="*70)
    
    # Check privileges and user context
    print_privilege_status()
    
    # Check DPAPI availability
    print(f"\n[*] Dependencies:")
    if is_dpapi_available():
        print(f"    ✓ pywin32 installed (DPAPI available)")
    else:
        print(f"    ✗ pywin32 not installed")
        print(f"    Install: pip install pywin32")
    
    # Check decryptor availability
    print(f"\n[*] Decryptor Availability:")
    decryptor = DPAPIDecryptor()
    available = decryptor.list_available_decryptors()
    
    print(f"\n[+] {len(available)}/{len(decryptor.decryptors)} decryptors available")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='DPAPI Credential Decryptor Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Decrypt all credentials
  dpapi_decrypt.py decrypt --all
  
  # Decrypt specific target
  dpapi_decrypt.py decrypt --target chrome
  dpapi_decrypt.py decrypt --target edge
  
  # List available decryptors
  dpapi_decrypt.py list
  
  # Show decryptor details
  dpapi_decrypt.py info --decryptor chrome
  
  # Check environment and availability
  dpapi_decrypt.py check
"""
    )
    
    parser.add_argument('--version', action='version', version='DPAPI Decryptor v1.0')
    parser.add_argument('--output', '-o', default='dpapi_creds',
                       help='Output directory (default: dpapi_creds)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt credentials')
    decrypt_parser.add_argument('--target', '-t',
                               choices=['all', 'chrome', 'edge', 'firefox',
                                      'windows_vault', 'rdp'],
                               default='all',
                               help='Target application (default: all)')
    decrypt_parser.add_argument('--no-json', action='store_true',
                               help='Do not save JSON report')
    decrypt_parser.set_defaults(func=cmd_decrypt)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available decryptors')
    list_parser.add_argument('--available', '-a', action='store_true',
                            help='Only show currently available decryptors')
    list_parser.set_defaults(func=cmd_list)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show decryptor information')
    info_parser.add_argument('--decryptor', '-d', required=True,
                            help='Decryptor name')
    info_parser.set_defaults(func=cmd_info)
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check environment and dependencies')
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
