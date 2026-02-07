<#
.SYNOPSIS
    Computer enumeration module
.DESCRIPTION
    Enumerates domain computers and identifies delegation vulnerabilities
#>

function Invoke-ComputerEnumeration {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Params = @{}
    )

    Write-Host "`n[+] Enumerating Computers..." -ForegroundColor Green

    $results = @{
        AllComputers = @()
        UnconstrainedDelegation = @()
        ConstrainedDelegation = @()
        LAPSReadable = @()
    }

    try {
        # Import configuration
        . "$PSScriptRoot\..\core\Config.ps1"
        $compProps = Get-ComputerProperties

        # Get all computers
        $computers = Get-DomainComputer @Params -Properties $compProps
        $results.AllComputers = $computers

        # Export all computers
        $computers | Export-Csv "$OutputDir\computers_all.csv" -NoTypeInformation
        Write-Host "    Total Computers: $($computers.Count)" -ForegroundColor Cyan

        # Count servers vs workstations
        $servers = $computers | Where-Object { $_.operatingsystem -match 'Server' }
        $workstations = $computers | Where-Object { $_.operatingsystem -notmatch 'Server' }
        Write-Host "        Servers: $($servers.Count)" -ForegroundColor White
        Write-Host "        Workstations: $($workstations.Count)" -ForegroundColor White

        # Check for unconstrained delegation (excluding DCs)
        $unconDel = Get-DomainComputer @Params -Unconstrained |
            Where-Object { $_.operatingsystem -notmatch 'Domain Controller' }
        $results.UnconstrainedDelegation = $unconDel

        if ($unconDel.Count -gt 0) {
            Write-Host "`n    [!] Unconstrained Delegation (Non-DC):" -ForegroundColor Red
            foreach ($comp in $unconDel) {
                Write-Host "        $($comp.name)" -ForegroundColor Yellow
            }
            $unconDel | Export-Csv "$OutputDir\computers_unconstrained.csv" -NoTypeInformation
        }

        # Check for constrained delegation
        $conDel = $computers | Where-Object { $_.'msds-allowedtodelegateto' }
        $results.ConstrainedDelegation = $conDel

        if ($conDel.Count -gt 0) {
            Write-Host "`n    [!] Constrained Delegation:" -ForegroundColor Red
            foreach ($comp in $conDel) {
                $targets = $_.'msds-allowedtodelegateto' -join ', '
                Write-Host "        $($comp.name) -> $targets" -ForegroundColor Yellow
            }
            $conDel | Export-Csv "$OutputDir\computers_constrained.csv" -NoTypeInformation
        }

        # Check for readable LAPS passwords
        $lapsEnabled = $computers | Where-Object {
            $_.'ms-mcs-admpwd' -and $_.'ms-mcs-admpwd' -ne $null
        }
        $results.LAPSReadable = $lapsEnabled

        if ($lapsEnabled.Count -gt 0) {
            Write-Host "`n    [!] LAPS Passwords Readable:" -ForegroundColor Red
            foreach ($comp in $lapsEnabled) {
                Write-Host "        $($comp.name): $($_.'ms-mcs-admpwd')" -ForegroundColor Red
            }
            $lapsEnabled | Export-Csv "$OutputDir\computers_laps_readable.csv" -NoTypeInformation
        }

    } catch {
        Write-Host "    [-] Computer enumeration failed: $_" -ForegroundColor Red
    }

    return $results
}