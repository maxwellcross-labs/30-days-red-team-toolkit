import argparse
import sys
from core.enumerator import PrivEscEnumerator


def main():
    parser = argparse.ArgumentParser(description="Windows Privilege Escalation Enumerator")
    parser.add_argument('--output', type=str, default='privesc_enum',
                        help='Output directory')

    args = parser.parse_args()

    try:
        enumerator = PrivEscEnumerator(output_dir=args.output)
        enumerator.run()
    except KeyboardInterrupt:
        print("\n[!] Enumeration interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()