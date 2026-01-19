"""
Constants for the AlwaysInstallElevated Framework.
"""

# Registry paths for AlwaysInstallElevated
REGISTRY_PATHS = {
    'hklm': r'HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer',
    'hkcu': r'HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer',
    'value_name': 'AlwaysInstallElevated'
}

# MSI error codes
MSI_ERROR_CODES = {
    0: 'Success',
    13: 'Invalid data',
    87: 'Invalid parameter',
    1601: 'Windows Installer not accessible',
    1602: 'User cancelled installation',
    1603: 'Fatal error during installation',
    1604: 'Installation suspended, incomplete',
    1605: 'This action is only valid for products that are currently installed',
    1618: 'Another installation is already in progress',
    1619: 'Installation package could not be opened',
    1620: 'Installation package could not be opened (path)',
    1621: 'Error starting Windows Installer service UI',
    1622: 'Error opening installation log file',
    1623: 'Language not supported',
    1624: 'Error applying transforms',
    1625: 'Installation prohibited by system policy',
    1626: 'Function could not be executed',
    1627: 'Function failed during execution',
    1628: 'Invalid or unknown table specified',
    1629: 'Data supplied is of wrong type',
    1630: 'Data of this type is not supported',
    1631: 'Windows Installer service failed to start',
    1632: 'Temp folder full or inaccessible',
    1633: 'Platform not supported',
    1634: 'Component not found',
    1635: 'Patch package could not be opened',
    1636: 'Patch package is invalid',
    1637: 'Patch package cannot be processed',
    1638: 'Another version of this product is already installed',
    1639: 'Invalid command line argument',
    1640: 'Installation from terminal server client session not permitted',
    1641: 'Installer initiated restart',
    1642: 'Installer cannot install upgrade patch',
    3010: 'Restart required'
}

# Tool download URLs
TOOL_URLS = {
    'msfvenom': 'https://www.metasploit.com/',
    'wix': 'https://wixtoolset.org/releases/',
    'msi_wrapper': 'https://www.exemsi.com/'
}

# Default payload settings
DEFAULT_PAYLOADS = {
    'username': 'hacker',
    'password': 'Password123!',
    'lport': 4444
}

# Common msfvenom payloads for MSI
MSFVENOM_PAYLOADS = {
    'reverse_tcp_x64': 'windows/x64/shell_reverse_tcp',
    'reverse_tcp_x86': 'windows/shell_reverse_tcp',
    'meterpreter_x64': 'windows/x64/meterpreter/reverse_tcp',
    'meterpreter_x86': 'windows/meterpreter/reverse_tcp',
    'exec_x64': 'windows/x64/exec',
    'exec_x86': 'windows/exec'
}