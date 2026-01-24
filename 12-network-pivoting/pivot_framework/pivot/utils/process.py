import subprocess

def run_command(cmd_list, timeout=5):
    """Executes a system command safely"""
    try:
        subprocess.run(cmd_list, capture_output=True, timeout=timeout)
        return True
    except subprocess.TimeoutExpired:
        # SSH -N (no command) hangs by design, so timeout often means success
        return True
    except Exception as e:
        print(f"[-] System Error: {e}")
        return False