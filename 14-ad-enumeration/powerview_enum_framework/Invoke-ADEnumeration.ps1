<#
.SYNOPSIS
    Active Directory Enumeration Framework - Main Orchestrator
.DESCRIPTION
    Coordinates all enumeration modules and generates comprehensive reports
.NOTES
    Requires PowerView.ps1 to be loaded first
.EXAMPLE
    . .\PowerView.ps1
    . .\Invoke-ADEnumeration.ps1
    Invoke-ADEnumeration -OutputDir C:\AD_Enum
.EXAMPLE
    Invoke-ADEnumeration -OutputDir C:\AD_Enum -Domain contoso.com -Server DC01
#>

# Import all modules
. "$PSScriptRoot\core\Config.ps1"
. "$PSScriptRoot\modules\DomainEnum.ps1"
. "$PSScriptRoot\modules\UserEnum.ps1"
. "$PSScriptRoot\modules\GroupEnum.ps1"
. "$PSScriptRoot\modules\ComputerEnum.ps1"
. "$PSScriptRoot\modules\TrustEnum.ps1"
. "$PSScriptRoot\modules\ACLEnum.ps1"
. "$PSScriptRoot\utils\Reporter.ps1"

function Invoke-ADEnumeration {
    <#
    .SYNOPSIS
        Execute full Active Directory enumeration
    .PARAMETER OutputDir
        Directory to save enumeration results
    .PARAMETER Domain
        Target domain (optional, defaults to current domain)
    .PARAMETER Server
        Domain controller to query (optional)
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$OutputDir = "C:\AD_Enum",

        [Parameter(Mandatory=$false)]
        [string]$Domain = $null,

        [Parameter(Mandatory=$false)]
        [string]$Server = $null
    )

    # Create output directory
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
    }

    # Print banner
    Write-Host "`n" + ("="*60) -ForegroundColor Cyan
    Write-Host "ACTIVE DIRECTORY ENUMERATION FRAMEWORK" -ForegroundColor Cyan
    Write-Host ("="*60) -ForegroundColor Cyan
    Write-Host "[*] Output Directory: $OutputDir" -ForegroundColor White

    # Build parameters for PowerView functions
    $params = @{}
    if ($Domain) {
        $params['Domain'] = $Domain
        Write-Host "[*] Target Domain: $Domain" -ForegroundColor White
    }
    if ($Server) {
        $params['Server'] = $Server
        Write-Host "[*] Domain Controller: $Server" -ForegroundColor White
    }

    # Initialize results collection
    $allResults = @{
        Domain = @{}
        Users = @{}
        Groups = @{}
        Computers = @{}
        Trusts = @{}
        ACLs = @{}
    }

    # Execute enumeration modules
    try {
        # Domain enumeration
        $allResults.Domain = Invoke-DomainEnumeration -OutputDir $OutputDir -Params $params

        # User enumeration
        $allResults.Users = Invoke-UserEnumeration -OutputDir $OutputDir -Params $params

        # Group enumeration
        $allResults.Groups = Invoke-GroupEnumeration -OutputDir $OutputDir -Params $params

        # Computer enumeration
        $allResults.Computers = Invoke-ComputerEnumeration -OutputDir $OutputDir -Params $params

        # Trust enumeration
        $allResults.Trusts = Invoke-TrustEnumeration -OutputDir $OutputDir -Params $params

        # ACL enumeration
        $allResults.ACLs = Invoke-ACLEnumeration -OutputDir $OutputDir -Params $params

    } catch {
        Write-Host "`n[-] Enumeration error: $_" -ForegroundColor Red
    }

    # Generate reports
    Write-Host "`n" + ("="*60) -ForegroundColor Cyan
    Write-Host "GENERATING REPORTS" -ForegroundColor Cyan
    Write-Host ("="*60) -ForegroundColor Cyan

    try {
        $summaryFile = New-EnumerationSummary -OutputDir $OutputDir -Results $allResults
        $attackFile = New-AttackPathReport -OutputDir $OutputDir -Results $allResults

        Write-Host "`n[+] Summary Report: $summaryFile" -ForegroundColor Green
        Write-Host "[+] Attack Paths: $attackFile" -ForegroundColor Green

    } catch {
        Write-Host "[-] Report generation error: $_" -ForegroundColor Red
    }

    # Final summary
    Write-Host "`n" + ("="*60) -ForegroundColor Cyan
    Write-Host "ENUMERATION COMPLETE" -ForegroundColor Cyan
    Write-Host ("="*60) -ForegroundColor Cyan
    Write-Host "[+] Results saved to: $OutputDir" -ForegroundColor Green
    Write-Host "`n"

    return $allResults
}

# Export the main function
Export-ModuleMember -Function Invoke-ADEnumeration