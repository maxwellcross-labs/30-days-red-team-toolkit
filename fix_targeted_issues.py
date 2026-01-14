"""
================================================================================
30 Days of Red Team - Final Import Fixes
================================================================================

Fixes the remaining issues:
1. Missing output/formatters.py modules
2. Missing ManifestGenerator export
3. payload.payload import issue
4. Windows path escaping in chrome.py/edge.py

================================================================================
"""

import re
import sys
from pathlib import Path


def create_formatters_module(output_dir: Path) -> bool:
    """Create a formatters.py module in an output directory."""
    formatters_file = output_dir / 'formatters.py'

    if formatters_file.exists():
        return False

    content = '''"""
Output formatters for displaying and exporting results.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class OutputFormatter:
    """Base class for output formatting."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def format_header(self, title: str) -> str:
        """Format a section header."""
        return f"\\n{'='*60}\\n  {title}\\n{'='*60}\\n"
    
    def format_item(self, key: str, value: Any) -> str:
        """Format a key-value item."""
        return f"  {key}: {value}"
    
    def format_list(self, items: List[Any]) -> str:
        """Format a list of items."""
        return "\\n".join(f"  - {item}" for item in items)
    
    def format_table(self, headers: List[str], rows: List[List[Any]]) -> str:
        """Format data as a table."""
        if not rows:
            return "  No data"
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))
        
        # Build table
        lines = []
        header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        for row in rows:
            row_line = " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            lines.append(row_line)
        
        return "\\n".join(lines)


class JSONFormatter(OutputFormatter):
    """Format output as JSON."""
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """Format results as JSON string."""
        import json
        return json.dumps(results, indent=2, default=str)


class TextFormatter(OutputFormatter):
    """Format output as plain text."""
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """Format results as text."""
        lines = []
        for key, value in results.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                lines.append(self.format_list(value))
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        return "\\n".join(lines)


# Convenience function
def get_formatter(format_type: str = 'text', verbose: bool = False) -> OutputFormatter:
    """Get a formatter instance by type."""
    formatters = {
        'text': TextFormatter,
        'json': JSONFormatter,
    }
    formatter_class = formatters.get(format_type.lower(), TextFormatter)
    return formatter_class(verbose=verbose)
'''

    formatters_file.write_text(content)
    return True


def update_output_init(output_dir: Path) -> bool:
    """Update output/__init__.py to export formatters."""
    init_file = output_dir / '__init__.py'

    try:
        if init_file.exists():
            content = init_file.read_text()
        else:
            content = '"""Output module."""\n'

        # Check if formatters is already imported
        if 'formatters' in content:
            return False

        # Add import
        new_content = content.rstrip() + '\n\nfrom .formatters import OutputFormatter, JSONFormatter, TextFormatter, get_formatter\n'
        init_file.write_text(new_content)
        return True

    except Exception as e:
        print(f"  [ERROR] {init_file}: {e}")
        return False


def create_manifest_generator(output_dir: Path) -> bool:
    """Create ManifestGenerator in output module."""
    # Check if it exists in the init file
    init_file = output_dir / '__init__.py'

    # Create manifest.py if it doesn't exist
    manifest_file = output_dir / 'manifest.py'

    if not manifest_file.exists():
        content = '''"""
Manifest generator for tracking exfiltrated data.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import hashlib


class ManifestGenerator:
    """Generates manifests for data exfiltration tracking."""
    
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
    
    def add_entry(self, filepath: str, size: int, checksum: str, 
                  metadata: Optional[Dict] = None) -> None:
        """Add a file entry to the manifest."""
        entry = {
            'filepath': filepath,
            'size': size,
            'checksum': checksum,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.entries.append(entry)
    
    def generate(self) -> Dict[str, Any]:
        """Generate the complete manifest."""
        return {
            'manifest_version': '1.0',
            'created_at': self.created_at.isoformat(),
            'total_files': len(self.entries),
            'total_size': sum(e['size'] for e in self.entries),
            'entries': self.entries
        }
    
    def to_json(self) -> str:
        """Export manifest as JSON."""
        return json.dumps(self.generate(), indent=2)
    
    def save(self, filepath: str) -> None:
        """Save manifest to file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @staticmethod
    def calculate_checksum(filepath: str) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
'''
        manifest_file.write_text(content)

    # Update __init__.py to export ManifestGenerator
    try:
        if init_file.exists():
            content = init_file.read_text()
        else:
            content = '"""Output module."""\n'

        if 'ManifestGenerator' not in content:
            content = content.rstrip() + '\nfrom .manifest import ManifestGenerator\n'
            init_file.write_text(content)
            return True
    except Exception as e:
        print(f"  [ERROR] {init_file}: {e}")

    return False


