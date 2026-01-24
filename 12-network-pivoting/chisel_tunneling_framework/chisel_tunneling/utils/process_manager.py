import subprocess


class ProcessManager:
    """Manage Chisel processes"""

    @staticmethod
    def kill_all_chisel():
        print("\n[*] Killing all Chisel processes...")
        cmd = "ps aux | grep chisel | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null"
        subprocess.run(cmd, shell=True)
        print("[+] Done")
        return 0

    @staticmethod
    def list_processes():
        print("\n" + "=" * 60)
        print("CHISEL PROCESSES")
        print("=" * 60)
        subprocess.run("ps aux | grep chisel | grep -v grep", shell=True)