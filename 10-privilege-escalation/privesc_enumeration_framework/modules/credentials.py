import os
from utils.helpers import run_command


def enumerate_passwords(reporter):
    print(f"\n" + "=" * 60)
    print(f"STORED PASSWORD ENUMERATION")
    print(f"=" * 60)

    try:
        # 1. Cred Manager
        print(f"\n[*] Checking Windows Credential Manager...")
        result = run_command("cmdkey /list")
        if 'Target:' in result.stdout:
            print(f"[+] Found saved credentials:\n{result.stdout}")
            reporter.add_finding('medium', {
                'category': 'Saved Credentials',
                'finding': 'Credentials stored in Windows Credential Manager',
                'exploitation': 'Use runas with /savecred or extract with DPAPI',
                'impact': 'Medium - May contain privileged credentials'
            })
        else:
            print(f"[-] No saved credentials found")

        # 2. Unattend files
        print(f"\n[*] Checking for unattend.xml files...")
        unattend_paths = [
            'C:\\Windows\\Panther\\Unattend.xml',
            'C:\\Windows\\Panther\\Unattend\\Unattend.xml',
            'C:\\Windows\\System32\\Sysprep\\Unattend.xml'
        ]
        for path in unattend_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'Password' in content or 'password' in content:
                        print(f"[+] Found unattend file with passwords: {path}")
                        reporter.add_finding('high', {
                            'category': 'Unattend File',
                            'file': path,
                            'finding': 'Contains potential credentials',
                            'exploitation': 'Extract base64-encoded passwords',
                            'impact': 'High - Often contains admin credentials'
                        })

        # 3. GPP
        print(f"\n[*] Checking for GPP passwords...")
        gpp_path = 'C:\\ProgramData\\Microsoft\\Group Policy\\History'
        if os.path.exists(gpp_path):
            for root, dirs, files in os.walk(gpp_path):
                for file in files:
                    if file.lower() in ['groups.xml', 'services.xml', 'scheduledtasks.xml']:
                        full_path = os.path.join(root, file)
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if 'cpassword' in f.read().lower():
                                print(f"[+] Found GPP password file: {full_path}")
                                reporter.add_finding('high', {
                                    'category': 'Group Policy Preferences',
                                    'file': full_path,
                                    'finding': 'Contains encrypted password (cpassword)',
                                    'exploitation': 'Decrypt using known AES key',
                                    'impact': 'High - Often domain admin credentials'
                                })
        print(f"\n[*] Password enumeration complete")
    except Exception as e:
        print(f"[-] Password enumeration failed: {e}")