from pathlib import Path

def write_file(path: Path, content: str):
    """Writes content to file"""
    with open(path, 'w') as f:
        f.write(content)
    print(f"[+] Script created: {path}")

def log_instruction(msg_list):
    """Prints usage instructions"""
    print(f"\n[*] Usage:")
    for msg in msg_list:
        print(f"    {msg}")

def ensure_dir(path_str):
    path = Path(path_str)
    path.mkdir(exist_ok=True)
    return path