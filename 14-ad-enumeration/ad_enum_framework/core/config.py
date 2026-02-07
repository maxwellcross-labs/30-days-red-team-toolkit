"""
Configuration and constants for AD enumeration
"""

# Privileged groups to focus on during enumeration
PRIVILEGED_GROUPS = [
    'Domain Admins',
    'Enterprise Admins',
    'Administrators',
    'Schema Admins',
    'Account Operators',
    'Backup Operators',
    'Server Operators',
    'DnsAdmins',
    'Print Operators'
]

# Trust relationship mappings
TRUST_DIRECTIONS = {
    0: 'Disabled',
    1: 'Inbound',
    2: 'Outbound',
    3: 'Bidirectional'
}

TRUST_TYPES = {
    1: 'Windows NT',
    2: 'Active Directory',
    3: 'MIT Kerberos'
}

# User Account Control flags
UAC_FLAGS = {
    'DONT_REQ_PREAUTH': 0x400000,
    'TRUSTED_FOR_DELEGATION': 0x80000,
    'PASSWD_NOTREQD': 0x0020,
    'DONT_EXPIRE_PASSWORD': 0x10000,
    'ENCRYPTED_TEXT_PWD_ALLOWED': 0x0080
}

# LDAP attributes to query
USER_ATTRIBUTES = [
    'sAMAccountName',
    'userPrincipalName',
    'displayName',
    'memberOf',
    'adminCount',
    'servicePrincipalName',
    'userAccountControl',
    'pwdLastSet',
    'lastLogon',
    'description',
    'whenCreated',
    'title',
    'department'
]

COMPUTER_ATTRIBUTES = [
    'sAMAccountName',
    'dNSHostName',
    'operatingSystem',
    'operatingSystemVersion',
    'servicePrincipalName',
    'userAccountControl',
    'msDS-AllowedToDelegateTo',
    'ms-MCS-AdmPwd',
    'description'
]

GROUP_ATTRIBUTES = [
    'sAMAccountName',
    'member',
    'memberOf',
    'description'
]

# Keywords that might indicate passwords in descriptions
PASSWORD_KEYWORDS = [
    'password',
    'pwd',
    'pass',
    'cred',
    'credential'
]
