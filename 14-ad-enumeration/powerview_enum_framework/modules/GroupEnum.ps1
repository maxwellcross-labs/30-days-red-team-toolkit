<#
.SYNOPSIS
    Group enumeration module
.DESCRIPTION
    Enumerates domain groups with focus on privileged groups
#>

function Invoke-GroupEnumeration {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Params = @{}
    )

    Write-Host "`n[+] Enumerating Groups..." -ForegroundColor Green

    $results = @{
        AllGroups = @()
        PrivilegedGroupMembers = @{}
    }

    try {
        # Import configuration
        . "$PSScriptRoot\..\core\Config.ps1"
        $privGroups = Get-PrivilegedGroups

        # Get all groups
        $groups = Get-DomainGroup @Params
        $results.AllGroups = $groups

        # Export all groups
        $groups | Export-Csv "$OutputDir\groups_all.csv" -NoTypeInformation
        Write-Host "    Total Groups: $($groups.Count)" -ForegroundColor Cyan

        # Enumerate privileged groups
        Write-Host "`n    Privileged Group Membership:" -ForegroundColor Cyan

        foreach ($groupName in $privGroups) {
            try {
                $members = Get-DomainGroupMember @Params -Identity $groupName -Recurse -ErrorAction SilentlyContinue

                if ($members) {
                    $results.PrivilegedGroupMembers[$groupName] = $members

                    Write-Host "        $groupName`: $($members.Count) members" -ForegroundColor Yellow

                    # Export group members
                    $safeGroupName = $groupName.Replace(' ', '_')
                    $members | Export-Csv "$OutputDir\group_$safeGroupName.csv" -NoTypeInformation

                    # Show first 5 members
                    foreach ($member in ($members | Select-Object -First 5)) {
                        Write-Host "            - $($member.MemberName)" -ForegroundColor White
                    }
                    if ($members.Count -gt 5) {
                        Write-Host "            ... and $($members.Count - 5) more" -ForegroundColor White
                    }
                }
            } catch {
                # Silently skip groups that don't exist
            }
        }

    } catch {
        Write-Host "    [-] Group enumeration failed: $_" -ForegroundColor Red
    }

    return $results
}
