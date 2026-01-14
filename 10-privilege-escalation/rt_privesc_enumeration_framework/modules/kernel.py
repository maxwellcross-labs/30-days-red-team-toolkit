from utils.helpers import run_command


def check_kernel_exploits(reporter):
    print(f"\n" + "=" * 60)
    print(f"KERNEL EXPLOIT SUGGESTIONS")
    print(f"=" * 60)

    try:
        result = run_command("systeminfo")
        version_info = {}
        for line in result.stdout.split('\n'):
            if 'OS Name:' in line:
                version_info['os_name'] = line.split(':')[1].strip()
            elif 'OS Version:' in line:
                version_info['os_version'] = line.split(':')[1].strip()
            elif 'System Type:' in line:
                version_info['architecture'] = line.split(':')[1].strip()

        print(f"[*] OS: {version_info.get('os_name', 'Unknown')}")
        print(f"[*] Version: {version_info.get('os_version', 'Unknown')}")

        result_hotfix = run_command("wmic qfe get HotFixID")
        hotfixes = [line.strip() for line in result_hotfix.stdout.split('\n')[1:] if line.strip()]

        print(f"\n[*] Installed hotfixes: {len(hotfixes)}")
        print(f"\n[!] NOTE: Use Windows-Exploit-Suggester for comprehensive analysis")

        reporter.add_finding('low', {
            'category': 'Kernel Exploits',
            'note': 'Check with Windows-Exploit-Suggester',
            'os_version': version_info.get('os_version', 'Unknown'),
            'hotfixes_installed': len(hotfixes),
            'impact': 'Critical - Can achieve SYSTEM but may crash system'
        })
    except Exception as e:
        print(f"[-] Kernel exploit check failed: {e}")