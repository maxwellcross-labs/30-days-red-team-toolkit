import os
from utils.helpers import run_command, check_file_permissions


def enumerate_services(reporter):
    print(f"\n" + "=" * 60)
    print(f"SERVICE ENUMERATION")
    print(f"=" * 60)

    try:
        cmd = 'wmic service get name,displayname,pathname,startmode,startname'
        result = run_command(cmd)

        services = []
        lines = result.stdout.split('\n')[1:]

        for line in lines:
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 3:
                    services.append({
                        'name': parts[1] if len(parts) > 1 else '',
                        'path': ' '.join(parts[2:-2]) if len(parts) > 4 else '',
                        'startmode': parts[-2] if len(parts) > 2 else '',
                        'startname': parts[-1] if len(parts) > 1 else ''
                    })

        print(f"[*] Found {len(services)} services")

        # Check unquoted paths
        print(f"\n[*] Checking for unquoted service paths...")
        for service in services:
            path = service.get('path', '')
            if path and ' ' in path and not path.startswith('"') and path.lower().endswith('.exe'):
                if path.count(' ') > 0:
                    print(f"[+] Found unquoted service path: {service['name']}")
                    reporter.add_finding('high', {
                        'category': 'Unquoted Service Path',
                        'service': service['name'],
                        'path': path,
                        'startmode': service['startmode'],
                        'exploitation': 'Place malicious executable in path with space',
                        'impact': 'High - Can execute as SYSTEM'
                    })

        # Check permissions
        print(f"\n[*] Checking service binary permissions...")
        for service in services:
            path = service.get('path', '').strip('"').split()[0]
            if path and os.path.exists(path):
                perm_result = check_file_permissions(path)
                if perm_result:
                    print(f"[+] Found service with weak permissions: {service['name']}")
                    reporter.add_finding('high', {
                        'category': 'Weak Service Permissions',
                        'service': service['name'],
                        'path': path,
                        'permissions': perm_result,
                        'exploitation': 'Replace service binary with malicious executable',
                        'impact': 'High - Execute as SYSTEM'
                    })

        print(f"\n[*] Service enumeration complete")
    except Exception as e:
        print(f"[-] Service enumeration failed: {e}")