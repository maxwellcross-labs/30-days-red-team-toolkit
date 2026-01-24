"""
Process Manager
Utilities for managing SSH tunnel processes
"""

import subprocess
import re
from typing import List, Dict


class ProcessManager:
    """Manager for SSH tunnel processes"""

    @staticmethod
    def find_tunnel_processes() -> List[Dict]:
        """
        Find all SSH tunnel processes

        Returns:
            List of process dictionaries with pid, user, command
        """
        processes = []

        # Find SSH processes with port forwarding flags
        cmd = "ps aux | grep 'ssh.*-[LRD]' | grep -v grep"

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(None, 10)

                        if len(parts) >= 11:
                            processes.append({
                                'user': parts[0],
                                'pid': parts[1],
                                'cpu': parts[2],
                                'mem': parts[3],
                                'command': parts[10]
                            })

        except Exception as e:
            print(f"[-] Error finding processes: {e}")

        return processes

    @staticmethod
    def kill_process(pid: str) -> bool:
        """
        Kill a process by PID

        Args:
            pid: Process ID

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(f"kill {pid}", shell=True, check=True)
            print(f"[+] Killed PID: {pid}")
            return True

        except subprocess.CalledProcessError:
            print(f"[-] Failed to kill PID: {pid}")
            return False

        except Exception as e:
            print(f"[-] Error killing process: {e}")
            return False

    @staticmethod
    def kill_all_tunnels() -> int:
        """
        Kill all SSH tunnel processes

        Returns:
            Number of processes killed
        """
        print(f"\n[*] Killing all SSH tunnel processes...")

        processes = ProcessManager.find_tunnel_processes()

        if not processes:
            print(f"[*] No SSH tunnel processes found")
            return 0

        killed_count = 0

        for proc in processes:
            if ProcessManager.kill_process(proc['pid']):
                killed_count += 1

        print(f"\n[+] Killed {killed_count} SSH tunnel process(es)")

        return killed_count

    @staticmethod
    def list_processes():
        """List all SSH tunnel processes"""
        print(f"\n" + "=" * 80)
        print(f"SSH TUNNEL PROCESSES")
        print(f"=" * 80)

        processes = ProcessManager.find_tunnel_processes()

        if not processes:
            print(f"\n[*] No SSH tunnel processes found")
            return

        print(f"\n{'PID':<10} {'USER':<15} {'CPU%':<8} {'MEM%':<8} {'COMMAND'}")
        print(f"{'-' * 80}")

        for proc in processes:
            cmd = proc['command']
            if len(cmd) > 50:
                cmd = cmd[:47] + "..."

            print(f"{proc['pid']:<10} {proc['user']:<15} {proc['cpu']:<8} {proc['mem']:<8} {cmd}")

    @staticmethod
    def check_port_in_use(port: int) -> bool:
        """
        Check if a port is in use

        Args:
            port: Port number

        Returns:
            True if port is in use, False otherwise
        """
        cmd = f"lsof -i :{port} | grep LISTEN"

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            return result.returncode == 0

        except Exception:
            return False

    @staticmethod
    def get_port_info(port: int) -> Dict:
        """
        Get information about what's using a port

        Args:
            port: Port number

        Returns:
            Dictionary with port information
        """
        cmd = f"lsof -i :{port}"

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')

                if len(lines) > 1:
                    # Parse first data line
                    parts = lines[1].split()

                    return {
                        'port': port,
                        'command': parts[0] if len(parts) > 0 else 'unknown',
                        'pid': parts[1] if len(parts) > 1 else 'unknown',
                        'user': parts[2] if len(parts) > 2 else 'unknown'
                    }

        except Exception:
            pass

        return {'port': port, 'in_use': False}