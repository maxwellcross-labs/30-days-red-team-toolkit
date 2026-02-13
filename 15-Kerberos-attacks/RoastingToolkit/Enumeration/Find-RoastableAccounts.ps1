function Find-RoastableAccounts {
    <#
    .SYNOPSIS
        Enumerate Kerberoastable and AS-REP Roastable accounts via LDAP.

    .DESCRIPTION
        Queries Active Directory for user accounts with SPNs (Kerberoastable)
        and accounts without pre-authentication required (AS-REP Roastable).
        Highlights admin accounts for priority targeting.

    .EXAMPLE
        Find-RoastableAccounts
    #>

    Write-Host "`n[*] Finding Roastable Accounts" -ForegroundColor Cyan

    # ── Kerberoastable ──────────────────────────────────────────
    Write-Host "`n[*] Kerberoastable Users:" -ForegroundColor Green

    $searcher = New-Object System.DirectoryServices.DirectorySearcher
    $searcher.Filter = "(&(objectClass=user)(objectCategory=person)(servicePrincipalName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
    $searcher.PropertiesToLoad.AddRange(@('samaccountname', 'serviceprincipalname', 'admincount', 'description'))

    $kerbResults = $searcher.FindAll()
    foreach ($r in $kerbResults) {
        $name  = $r.Properties['samaccountname'][0]
        $spn   = $r.Properties['serviceprincipalname'][0]
        $admin = $r.Properties['admincount'][0] -eq 1
        $tag   = if ($admin) { " [ADMIN]" } else { "" }
        Write-Host "    $name$tag — SPN: $spn" -ForegroundColor $(if ($admin) { 'Red' } else { 'Yellow' })
    }
    Write-Host "    Total: $($kerbResults.Count)" -ForegroundColor Green

    # ── AS-REP Roastable ────────────────────────────────────────
    Write-Host "`n[*] AS-REP Roastable Users:" -ForegroundColor Green

    $searcher2 = New-Object System.DirectoryServices.DirectorySearcher
    $searcher2.Filter = "(&(objectClass=user)(objectCategory=person)(userAccountControl:1.2.840.113556.1.4.803:=4194304))"
    $searcher2.PropertiesToLoad.AddRange(@('samaccountname', 'admincount'))

    $asrepResults = $searcher2.FindAll()
    foreach ($r in $asrepResults) {
        $name = $r.Properties['samaccountname'][0]
        Write-Host "    $name" -ForegroundColor Yellow
    }
    Write-Host "    Total: $($asrepResults.Count)" -ForegroundColor Green
}