<#
.SYNOPSIS
    Trust relationship enumeration module
.DESCRIPTION
    Enumerates domain trust relationships
#>

function Invoke-TrustEnumeration {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Params = @{}
    )

    Write-Host "`n[+] Enumerating Trusts..." -ForegroundColor Green

    $results = @{
        Trusts = @()
    }

    try {
        # Get domain trusts
        $trusts = Get-DomainTrust @Params
        $results.Trusts = $trusts

        if ($trusts) {
            # Export trusts
            $trusts | Export-Csv "$OutputDir\trusts.csv" -NoTypeInformation

            Write-Host "    Trusts Found: $($trusts.Count)" -ForegroundColor Cyan

            foreach ($trust in $trusts) {
                $direction = $trust.TrustDirection
                $type = $trust.TrustType
                Write-Host "        $($trust.TargetName)" -ForegroundColor Yellow
                Write-Host "            Direction: $direction" -ForegroundColor White
                Write-Host "            Type: $type" -ForegroundColor White
            }
        } else {
            Write-Host "    No trust relationships found" -ForegroundColor White
        }

    } catch {
        Write-Host "    [-] Trust enumeration failed: $_" -ForegroundColor Red
    }

    return $results
}