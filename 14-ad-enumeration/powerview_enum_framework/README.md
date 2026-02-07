# PowerView AD Enumeration Framework

A modular PowerShell framework for comprehensive Active Directory enumeration using PowerView. Built for red team operations with organized, maintainable code structure.

## Features

- **Modular Architecture** - Separate modules for each enumeration category
- **Domain Enumeration** - Discover domain info and domain controllers
- **User Enumeration** - Identify users, privileged accounts, and attack vectors
- **Group Enumeration** - Map group memberships with focus on privileged groups
- **Computer Enumeration** - Find computers, delegation vulnerabilities, and LAPS
- **Trust Enumeration** - Discover domain trust relationships
- **ACL Enumeration** - Identify dangerous ACL misconfigurations
- **Automated Reporting** - Generate summaries and attack path reports

## Attack Vectors Detected

✓ **Kerberoastable Users** - Accounts with SPNs for offline cracking  
✓ **AS-REP Roastable Users** - Accounts without Kerberos pre-authentication  
✓ **Unconstrained Delegation** - Computers vulnerable to credential theft  
✓ **Constrained Delegation** - Potential privilege escalation paths  
✓ **LAPS Passwords** - Readable local admin passwords  
✓ **Passwords in Descriptions** - Cleartext credentials in user attributes  
✓ **Critical ACL Misconfigurations** - GenericAll, WriteDacl, WriteOwner  
✓ **Privileged Group Membership** - Domain Admins, Enterprise Admins, etc.

## Prerequisites

**PowerView** is required for this framework to function. Download from:
```
https://github.com/PowerShellMafia/PowerSploit/blob/master/Recon/PowerView.ps1
```

## Installation

```powershell
# 1. Download PowerView.ps1 to the same directory
# 2. Clone or download this framework
# 3. Load the framework
. .\Load-Framework.ps1
```

## Usage

### Quick Start
```powershell
# Load PowerView and framework
. .\Load-Framework.ps1

# Run full enumeration (default: C:\AD_Enum)
Invoke-ADEnumeration
```

### Custom Output Directory
```powershell
Invoke-ADEnumeration -OutputDir C:\MyRecon
```

### Target Specific Domain
```powershell
Invoke-ADEnumeration -Domain contoso.com -Server DC01
```

### Manual Loading (without Load-Framework.ps1)
```powershell
# Load PowerView first
. .\PowerView.ps1

# Load the framework
. .\Invoke-ADEnumeration.ps1

# Run enumeration
Invoke-ADEnumeration
```

## Project Structure

```
powerview_enum_framework/
│
├── Load-Framework.ps1              # Quick loader script
├── Invoke-ADEnumeration.ps1        # Main orchestrator
│
├── core/
│   └── Config.ps1                  # Constants and configuration
│
├── modules/
│   ├── DomainEnum.ps1              # Domain information
│   ├── UserEnum.ps1                # User enumeration
│   ├── GroupEnum.ps1               # Group enumeration
│   ├── ComputerEnum.ps1            # Computer enumeration
│   ├── TrustEnum.ps1               # Trust enumeration
│   └── ACLEnum.ps1                 # ACL enumeration
│
└── utils/
    └── Reporter.ps1                # Report generation
```

## Output Files

The framework generates multiple CSV files and reports:

### CSV Exports
- `domain_info.csv` - Domain information
- `domain_controllers.csv` - List of DCs
- `users_all.csv` - All domain users
- `users_privileged.csv` - Users with adminCount=1
- `users_kerberoastable.csv` - Users with SPNs
- `users_asreproastable.csv` - Users without pre-auth
- `groups_all.csv` - All groups
- `group_*.csv` - Privileged group memberships
- `computers_all.csv` - All computers
- `computers_unconstrained.csv` - Unconstrained delegation
- `computers_constrained.csv` - Constrained delegation
- `trusts.csv` - Domain trusts
- `interesting_acls.csv` - All interesting ACLs
- `critical_acls.csv` - Critical ACL findings

### Reports
- `enumeration_summary.txt` - Executive summary with statistics
- `attack_paths.txt` - Potential attack paths and methods

## Module Breakdown

### Core Module
**Config.ps1** - Centralized configuration
- Privileged groups to enumerate
- Password keywords for detection
- Critical AD rights definitions
- User and computer properties to query

### Enumeration Modules

**DomainEnum.ps1** - Domain discovery
- Queries domain information
- Enumerates domain controllers
- Exports domain metadata

**UserEnum.ps1** - User reconnaissance
- Discovers all domain users
- Identifies privileged accounts
- Finds Kerberoastable users
- Detects AS-REP roastable users
- Locates passwords in descriptions

**GroupEnum.ps1** - Group analysis
- Enumerates all groups
- Maps privileged group memberships
- Recursive membership resolution

**ComputerEnum.ps1** - Computer discovery
- Lists all domain computers
- Identifies delegation vulnerabilities
- Checks for readable LAPS passwords
- Categorizes servers vs workstations

**TrustEnum.ps1** - Trust mapping
- Discovers domain trusts
- Identifies trust direction and type
- Exports trust relationships

**ACLEnum.ps1** - ACL analysis
- Finds interesting ACLs
- Identifies critical misconfigurations
- Detects privilege escalation paths

### Utilities

**Reporter.ps1** - Report generation
- Creates executive summaries
- Generates attack path reports
- Highlights high-value targets

## Extending the Framework

To add new enumeration capabilities:

1. Create a new module in `modules/YourModule.ps1`
2. Implement the enumeration function
3. Import in `Invoke-ADEnumeration.ps1`
4. Call in the main enumeration flow
5. Add results to the report generators

Example module structure:
```powershell
function Invoke-YourEnumeration {
    [CmdletBinding()]
    param(
        [string]$OutputDir,
        [hashtable]$Params = @{}
    )
    
    # Your enumeration logic here
    $results = @{}
    
    return $results
}
```

## OPSEC Considerations

⚠️ **This framework generates extensive LDAP queries**
- All queries are logged by domain controllers
- Defenders may detect unusual query patterns
- Use credentials with legitimate access
- Consider spreading enumeration over time
- Test detection capabilities in your own lab

## PowerView Functions Used

This framework leverages the following PowerView functions:
- `Get-Domain`
- `Get-DomainController`
- `Get-DomainUser`
- `Get-DomainGroup`
- `Get-DomainGroupMember`
- `Get-DomainComputer`
- `Get-DomainTrust`
- `Find-InterestingDomainAcl`

## Tips for Red Team Operations

1. **Start with domain info** - Understand the environment first
2. **Prioritize Kerberoastable accounts** - Quick wins with offline cracking
3. **Check for unconstrained delegation** - High-impact credential theft
4. **Review ACLs carefully** - Often reveals hidden privilege paths
5. **Document everything** - CSV outputs are crucial for reporting

## Troubleshooting

**PowerView not loading?**
- Ensure PowerView.ps1 is in the same directory
- Check execution policy: `Set-ExecutionPolicy Bypass -Scope Process`
- Manually specify path: `. C:\Path\To\PowerView.ps1`

**Access denied errors?**
- Verify domain credentials have read access
- Try specifying a different DC with `-Server`
- Some queries require privileged access

**Empty results?**
- Confirm connectivity to domain controller
- Check if the domain parameter is correct
- Verify PowerView is loaded: `Get-Command Get-Domain`

## Legal Notice

This tool is for authorized security testing only. Ensure you have explicit permission before running against any domain.

## Credits

Built for the "30 Days of Red Team" series  
Powered by PowerView from PowerSploit  