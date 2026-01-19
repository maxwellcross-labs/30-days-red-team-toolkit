#!/usr/bin/env python3
"""
Linux Privilege Escalation Enumerator - CLI
============================================

Command-line interface for the Linux privilege escalation framework.

Part of the 30 Days of Red Team toolkit.

Usage:
    python -m rt_linux_privesc
    python -m rt_linux_privesc --output /tmp/results
    python -m rt_linux_privesc --verbose
    python -m rt_linux_privesc --list
"""

import argparse
import sys
from pathlib import Path

from .core.enumerator import LinuxPrivEscEnumerator
from .core.config import Config


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Linux Privilege Escalation Enumerator - 30 Days of Red Team",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     Run full enumeration
  %(prog)s --output /tmp/scan  Save results to specific directory
  %(prog)s --verbose           Enable verbose output
  %(prog)s --quiet             Minimal output (findings only)
  %(prog)s --list              List available enumerators
  %(prog)s --only suid sudo    Run only specific enumerators

For authorized security testing only.
        """
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='/tmp/privesc_enum',
        help='Output directory for reports (default: /tmp/privesc_enum)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - minimal output'
    )

    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=60,
        help='Command timeout in seconds (default: 60)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available enumerators'
    )

    parser.add_argument(
        '--only',
        nargs='+',
        metavar='ENUM',
        help='Run only specific enumerators'
    )

    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Skip report generation'
    )

    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    # Create configuration
    config = Config(
        output_dir=Path(args.output),
        timeout=args.timeout,
        verbose=args.verbose,
        quiet=args.quiet
    )

    # Initialize enumerator
    enumerator = LinuxPrivEscEnumerator(config=config)

    # List mode
    if args.list:
        enumerator.list_enumerators()
        return 0

    # Run enumeration
    try:
        if args.only:
            enumerator.run_specific(args.only)
        else:
            enumerator.run_all()

        # Generate report
        if not args.no_report:
            enumerator.generate_report()

        # Exit code based on critical findings
        critical_count = len(enumerator.findings.get_critical())

        if critical_count > 0:
            print(f"\n[!] {critical_count} CRITICAL privilege escalation paths found!")
            return 0  # Success - we found something!
        else:
            print(f"\n[*] No critical findings. Check high/medium severity.")
            return 0

    except KeyboardInterrupt:
        print("\n[!] Enumeration interrupted by user")
        return 130
    except Exception as e:
        print(f"\n[-] Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())