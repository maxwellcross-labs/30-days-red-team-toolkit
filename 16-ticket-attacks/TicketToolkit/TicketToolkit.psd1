@{
    RootModule        = 'TicketToolkit.psm1'
    ModuleVersion     = '1.0.0'
    Author            = 'Maxwell Cross'
    Description       = 'Kerberos Ticket Attack Toolkit — Rubeus & Mimikatz wrapper for Overpass-the-Hash, Golden, Silver, and Diamond Ticket attacks.'

    FunctionsToExport = @(
        'Invoke-OverpassTheHash',
        'Invoke-GoldenTicket',
        'Invoke-SilverTicket',
        'Invoke-DiamondTicket',
        'Export-AllTickets'
    )

    CmdletsToExport   = @()
    VariablesToExport  = @()
    AliasesToExport    = @()
}