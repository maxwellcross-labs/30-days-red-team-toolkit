#!/usr/bin/env python3
"""
Command-line interface for SAM Extractor Framework
"""

import argparse
import sys
from pathlib import Path

from .core import SAMExtractor
from .utils import print_privilege_status


def print_banner():
    """Print framework banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                 SAM EXTRACTOR FRAMEWORK v1.0                      ║
║           Local Account Hash Harvesting Toolkit                   ║
║                                                                   ║
║  WARNING: For authorized security testing only                   ║
║  Unauthorized access to computer systems is illegal              ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_extract(args):
    """Execute extract command"""
    extractor = SAMExtractor(output_dir=args.output)
    
    if args.method == 'auto':
        result = extractor.auto_extract(preferred_method=args.prefer)
    else:
        result = extractor.extract(args.method)
    
    if result:
        if args.parse:
            print(f"\n[*] Parsing extracted hives...")
            
            sam_file = result.get('sam')
            system_file = result.get('system')
            security_file = result.get('security')
            
            if sam_file and system_file:
                extractor.parse_hives(sam_file, system_file, security_file, save_hashes=True)
        
        return 0
    else:
        return 1


def cmd_parse(args):
    """Execute parse command"""
    extractor = SAMExtractor(output_dir=args.output)
    
    if not args.sam or not args.system:
        print(f"[-] Parse requires both --sam and --system files")
        return 1
    
    credentials = extractor.parse_hives(
        args.sam,
        args.system,
        args.security,
        save_hashes=not args.no_save
    )
    
    return 0 if credentials else 1


def cmd_list(args):
    """List available methods"""
    extractor = SAMExtractor()
    
    if args.available:
        available = extractor.list_available_methods()
        print(f"\n[*] {len(available)} methods ready to use")
    else:
        extractor.show_all_methods()
    
    return 0


def cmd_info(args):
    """Show method information"""
    extractor = SAMExtractor()
    extractor.show_method_info(args.method)
    return 0


def cmd_check(args):
    """Check privileges and environment"""
    print_banner()
    
    print(f"\n[*] Environment Check")
    print(f"="*70)
    
    # Check privileges
    print_privilege_status()
    
    # Check available methods
    print(f"\n[*] Method Availability:")
    extractor = SAMExtractor()
    available = extractor.list_available_methods()
    
    print(f"\n[+] {len(available)}/{len(extractor.extractors)} methods available")
    
    # Check parser
    print(f"\n[*] Parser Status:")
    if extractor.parser.is_available():
        print(f"    ✓ Impacket secretsdump available")
    else:
        print(f"    ✗ Impacket not installed")
        print(f"    Install: pip install impacket")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='SAM/SYSTEM Extractor Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto extract with default method
  sam_extract.py extract --auto
  
  # Extract with specific method
  sam_extract.py extract --method reg_save
  
  # Extract and parse
  sam_extract.py extract --auto --parse
  
  # Parse existing hives
  sam_extract.py parse --sam sam.save --system system.save
  
  # List available methods
  sam_extract.py list
  
  # Show method details
  sam_extract.py info --method vss
  
  # Check privileges and availability
  sam_extract.py check
"""
    )
    
    parser.add_argument('--version', action='version', version='SAM Extractor v1.0')
    parser.add_argument('--output', '-o', default='sam_dumps',
                       help='Output directory (default: sam_dumps)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract SAM/SYSTEM hives')
    extract_parser.add_argument('--method', '-m',
                               choices=['auto', 'reg_save', 'vss'],
                               default='auto',
                               help='Extraction method (default: auto)')
    extract_parser.add_argument('--prefer', '-p', default='reg_save',
                               help='Preferred method for auto mode (default: reg_save)')
    extract_parser.add_argument('--parse', action='store_true',
                               help='Automatically parse hives after extraction')
    extract_parser.set_defaults(func=cmd_extract)
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse existing hive files')
    parse_parser.add_argument('--sam', required=True,
                             help='SAM hive file')
    parse_parser.add_argument('--system', required=True,
                             help='SYSTEM hive file')
    parse_parser.add_argument('--security',
                             help='SECURITY hive file (optional)')
    parse_parser.add_argument('--no-save', action='store_true',
                             help='Do not save hashes to files')
    parse_parser.set_defaults(func=cmd_parse)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List extraction methods')
    list_parser.add_argument('--available', '-a', action='store_true',
                            help='Only show currently available methods')
    list_parser.set_defaults(func=cmd_list)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show method information')
    info_parser.add_argument('--method', '-m', required=True,
                            help='Method name')
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
