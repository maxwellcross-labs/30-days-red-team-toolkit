import subprocess
import os


def run_command(cmd):
    """Run a shell command and return the result object."""
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except Exception as e:
        print(f"[-] Command failed: {cmd} ({e})")
        return None


def check_file_permissions(path):
    """
    Checks a file path for weak permissions using icacls.
    Returns the specific weak permission found (e.g., 'Everyone (F)') or None.
    """
    if not path or not os.path.exists(path):
        return None

    cmd = f'icacls "{path}"'
    result = run_command(cmd)

    if not result or not result.stdout:
        return None

    # Look for weak permissions
    # (F) = Full, (M) = Modify, (W) = Write
    weak_perms = ['(F)', '(M)', '(W)']

    for perm in weak_perms:
        if perm in result.stdout and 'Everyone' in result.stdout:
            return f"Everyone {perm}"

    return None