<#
.SYNOPSIS
    User enumeration module
.DESCRIPTION
    Enumerates domain users and identifies attack vectors
#>

function Invoke-UserEnumeration {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Params = @{}
    )

    Write-Host "`n[+] Enumerating Users..." -ForegroundColor Green

    $results = @{
        AllUsers = @()
        PrivilegedUsers = @()
        KerberoastableUsers = @()
        ASREPRoastableUsers = @()
        PasswordsInDescription = @()
    }

    try {
        # Import configuration
        . "$PSScriptRoot\..\core\Config.ps1"
        $userProps = Get-UserProperties
        $passwordKeywords = Get-PasswordKeywords

        # Get all users
        $users = Get-DomainUser @Params -Properties $userProps
        $results.AllUsers = $users

        # Export all users
        $users | Export-Csv "$OutputDir\users_all.csv" -NoTypeInformation
        Write-Host "    Total Users: $($users.Count)" -ForegroundColor Cyan

        # Identify privileged users (adminCount = 1)
        $privUsers = $users | Where-Object { $_.admincount -eq 1 }
        $results.PrivilegedUsers = $privUsers

        $privUsers | Export-Csv "$OutputDir\users_privileged.csv" -NoTypeInformation
        Write-Host "    Privileged Users (adminCount=1): $($privUsers.Count)" -ForegroundColor Yellow

        # Identify Kerberoastable users
        $kerbUsers = Get-DomainUser @Params -SPN
        $results.KerberoastableUsers = $kerbUsers

        $kerbUsers | Export-Csv "$OutputDir\users_kerberoastable.csv" -NoTypeInformation
        Write-Host "    Kerberoastable Users: $($kerbUsers.Count)" -ForegroundColor Yellow

        if ($kerbUsers.Count -gt 0) {
            Write-Host "`n    [!] Kerberoastable Users Found:" -ForegroundColor Red
            foreach ($user in $kerbUsers | Select-Object -First 10) {
                $spn = if ($user.serviceprincipalname) { $user.serviceprincipalname[0] } else { "N/A" }
                Write-Host "        $($user.samaccountname): $spn" -ForegroundColor Yellow
            }
            if ($kerbUsers.Count -gt 10) {
                Write-Host "        ... and $($kerbUsers.Count - 10) more" -ForegroundColor Yellow
            }
        }

        # Identify AS-REP Roastable users
        $asrepUsers = Get-DomainUser @Params -PreauthNotRequired
        $results.ASREPRoastableUsers = $asrepUsers

        $asrepUsers | Export-Csv "$OutputDir\users_asreproastable.csv" -NoTypeInformation
        Write-Host "    AS-REP Roastable Users: $($asrepUsers.Count)" -ForegroundColor Yellow

        # Check for passwords in descriptions
        $passInDesc = $users | Where-Object {
            $desc = $_.description
            if ($desc) {
                $passwordKeywords | Where-Object { $desc -match $_ }
            }
        }
        $results.PasswordsInDescription = $passInDesc

        if ($passInDesc.Count -gt 0) {
            Write-Host "`n    [!] Potential Passwords in Description:" -ForegroundColor Red
            foreach ($user in $passInDesc) {
                Write-Host "        $($user.samaccountname): $($user.description)" -ForegroundColor Red
            }
            $passInDesc | Export-Csv "$OutputDir\users_passwords_in_desc.csv" -NoTypeInformation
        }

    } catch {
        Write-Host "    [-] User enumeration failed: $_" -ForegroundColor Red
    }

    return $results
}