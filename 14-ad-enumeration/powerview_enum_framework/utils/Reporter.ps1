<#
.SYNOPSIS
    Report generation utility
.DESCRIPTION
    Generates summary reports from enumeration results
#>

function New-EnumerationSummary {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Results
    )

    Write-Host "`n[+] Generating Summary Report..." -ForegroundColor Green

    $summaryFile = Join-Path $OutputDir "enumeration_summary.txt"

    $summary = @"
==============================================================
ACTIVE DIRECTORY ENUMERATION SUMMARY
==============================================================
Enumeration Time: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

DOMAIN INFORMATION:
------------------
Domain: $($Results.Domain.DomainInfo.Name)
Forest: $($Results.Domain.DomainInfo.Forest)
Domain Controllers: $($Results.Domain.DomainControllers.Count)

USER STATISTICS:
----------------
Total Users: $($Results.Users.AllUsers.Count)
Privileged Users: $($Results.Users.PrivilegedUsers.Count)
Kerberoastable Users: $($Results.Users.KerberoastableUsers.Count)
AS-REP Roastable Users: $($Results.Users.ASREPRoastableUsers.Count)
Passwords in Description: $($Results.Users.PasswordsInDescription.Count)

GROUP STATISTICS:
-----------------
Total Groups: $($Results.Groups.AllGroups.Count)
Privileged Groups Enumerated: $($Results.Groups.PrivilegedGroupMembers.Count)

COMPUTER STATISTICS:
--------------------
Total Computers: $($Results.Computers.AllComputers.Count)
Unconstrained Delegation: $($Results.Computers.UnconstrainedDelegation.Count)
Constrained Delegation: $($Results.Computers.ConstrainedDelegation.Count)
LAPS Passwords Readable: $($Results.Computers.LAPSReadable.Count)

TRUST RELATIONSHIPS:
--------------------
Domain Trusts: $($Results.Trusts.Trusts.Count)

ACL FINDINGS:
-------------
Interesting ACLs: $($Results.ACLs.InterestingACLs.Count)
Critical ACLs: $($Results.ACLs.CriticalACLs.Count)

==============================================================
ATTACK SURFACE SUMMARY:
==============================================================
"@

    # Add high-value targets section
    if ($Results.Users.KerberoastableUsers.Count -gt 0) {
        $summary += "`n[HIGH] Kerberoastable accounts detected - Offline password attacks possible"
    }

    if ($Results.Users.ASREPRoastableUsers.Count -gt 0) {
        $summary += "`n[HIGH] AS-REP Roastable accounts detected - Pre-authentication not required"
    }

    if ($Results.Computers.UnconstrainedDelegation.Count -gt 0) {
        $summary += "`n[CRITICAL] Unconstrained delegation detected - Credential theft possible"
    }

    if ($Results.Computers.LAPSReadable.Count -gt 0) {
        $summary += "`n[CRITICAL] LAPS passwords readable - Local admin compromise possible"
    }

    if ($Results.Users.PasswordsInDescription.Count -gt 0) {
        $summary += "`n[HIGH] Passwords found in user descriptions - Immediate credential access"
    }

    if ($Results.ACLs.CriticalACLs.Count -gt 0) {
        $summary += "`n[HIGH] Critical ACL misconfigurations - Privilege escalation paths exist"
    }

    $summary += "`n==============================================================`n"

    # Write to file
    $summary | Out-File -FilePath $summaryFile -Encoding UTF8

    Write-Host "    [+] Summary saved to: $summaryFile" -ForegroundColor Cyan

    return $summaryFile
}

function New-AttackPathReport {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Results
    )

    $attackFile = Join-Path $OutputDir "attack_paths.txt"

    $report = @"
==============================================================
POTENTIAL ATTACK PATHS
==============================================================

"@

    # Kerberoasting path
    if ($Results.Users.KerberoastableUsers.Count -gt 0) {
        $report += @"
[1] KERBEROASTING ATTACK
------------------------
Target: $($Results.Users.KerberoastableUsers.Count) users with SPNs
Method: Request service tickets and crack offline
Tools: Rubeus.exe, GetUserSPNs.py (Impacket)

High-Value Targets:
"@
        foreach ($user in ($Results.Users.KerberoastableUsers | Where-Object { $_.admincount -eq 1 } | Select-Object -First 5)) {
            $report += "`n    - $($user.samaccountname) [PRIVILEGED]"
        }
        $report += "`n`n"
    }

    # AS-REP Roasting path
    if ($Results.Users.ASREPRoastableUsers.Count -gt 0) {
        $report += @"
[2] AS-REP ROASTING ATTACK
--------------------------
Target: $($Results.Users.ASREPRoastableUsers.Count) users without pre-auth
Method: Request AS-REP and crack offline
Tools: Rubeus.exe, GetNPUsers.py (Impacket)

Targets:
"@
        foreach ($user in ($Results.Users.ASREPRoastableUsers | Select-Object -First 5)) {
            $report += "`n    - $($user.samaccountname)"
        }
        $report += "`n`n"
    }

    # Unconstrained delegation path
    if ($Results.Computers.UnconstrainedDelegation.Count -gt 0) {
        $report += @"
[3] UNCONSTRAINED DELEGATION ABUSE
-----------------------------------
Target: $($Results.Computers.UnconstrainedDelegation.Count) computers
Method: Force auth to compromised host, extract TGT
Tools: Rubeus.exe, SpoolSample, PetitPotam

Vulnerable Computers:
"@
        foreach ($comp in ($Results.Computers.UnconstrainedDelegation | Select-Object -First 5)) {
            $report += "`n    - $($comp.name)"
        }
        $report += "`n`n"
    }

    $report += "==============================================================`n"

    $report | Out-File -FilePath $attackFile -Encoding UTF8

    Write-Host "    [+] Attack paths saved to: $attackFile" -ForegroundColor Cyan

    return $attackFile
}