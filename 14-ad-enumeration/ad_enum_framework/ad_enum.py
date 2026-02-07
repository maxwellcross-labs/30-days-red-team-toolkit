"""
AD Enumeration Framework
Main entry point for Active Directory enumeration
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .core.enumerator import ADEnumerator


def print_banner():
    """Print tool banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║   Active Directory Enumeration Framework                 ║
║   Red Team Domain Reconnaissance                         ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main execution function"""
    print_banner()

    parser = argparse.ArgumentParser(
        description="Active Directory Enumeration Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -d contoso.com -u jdoe -p Password123
  %(prog)s -d corp.local -u administrator -p Pass@123 --dc 10.0.0.10
  %(prog)s -d lab.local -u admin -p P@ssw0rd -o ./recon_output
        """
    )

    parser.add_argument('--domain', '-d', required=True,
                        help='Target domain (e.g., contoso.com)')
    parser.add_argument('--username', '-u', required=True,
                        help='Domain username')
    parser.add_argument('--password', '-p', required=True,
                        help='Domain password')
    parser.add_argument('--dc',
                        help='Domain controller IP address (optional)')
    parser.add_argument('--output', '-o', default='ad_enum',
                        help='Output directory (default: ad_enum)')

    args = parser.parse_args()

    # Initialize enumerator
    enumerator = ADEnumerator(
        domain=args.domain,
        username=args.username,
        password=args.password,
        dc_ip=args.dc,
        output_dir=args.output
    )

    # Run enumeration
    try:
        success = enumerator.run_full_enumeration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[!] Enumeration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()