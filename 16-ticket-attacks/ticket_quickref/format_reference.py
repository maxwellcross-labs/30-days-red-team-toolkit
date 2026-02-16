"""
Ticket Format Conversion Reference — Commands for converting
between .kirbi (Windows), .ccache (Linux), and Base64 (Rubeus) formats.
"""


def print_ticket_format_conversion():
    """Print the ticket format conversion cheat sheet."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    TICKET FORMAT CONVERSION                         ║
╠══════════════════════════════════════════════════════════════════════╣
║  .kirbi → .ccache:  ticketConverter.py ticket.kirbi ticket.ccache   ║
║  .ccache → .kirbi:  ticketConverter.py ticket.ccache ticket.kirbi   ║
║  Base64 → .kirbi:   echo "BASE64" | base64 -d > ticket.kirbi       ║
║  Rubeus → file:     Rubeus.exe dump /nowrap → base64 -d > .kirbi   ║
╚══════════════════════════════════════════════════════════════════════╝
""")