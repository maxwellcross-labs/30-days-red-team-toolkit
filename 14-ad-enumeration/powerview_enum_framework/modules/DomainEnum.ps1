<#
.SYNOPSIS
    Domain information enumeration module
.DESCRIPTION
    Enumerates basic domain information and domain controllers
#>

function Invoke-DomainEnumeration {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Params = @{}
    )

    Write-Host "`n[+] Enumerating Domain Information..." -ForegroundColor Green

    $results = @{
        DomainInfo = $null
        DomainControllers = @()
    }

    try {
        # Get domain information
        $domainInfo = Get-Domain @Params
        $results.DomainInfo = $domainInfo

        # Export domain info
        $domainInfo | Export-Csv "$OutputDir\domain_info.csv" -NoTypeInformation
        Write-Host "    Domain: $($domainInfo.Name)" -ForegroundColor Cyan
        Write-Host "    Forest: $($domainInfo.Forest)" -ForegroundColor Cyan

        # Get domain controllers
        $dcs = Get-DomainController @Params
        $results.DomainControllers = $dcs

        Write-Host "`n    Domain Controllers:" -ForegroundColor Cyan
        foreach ($dc in $dcs) {
            Write-Host "        $($dc.Name) - $($dc.IPAddress)" -ForegroundColor White
        }

        # Export DCs
        $dcs | Export-Csv "$OutputDir\domain_controllers.csv" -NoTypeInformation
        Write-Host "    [+] Found $($dcs.Count) domain controller(s)"

    } catch {
        Write-Host "    [-] Domain info enumeration failed: $_" -ForegroundColor Red
    }

    return $results
}