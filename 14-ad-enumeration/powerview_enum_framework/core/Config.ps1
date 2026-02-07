<#
.SYNOPSIS
    Configuration settings for AD enumeration
.DESCRIPTION
    Contains privileged groups, output settings, and constants
#>

# Privileged groups to focus on during enumeration
$script:PrivilegedGroups = @(
    "Domain Admins",
    "Enterprise Admins",
    "Administrators",
    "Schema Admins",
    "Account Operators",
    "Backup Operators",
    "Server Operators",
    "DnsAdmins",
    "Print Operators",
    "Group Policy Creator Owners"
)

# Keywords that might indicate passwords in descriptions
$script:PasswordKeywords = @(
    'pass',
    'pwd',
    'password',
    'cred',
    'credential',
    'secret'
)

# Critical Active Directory Rights for ACL analysis
$script:CriticalADRights = @(
    'GenericAll',
    'WriteDacl',
    'WriteOwner',
    'GenericWrite',
    'WriteProperty'
)

# User properties to enumerate
$script:UserProperties = @(
    'samaccountname',
    'displayname',
    'description',
    'memberof',
    'admincount',
    'serviceprincipalname',
    'useraccountcontrol',
    'pwdlastset',
    'lastlogon',
    'whencreated',
    'title',
    'department'
)

# Computer properties to enumerate
$script:ComputerProperties = @(
    'name',
    'dnshostname',
    'operatingsystem',
    'operatingsystemversion',
    'useraccountcontrol',
    'msds-allowedtodelegateto',
    'ms-mcs-admpwd',
    'description'
)

# Export settings
function Get-PrivilegedGroups { return $script:PrivilegedGroups }
function Get-PasswordKeywords { return $script:PasswordKeywords }
function Get-CriticalADRights { return $script:CriticalADRights }
function Get-UserProperties { return $script:UserProperties }
function Get-ComputerProperties { return $script:ComputerProperties }