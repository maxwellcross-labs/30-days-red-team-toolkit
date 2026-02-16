"""
Silver Ticket Service Reference — Common SPNs and what access they grant.

Used as a quick-lookup when choosing which service to forge a Silver Ticket for.
"""


def print_silver_ticket_services():
    """Print the common Silver Ticket SPN → access mapping table."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                   COMMON SILVER TICKET SERVICES                     ║
╠══════════════════════════════════════════════════════════════════════╣
║  CIFS/host.domain      → SMB file share access                      ║
║  HOST/host.domain      → WMI, scheduled tasks, PSRemoting          ║
║  MSSQLSvc/host:1433    → SQL Server database access                 ║
║  HTTP/host.domain      → Web application / IIS access               ║
║  LDAP/dc.domain        → LDAP operations (DCSync!)                  ║
║  RPCSS/host.domain     → WMI remote management                      ║
║  exchangeMDB/host      → Exchange mailbox access                     ║
╚══════════════════════════════════════════════════════════════════════╝
""")