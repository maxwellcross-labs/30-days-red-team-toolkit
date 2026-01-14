import winreg
import os
from utils.helpers import run_command, check_file_permissions


def enumerate_registry(reporter):
    print(f"\n" + "=" * 60)
    print(f"REGISTRY ENUMERATION")
    print(f"=" * 60)

    try:
        # 1. AlwaysInstallElevated
        print(f"\n[*] Checking AlwaysInstallElevated...")
        try:
            key_hklm = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Policies\Microsoft\Windows\Installer', 0,
                                      winreg.KEY_READ)
            value_hklm = winreg.QueryValueEx(key_hklm, 'AlwaysInstallElevated')[0]
            winreg.CloseKey(key_hklm)

            key_hkcu = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Policies\Microsoft\Windows\Installer', 0,
                                      winreg.KEY_READ)
            value_hkcu = winreg.QueryValueEx(key_hkcu, 'AlwaysInstallElevated')[0]
            winreg.CloseKey(key_hkcu)

            if value_hklm == 1 and value_hkcu == 1:
                print(f"[+] AlwaysInstallElevated is ENABLED!")
                reporter.add_finding('high', {
                    'category': 'AlwaysInstallElevated',
                    'finding': 'MSI packages install with SYSTEM privileges',
                    'exploitation': 'Create malicious MSI, install to get SYSTEM shell',
                    'impact': 'Critical - Direct SYSTEM access'
                })
            else:
                print(f"[-] AlwaysInstallElevated not fully enabled")
        except:
            print(f"[-] AlwaysInstallElevated not configured")

        # 2. Auto runs
        print(f"\n[*] Checking Autorun registry keys...")
        autorun_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'),
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'),
            (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'),
            (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'),
        ]

        for hkey, path in autorun_keys:
            try:
                key = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        name, value, type_ = winreg.EnumValue(key, i)
                        if isinstance(value, str) and value:
                            exe_path = value.split()[0].strip('"')
                            if os.path.exists(exe_path):
                                perm_result = check_file_permissions(exe_path)
                                if perm_result:
                                    print(f"[+] Found writable autorun: {name}")
                                    reporter.add_finding('medium', {
                                        'category': 'Weak Autorun',
                                        'key': path,
                                        'name': name,
                                        'path': exe_path,
                                        'exploitation': 'Replace executable with malicious binary',
                                        'impact': 'Medium - Execute at user login'
                                    })
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except:
                pass
        print(f"\n[*] Registry enumeration complete")
    except Exception as e:
        print(f"[-] Registry enumeration failed: {e}")