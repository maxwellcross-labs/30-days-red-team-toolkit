"""
Command Line Interface
======================

CLI for the Week 3 Attack Orchestrator.
"""

import argparse
import sys
from typing import List, Optional

from .models import Platform
from .core import Week3Orchestrator


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Arguments to parse (defaults to sys.argv)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="week3_orchestrator",
        description="Week 3 Integrated Attack Orchestrator - Chain red team techniques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full attack chain on Windows target
  python -m week3_orchestrator --platform windows

  # Run specific phase only
  python -m week3_orchestrator --phase 2 --platform windows

  # Run with custom targets
  python -m week3_orchestrator --targets 192.168.1.0/24 10.0.0.0/24

  # Specify output directory
  python -m week3_orchestrator --output my_operation
        """
    )

    parser.add_argument(
        "--platform", "-p",
        choices=["windows", "linux"],
        default="windows",
        help="Initial target platform (default: windows)"
    )

    parser.add_argument(
        "--targets", "-t",
        nargs="+",
        default=["192.168.1.0/24"],
        help="Target networks/hosts for lateral movement"
    )

    parser.add_argument(
        "--output", "-o",
        default="week3_operation",
        help="Output directory for logs and reports (default: week3_operation)"
    )

    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific phase only (1-5)"
    )

    parser.add_argument(
        "--domain",
        default="CORP.LOCAL",
        help="Target domain for trust exploitation (default: CORP.LOCAL)"
    )

    parser.add_argument(
        "--pivot-network",
        default="10.0.0.0/24",
        help="Target network for pivoting (default: 10.0.0.0/24)"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 1.0.0"
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for CLI.

    Args:
        args: Command line arguments

    Returns:
        Exit code (0 for success)
    """
    parsed = parse_args(args)

    # Initialize orchestrator
    orchestrator = Week3Orchestrator(output_dir=parsed.output)

    # Set verbosity
    if parsed.quiet:
        orchestrator.logger.console_enabled = False

    # Determine platform
    platform = Platform.WINDOWS if parsed.platform == "windows" else Platform.LINUX

    try:
        if parsed.phase:
            # Run specific phase
            phase_args = {
                "platform": platform,
                "targets": parsed.targets,
                "target_network": parsed.pivot_network,
                "domain": parsed.domain,
            }
            orchestrator.execute_phase(parsed.phase, **phase_args)
        else:
            # Run full chain
            orchestrator.execute_full_chain(platform, parsed.targets)

        return 0

    except KeyboardInterrupt:
        print("\n[!] Operation interrupted by user")
        orchestrator.generate_reports()
        return 1

    except Exception as e:
        orchestrator.logger.error(f"Operation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())