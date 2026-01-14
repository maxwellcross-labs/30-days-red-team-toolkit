import os


def enumerate_writable_paths(reporter):
    print(f"\n" + "=" * 60)
    print(f"WRITABLE PATH ENUMERATION")
    print(f"=" * 60)

    try:
        path_dirs = os.environ.get('PATH', '').split(';')
        print(f"[*] Checking PATH directories for write access...")

        for directory in path_dirs:
            if directory and os.path.exists(directory):
                test_file = os.path.join(directory, 'test_write.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    print(f"[+] Writable PATH directory: {directory}")
                    reporter.add_finding('medium', {
                        'category': 'Writable PATH',
                        'directory': directory,
                        'exploitation': 'Place malicious executable to hijack commands',
                        'impact': 'Medium - DLL hijacking or command hijacking'
                    })
                except:
                    pass
        print(f"\n[*] Writable path enumeration complete")
    except Exception as e:
        print(f"[-] Writable path enumeration failed: {e}")