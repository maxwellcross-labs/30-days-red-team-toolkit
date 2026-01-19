from reporter import Reporter
from modules import (
    privileges, services, tasks, registry,
    credentials, filesystem, kernel
)


class PrivEscEnumerator:
    def __init__(self, output_dir="privesc_enum"):
        print(f"[+] Privilege Escalation Enumerator initialized")
        print(f"[+] Output directory: {output_dir}")
        self.reporter = Reporter(output_dir)

    def run(self):
        print(f"\n" + "=" * 60)
        print(f"AUTOMATED PRIVILEGE ESCALATION ENUMERATION")
        print(f"=" * 60)

        # 1. Check Privileges
        is_admin = privileges.check_current_privileges(self.reporter)

        if is_admin:
            print(f"\n[!] Already running as Administrator")
            print(f"[*] Focusing on SYSTEM escalation methods...")

        # 2. Run Enumeration Modules
        services.enumerate_services(self.reporter)
        tasks.enumerate_scheduled_tasks(self.reporter)
        registry.enumerate_registry(self.reporter)
        credentials.enumerate_passwords(self.reporter)
        filesystem.enumerate_writable_paths(self.reporter)
        kernel.check_kernel_exploits(self.reporter)

        # 3. Finalize
        self.reporter.generate_report()