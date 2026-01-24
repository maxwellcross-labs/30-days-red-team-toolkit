import subprocess


class BinaryManager:
    """Manage Chisel binary"""

    @staticmethod
    def check_chisel():
        try:
            result = subprocess.run(['chisel', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] Chisel found")
                return True, result.stdout
        except:
            pass
        return False, "Chisel not found"

    @staticmethod
    def get_installation_instructions():
        return """
Install Chisel:
  wget https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_linux_amd64.gz
  gunzip chisel_1.9.1_linux_amd64.gz
  chmod +x chisel_1.9.1_linux_amd64
  sudo mv chisel_1.9.1_linux_amd64 /usr/local/bin/chisel
"""