<#
.SYNOPSIS
    Quick loader for AD Enumeration Framework
.DESCRIPTION
    Loads PowerView and the AD Enumeration Framework
.EXAMPLE
    . .\Load-Framework.ps1
    Invoke-ADEnumeration -OutputDir C:\enum
#>

# Check if PowerView is already loaded
$powerViewLoaded = Get-Command Get-Domain -ErrorAction SilentlyContinue

if (-not $powerViewLoaded) {
    Write-Host "[*] PowerView not detected. Attempting to load..." -ForegroundColor Yellow

    # Try to find PowerView in common locations
    $powerViewPaths = @(
        ".\PowerView.ps1",
        "..\PowerView.ps1",
        "C:\Tools\PowerView.ps1",
        "$env:USERPROFILE\Desktop\PowerView.ps1"
    )

    $loaded = $false
    foreach ($path in $powerViewPaths) {
        if (Test-Path $path) {
            Write-Host "[+] Loading PowerView from: $path" -ForegroundColor Green
            . $path
            $loaded = $true
            break
        }
    }

    if (-not $loaded) {
        Write-Host "`n[!] PowerView.ps1 not found!" -ForegroundColor Red
        Write-Host "[!] Please download from: https://github.com/PowerShellMafia/PowerSploit" -ForegroundColor Red
        Write-Host "[!] Or specify the path manually:" -ForegroundColor Yellow
        Write-Host "    . C:\Path\To\PowerView.ps1" -ForegroundColor Yellow
        Write-Host "    . .\Invoke-ADEnumeration.ps1`n" -ForegroundColor Yellow
        return
    }
} else {
    Write-Host "[+] PowerView already loaded" -ForegroundColor Green
}

# Load the AD Enumeration Framework
Write-Host "[+] Loading AD Enumeration Framework..." -ForegroundColor Green
. "$PSScriptRoot\Invoke-ADEnumeration.ps1"

Write-Host "`n[+] Framework loaded successfully!" -ForegroundColor Green
Write-Host "`nUsage Examples:" -ForegroundColor Cyan
Write-Host "  Invoke-ADEnumeration" -ForegroundColor White
Write-Host "  Invoke-ADEnumeration -OutputDir C:\MyEnum" -ForegroundColor White
Write-Host "  Invoke-ADEnumeration -Domain contoso.com -Server DC01`n" -ForegroundColor White