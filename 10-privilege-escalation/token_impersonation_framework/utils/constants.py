"""
Constants for the Token Impersonation Framework.
"""

# Default tool paths
TOOL_PATHS = {
    'printspoofer': 'C:\\Windows\\Temp\\PrintSpoofer.exe',
    'roguepotato': 'C:\\Windows\\Temp\\RoguePotato.exe',
    'juicypotato': 'C:\\Windows\\Temp\\JuicyPotato.exe',
    'sweetpotato': 'C:\\Windows\\Temp\\SweetPotato.exe',
    'godpotato': 'C:\\Windows\\Temp\\GodPotato.exe'
}

# Tool download URLs
TOOL_URLS = {
    'printspoofer': 'https://github.com/itm4n/PrintSpoofer/releases',
    'roguepotato': 'https://github.com/antonioCoco/RoguePotato/releases',
    'juicypotato': 'https://github.com/ohpe/juicy-potato/releases',
    'sweetpotato': 'https://github.com/CCob/SweetPotato/releases',
    'godpotato': 'https://github.com/BeichenDream/GodPotato/releases'
}

# Required privileges for Potato attacks
IMPERSONATION_PRIVILEGES = [
    'SeImpersonatePrivilege',
    'SeAssignPrimaryTokenPrivilege'
]

# Additional useful privileges
ESCALATION_PRIVILEGES = [
    'SeDebugPrivilege',
    'SeTcbPrivilege',
    'SeBackupPrivilege',
    'SeRestorePrivilege',
    'SeCreateTokenPrivilege',
    'SeLoadDriverPrivilege',
    'SeTakeOwnershipPrivilege'
]

# Windows build numbers
WINDOWS_BUILDS = {
    'win10_1809': 17763,  # JuicyPotato patched
    'win10_1903': 18362,
    'win10_1909': 18363,
    'win10_2004': 19041,
    'win10_20h2': 19042,
    'win10_21h1': 19043,
    'win10_21h2': 19044,
    'win11_21h2': 22000,
    'server_2019': 17763,
    'server_2022': 20348
}

# Common CLSIDs for JuicyPotato
CLSIDS = {
    'bits': '{4991d34b-80a1-4291-83b6-3328366b9097}',
    'wuauserv': '{9B1F122C-2982-4e91-AA8B-E071D54F2A4D}',
    'schedule': '{0f87369f-a4e5-4cfc-bd3e-73e6154572dd}',
    'dcom_default': '{F087771F-D74F-4C1A-BB8A-E16ACA9124EA}',
    'msdtc': '{A6F6A6C9-1A5C-4E74-B66D-D2D69BBC8A5D}'
}

# Services that commonly have SeImpersonate
VULNERABLE_SERVICES = [
    'IIS (IUSR, IWAM)',
    'MSSQL Server',
    'Apache (XAMPP)',
    'Local Service accounts',
    'Network Service accounts',
    'SQL Server Agent'
]