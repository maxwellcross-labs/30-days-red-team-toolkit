"""
Target Enumeration Framework
Command Line Interface

Discover lateral movement targets across a network.
For authorized penetration testing and red team operations only.

Usage:
    # Full auto enumeration
    python -m target_enum_framework --network 192.168.1.0/24

    # Specific protocols only
    python -m target_enum_framework --network 192.168.1.0/24 --protocols smb winrm

    # Single protocol scan
    python -m target_enum_framework --network 192.168.1.0/24 --protocol smb
"""

import argparse
import sys

from .core import TargetEnumerationFramework, FrameworkConfig
from .scanners import list_protocols


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Lateral Movement Target Enumeration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full enumeration (all protocols)
    %(prog)s --network 192.168.1.0/24

    # Windows-focused (SMB, WinRM, RDP)
    %(prog)s --network 192.168.1.0/24 --protocols smb winrm rdp

    # Linux-focused (SSH only)
    %(prog)s --network 192.168.1.0/24 --protocol ssh

    # Quick SMB scan
    %(prog)s --network 192.168.1.0/24 --protocol smb

Output Files:
    - windows_targets.txt    : Windows hosts
    - linux_targets.txt      : Linux hosts
    - high_value_targets.txt : High-value targets
    - domain_controllers.txt : Domain controllers
    - all_targets.txt        : All discovered hosts
    - targets_report.json    : Full JSON report
        """
    )

    # Network specification
    parser.add_argument(
        '--network', '-n',
        type=str,
        required=True,
        help='Network range (e.g., 192.168.1.0/24)'
    )

    # Protocol selection
    proto_group = parser.add_mutually_exclusive_group()
    proto_group.add_argument(
        '--protocol', '-p',
        type=str,
        choices=list_protocols(),
        help='Single protocol to scan'
    )
    proto_group.add_argument(
        '--protocols',
        type=str,
        nargs='+',
        choices=list_protocols(),
        help='Multiple protocols to scan'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='lm_targets',
        help='Output directory (default: lm_targets)'
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=300,
        help='Scan timeout in seconds (default: 300)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )

    # List available protocols
    parser.add_argument(
        '--list-protocols',
        action='store_true',
        help='List available protocols and exit'
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Handle list protocols
    if args.list_protocols:
        print("Available protocols:")
        for proto in list_protocols():
            print(f"  - {proto}")
        sys.exit(0)

    # Initialize framework
    config = FrameworkConfig(
        output_dir=args.output,
        timeout=args.timeout,
        verbose=not args.quiet
    )

    framework = TargetEnumerationFramework(config)

    # Determine which protocols to scan
    if args.protocol:
        # Single protocol
        framework.scan_protocol(args.network, args.protocol)
        framework.identify_high_value()
        framework.generate_reports()
        framework.report_gen.print_summary(framework.collection)

    elif args.protocols:
        # Multiple specified protocols
        framework.scan_protocols(args.network, args.protocols)
        framework.identify_high_value()
        framework.generate_reports()
        framework.report_gen.print_summary(framework.collection)

    else:
        # Full auto enumeration (all protocols)
        framework.auto_enumerate(args.network)


if __name__ == "__main__":
    main()