def fix_payload_import(repo_root: Path) -> int:
    """Fix the payload.payload import issue in registry_persistence."""
    fixes = 0

    # The issue: from rt_registry_persistence.payload.payload import ...
    # Should be: from ..payload.generator import ... (or similar)

    package_path = repo_root / '05-persistence/windows_persistence_tools/rt_registry_persistence'

    if not package_path.exists():
        return 0

    for pyfile in package_path.rglob('*.py'):
        if '__pycache__' in str(pyfile):
            continue

        try:
            content = pyfile.read_text()
            original = content

            # Fix various payload import patterns
            patterns = [
                # from rt_X.payload.payload import -> from ..payload.generator import
                (r'from rt_registry_persistence\.payload\.payload import', 'from ..payload.generator import'),
                (r'from \.payload\.payload import', 'from ..payload.generator import'),
                (r'from payload\.payload import', 'from ..payload.generator import'),
                # If in a subdir, might need different path
                (r'from \.\.payload\.payload import', 'from ..payload.generator import'),
            ]

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original:
                pyfile.write_text(content)
                print(f"  [FIXED] {pyfile.relative_to(repo_root)}")
                fixes += 1

        except Exception as e:
            print(f"  [ERROR] {pyfile}: {e}")

    return fixes


def fix_windows_paths(repo_root: Path) -> int:
    """Fix Windows path escaping in chrome.py and edge.py."""
    fixes = 0

    # Find the specific files
    target_files = [
        '09-credential-harvesting/rt_dpapi_decryptor_framework/rt_dpapi_decryptor/decryptors/chrome.py',
        '09-credential-harvesting/rt_dpapi_decryptor_framework/rt_dpapi_decryptor/decryptors/edge.py',
    ]

    for rel_path in target_files:
        filepath = repo_root / rel_path
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text()
            original = content

            # Find and fix Windows paths
            # Common patterns in these files:
            # f"...{user}\AppData\Local\Google\Chrome..."
            # "C:\Users\..."

            lines = content.split('\n')
            new_lines = []

            for line in lines:
                # Skip comments
                if line.strip().startswith('#'):
                    new_lines.append(line)
                    continue

                # Check for Windows paths
                if ('\\AppData\\' in line or '\\Users\\' in line or
                    '\\Local\\' in line or '\\Google\\' in line or
                    '\\Microsoft\\' in line or '\\Chrome\\' in line or
                    '\\Edge\\' in line or '\\Roaming\\' in line):

                    # Fix f-strings: f"..." -> rf"..." or fr"..."
                    if re.search(r'(?<!r)f"[^"]*\\', line):
                        line = re.sub(r'(?<!r)(f")', r'r\1', line)
                    if re.search(r"(?<!r)f'[^']*\\", line):
                        line = re.sub(r"(?<!r)(f')", r"r\1", line)

                    # Fix regular strings: "..." -> r"..."
                    if re.search(r'(?<![rf])"[^"]*\\[^"]*"', line):
                        line = re.sub(r'(?<![rf])("[^"]*\\[^"]*")', r'r\1', line)
                    if re.search(r"(?<![rf])'[^']*\\[^']*'", line):
                        line = re.sub(r"(?<![rf])('[^']*\\[^']*')", r"r\1", line)

                new_lines.append(line)

            new_content = '\n'.join(new_lines)

            if new_content != original:
                filepath.write_text(new_content)
                print(f"  [FIXED] {rel_path}")
                fixes += 1

        except Exception as e:
            print(f"  [ERROR] {filepath}: {e}")

    return fixes


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_final_issues.py /path/to/repository")
        sys.exit(1)

    repo_path = Path(sys.argv[1]).resolve()

    print("""
================================================================================
   30 DAYS OF RED TEAM - FINAL IMPORT FIXES
================================================================================
""")
    print(f"   Repository: {repo_path}\n")

    total_fixes = 0

    # Fix 1: Create missing formatters.py modules
    print("[*] Phase 1: Creating missing output/formatters.py modules...\n")

    output_dirs = [
        '05-persistence/rt_credential_harvester/output',
        '05-persistence/rt_network_discovery/output',
        '05-persistence/rt_situational_awareness/output',
        '05-persistence/rt_data_exfiltrator/output',
    ]

    for rel_dir in output_dirs:
        output_dir = repo_path / rel_dir
        if output_dir.exists():
            if create_formatters_module(output_dir):
                print(f"  [CREATED] {rel_dir}/formatters.py")
                total_fixes += 1
            if update_output_init(output_dir):
                print(f"  [UPDATED] {rel_dir}/__init__.py")
                total_fixes += 1

    # Fix 2: Create ManifestGenerator
    print("\n[*] Phase 2: Creating ManifestGenerator in data_exfiltrator...\n")

    data_exfil_output = repo_path / '05-persistence/rt_data_exfiltrator/output'
    if data_exfil_output.exists():
        if create_manifest_generator(data_exfil_output):
            print(f"  [CREATED] ManifestGenerator")
            total_fixes += 1

    # Fix 3: Fix payload.payload import
    print("\n[*] Phase 3: Fixing payload import in registry_persistence...\n")

    fixes = fix_payload_import(repo_path)
    total_fixes += fixes

    # Fix 4: Fix Windows paths in chrome.py/edge.py
    print("\n[*] Phase 4: Fixing Windows path escaping in DPAPI decryptors...\n")

    fixes = fix_windows_paths(repo_path)
    total_fixes += fixes

    print(f"""
================================================================================
   FIXES COMPLETE
================================================================================

   Total fixes applied: {total_fixes}

   EXPECTED FAILURES (Windows-only modules - OK on Linux):
   - registry_miner (uses winreg)
   - win_privesc (Windows-specific)

   Run test_imports.py again to verify.

================================================================================
""")


if __name__ == '__main__':
    main()
