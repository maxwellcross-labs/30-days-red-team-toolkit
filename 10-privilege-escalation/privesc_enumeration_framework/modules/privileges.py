# privesc_enumeration_framework/modules/privileges.py
import os
import ctypes
from utils.helpers import run_command


def _get_privilege_exploit(privilege):
    exploits = {
        'SeImpersonatePrivilege': 'Use JuicyPotato, RoguePotato, or PrintSpoofer',
        'SeAssignPrimaryTokenPrivilege': 'Use token manipulation tools',
        'SeDebugPrivilege': 'Inject into higher-privileged processes',
        'SeLoadDriverPrivilege': 'Load malicious kernel driver',
        'SeRestorePrivilege': 'Modify system files/registry',
        'SeTakeOwnershipPrivilege': 'Take ownership of privileged files',
        'SeTcbPrivilege': 'Act as part of the operating system'
    }
    return exploits.get(privilege, 'Research specific exploitation method')


def check_current_privileges(reporter):
    print(f"\n" + "=" * 60)
    print(f"CURRENT PRIVILEGE LEVEL")
    print(f"=" * 60)

    try:
        username = os.environ.get('USERNAME', 'Unknown')
        domain = os.environ.get('USERDOMAIN', 'Unknown')
        print(f"[*] Current User: {domain}\\{username}")

        is_admin = ctypes.windll.shell32.IsUserAnAdmin()

        if is_admin:
            print(f"[+] Administrator: YES")
            reporter.add_finding('info', {
                'category': 'Current Privileges',
                'finding': 'Already running as Administrator',
                'impact': 'High',
                'note': 'Can attempt SYSTEM escalation via token impersonation'
            })
        else:
            print(f"[-] Administrator: NO")
            print(f"[*] Need to escalate from User to Administrator")

        result = run_command("whoami /priv")
        print(f"\n[*] Current Privileges:")
        print(result.stdout)

        powerful_privs = [
            'SeDebugPrivilege', 'SeImpersonatePrivilege', 'SeAssignPrimaryTokenPrivilege',
            'SeTcbPrivilege', 'SeLoadDriverPrivilege', 'SeRestorePrivilege',
            'SeTakeOwnershipPrivilege'
        ]

        for priv in powerful_privs:
            if priv in result.stdout:
                # Check if Enabled
                if 'Enabled' in result.stdout.split(priv)[1].split('\n')[0]:
                    print(f"[+] Found enabled privilege: {priv}")
                    reporter.add_finding('high', {
                        'category': 'Dangerous Privileges',
                        'finding': f'{priv} is ENABLED',
                        'impact': 'Critical',
                        'exploitation': _get_privilege_exploit(priv)
                    })
        return is_admin

    except Exception as e:
        print(f"[-] Error checking privileges: {e}")
        return False