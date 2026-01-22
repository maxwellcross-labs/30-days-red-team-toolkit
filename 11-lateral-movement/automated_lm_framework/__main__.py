"""
Automated Lateral Movement Framework
Command Line Interface

Complete lateral movement automation for red team operations.
For authorized penetration testing only.

Usage:
    # Automated campaign
    python -m automated_lm_framework --targets hosts.txt --creds credentials.txt

    # With beacon deployment
    python -m automated_lm_framework --targets hosts.txt --creds credentials.txt --beacon beacon.exe

    # Custom command execution
    python -m automated_lm_framework --targets hosts.txt --creds credentials.txt --command "ipconfig /all"

    # Credential testing only
    python -m automated_lm_framework --targets hosts.txt --creds credentials.txt --test-only
"""

import argparse
import sys
from pathlib import Path

from .core import AutomatedLateralMovement, FrameworkConfig
from .utils.files import validate_file_exists


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Automated Lateral Movement Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full automated campaign
    %(prog)s --targets hosts.txt --creds credentials.txt

    # With beacon deployment
    %(prog)s --targets hosts.txt --creds credentials.txt --beacon beacon.exe

    # Custom command
    %(prog)s --targets hosts.txt --creds credentials.txt --command "net user"

    # Test credentials only (no execution)
    %(prog)s --targets hosts.txt --creds credentials.txt --test-only

Credential File Formats:
    Text format: username:domain:secret (one per line)
        - Hash: 32 hex chars or LM:NT format
        - Password: anything else

    JSON format:
        [{"username": "admin", "domain": "CORP", "password": "Pass123"}]
        [{"username": "admin", "domain": "CORP", "ntlm_hash": "aad3b435..."}]
        """
    )

    # Required inputs
    input_group = parser.add_argument_group('Input Files')
    input_group.add_argument(
        '--targets', '-t',
        type=str,
        required=True,
        help='File with target IPs (one per line)'
    )
    input_group.add_argument(
        '--creds', '-c',
        type=str,
        required=True,
        help='File with credentials'
    )

    # Operation options
    ops_group = parser.add_argument_group('Operations')
    ops_group.add_argument(
        '--beacon', '-b',
        type=str,
        help='Beacon file to deploy to compromised systems'
    )
    ops_group.add_argument(
        '--command', '-x',
        type=str,
        default='whoami',
        help='Command to execute on compromised systems (default: whoami)'
    )
    ops_group.add_argument(
        '--test-only',
        action='store_true',
        help='Only test credentials, do not execute commands'
    )
    ops_group.add_argument(
        '--admin-only',
        action='store_true',
        default=True,
        help='Only execute on systems with admin access (default: True)'
    )

    # Output options
    output_group = parser.add_argument_group('Output')
    output_group.add_argument(
        '--output', '-o',
        type=str,
        default='automated_lm',
        help='Output directory for reports (default: automated_lm)'
    )
    output_group.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Execution timeout in seconds (default: 30)'
    )
    output_group.add_argument(
        '--test-timeout',
        type=int,
        default=10,
        help='Credential test timeout in seconds (default: 10)'
    )
    output_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )

    return parser.parse_args()


def validate_args(args) -> bool:
    """Validate argument combinations"""
    # Check targets file exists
    if not validate_file_exists(args.targets):
        print(f"[-] Error: Targets file not found: {args.targets}")
        return False

    # Check credentials file exists
    if not validate_file_exists(args.creds):
        print(f"[-] Error: Credentials file not found: {args.creds}")
        return False

    # Check beacon file if provided
    if args.beacon and not validate_file_exists(args.beacon):
        print(f"[-] Error: Beacon file not found: {args.beacon}")
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
        test_timeout=args.test_timeout,
        verbose=not args.quiet
    )

    framework = AutomatedLateralMovement(config)

    if args.test_only:
        # Credential testing only
        framework.load_targets(args.targets)
        framework.load_credentials(args.creds)
        framework.test_credentials()

        # Just save access matrix report
        framework.reporter.save_access_matrix()

    else:
        # Full automated campaign
        framework.auto_campaign(
            targets_file=args.targets,
            creds_file=args.creds,
            beacon_path=args.beacon,
            command=args.command
        )


if __name__ == "__main__":
    main()