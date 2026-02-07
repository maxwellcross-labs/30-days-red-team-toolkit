<#
.SYNOPSIS
    ACL enumeration module
.DESCRIPTION
    Enumerates interesting ACLs for privilege escalation paths
#>

function Invoke-ACLEnumeration {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Params = @{}
    )

    Write-Host "`n[+] Enumerating Interesting ACLs..." -ForegroundColor Green

    $results = @{
        InterestingACLs = @()
        CriticalACLs = @()
    }

    try {
        # Import configuration
        . "$PSScriptRoot\..\core\Config.ps1"
        $criticalRights = Get-CriticalADRights

        # Find interesting ACLs
        $interestingAcls = Find-InterestingDomainAcl @Params -ResolveGUIDs
        $results.InterestingACLs = $interestingAcls

        if ($interestingAcls) {
            # Export all interesting ACLs
            $interestingAcls | Export-Csv "$OutputDir\interesting_acls.csv" -NoTypeInformation
            Write-Host "    Interesting ACLs: $($interestingAcls.Count)" -ForegroundColor Cyan

            # Filter for critical ACLs
            $criticalAcls = $interestingAcls | Where-Object {
                $rights = $_.ActiveDirectoryRights
                $criticalRights | Where-Object { $rights -match $_ }
            }
            $results.CriticalACLs = $criticalAcls

            if ($criticalAcls.Count -gt 0) {
                Write-Host "`n    [!] Critical ACL Findings:" -ForegroundColor Red

                $criticalAcls | Export-Csv "$OutputDir\critical_acls.csv" -NoTypeInformation

                # Show first 10 critical ACLs
                foreach ($acl in ($criticalAcls | Select-Object -First 10)) {
                    $identity = $acl.IdentityReferenceName
                    $object = $acl.ObjectDN
                    $rights = $acl.ActiveDirectoryRights

                    Write-Host "        $identity -> $object" -ForegroundColor Yellow
                    Write-Host "            Rights: $rights" -ForegroundColor White
                }

                if ($criticalAcls.Count -gt 10) {
                    Write-Host "        ... and $($criticalAcls.Count - 10) more critical ACLs" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "    No interesting ACLs found" -ForegroundColor White
        }

    } catch {
        Write-Host "    [-] ACL enumeration failed: $_" -ForegroundColor Red
    }

    return $results
}