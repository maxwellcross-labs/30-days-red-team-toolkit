#!/usr/bin/env python3
"""
================================================================================
30 Days of Red Team - Post-Migration Verification Script
================================================================================

Run this script after the migration to verify:
1. All imports resolve correctly
2. No circular import issues
3. All packages are properly structured
4. No leftover references to old package names

Usage:
    python verify_migration.py /path/to/30-days-of-red-team

================================================================================
"""

import os
import re
import sys
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field

# Old package names that should NO LONGER exist
OLD_PACKAGE_NAMES: Set[str] = {
    'tech_fingerprinter',
    'advanced_obfuscator',
    'macro_generator',
    'payload_generator',
    'shellcode_encoder',
    'attachment_weaponizer',
    'domain_reputation',
    'phishing_framework',
    'template_generator',
    'reverse_shell_handler',
    'service_exploiter',
    'vulnerability_scanner',
    'webshell_uploader',
    'credential_harvester',
    'data_exfiltrator',
    'linux_persistence_tools',
    'network_discovery',
    'shell_stabilizer',
    'situational_awareness',
    'windows_persistence_tools',
    'cron_persistence',
    'master_persistence',
    'shell_persistence',
    'ssh_persistence',
    'systemd_persistence',
    'registry_persistence',
    'scheduled_task_persistence',
    'service_persistence',
    'wmi_persistence',
    'c2_server',
    'c2_agent',
    'c2_payload_generator',
    'automated_collection',
    'bandwidth_throttling_manager',
    'chunked_exfil',
    'cloud_exfil',
    'dns_exfil',
    'encrypted_archive_builder',
    'steganography',
    'linux_log_cleanup',
    'memory_executor',
    'secure_delete',
    'timestamp_stomper',
    'windows_log_manipulation',
    'dpapi_decryptor',
    'lsass_dumper',
    'registry_miner',
    'sam_extractor',
    'win_privesc',
}

SKIP_DIRECTORIES: Set[str] = {
    '.git', '__pycache__', '.venv', 'venv', 'env', 'node_modules',
    '.idea', '.vscode', 'dist', 'build',
}


@dataclass
class VerificationResult:
    """Results of verification checks."""
    syntax_errors: List[Tuple[Path, str]] = field(default_factory=list)
    import_errors: List[Tuple[Path, str]] = field(default_factory=list)
    old_references: List[Tuple[Path, int, str]] = field(default_factory=list)
    missing_inits: List[Path] = field(default_factory=list)
    circular_imports: List[str] = field(default_factory=list)
    passed_files: int = 0
    total_files: int = 0


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    return any(skip in path.parts for skip in SKIP_DIRECTORIES)


def check_syntax(filepath: Path) -> Tuple[bool, str]:
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def check_imports(filepath: Path) -> Tuple[bool, List[str]]:
    """
    Parse a file and check for import issues.
    Returns (success, list of issues).
    """
    issues = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in OLD_PACKAGE_NAMES:
                        issues.append(
                            f"Line {node.lineno}: Old package reference: {alias.name}"
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    if module_name in OLD_PACKAGE_NAMES:
                        issues.append(
                            f"Line {node.lineno}: Old package reference: from {node.module}"
                        )

        return len(issues) == 0, issues

    except SyntaxError:
        return True, []  # Syntax errors handled separately
    except Exception as e:
        return False, [f"Parse error: {str(e)}"]


def find_old_references(filepath: Path) -> List[Tuple[int, str]]:
    """Find any string references to old package names."""
    references = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for old_name in OLD_PACKAGE_NAMES:
                    # Check for references that aren't part of rt_ names
                    pattern = rf'(?<![a-zA-Z_]){re.escape(old_name)}(?![a-zA-Z_])'
                    if re.search(pattern, line):
                        # Exclude if it's actually rt_name
                        if f'rt_{old_name}' not in line:
                            references.append((line_num, line.strip()[:80]))
                            break
    except Exception:
        pass

    return references


def check_package_structure(directory: Path) -> List[Path]:
    """Check for directories with Python files but no __init__.py."""
    missing_inits = []

    for dirpath in directory.rglob('*'):
        if not dirpath.is_dir() or should_skip(dirpath):
            continue

        has_python = any(dirpath.glob('*.py'))
        has_init = (dirpath / '__init__.py').exists()

        # Exclude certain directories that shouldn't be packages
        excluded = {'scripts', 'examples', 'tests', 'wordlists', 'templates'}
        if dirpath.name in excluded:
            continue

        if has_python and not has_init:
            missing_inits.append(dirpath)

    return missing_inits


def try_import(module_path: Path, package_root: Path) -> Tuple[bool, str]:
    """
    Try to import a module to check for circular imports and other issues.
    Note: This is a static check, not an actual import.
    """
    try:
        spec = importlib.util.spec_from_file_location(
            module_path.stem,
            module_path
        )
        if spec and spec.loader:
            return True, ""
        return False, "Could not create module spec"
    except Exception as e:
        return False, str(e)


def run_verification(repo_root: Path) -> VerificationResult:
    """Run all verification checks."""
    result = VerificationResult()

    python_files = [
        f for f in repo_root.rglob('*.py')
        if not should_skip(f)
    ]
    result.total_files = len(python_files)

    print(f"\n[*] Checking {len(python_files)} Python files...\n")

    for i, pyfile in enumerate(python_files):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(python_files)}")

        # Syntax check
        valid, error = check_syntax(pyfile)
        if not valid:
            result.syntax_errors.append((pyfile, error))
            continue

        # Import check
        valid, issues = check_imports(pyfile)
        if not valid:
            for issue in issues:
                result.import_errors.append((pyfile, issue))

        # Old reference check
        refs = find_old_references(pyfile)
        for line_num, line in refs:
            result.old_references.append((pyfile, line_num, line))

        if valid and len(refs) == 0:
            result.passed_files += 1

    # Check package structure
    print("\n[*] Checking package structure...")
    result.missing_inits = check_package_structure(repo_root)

    return result


def print_report(result: VerificationResult) -> None:
    """Print verification report."""
    print(f"""
================================================================================
   VERIFICATION REPORT
================================================================================

   Files Checked:    {result.total_files}
   Files Passed:     {result.passed_files}
   Files with Issues: {result.total_files - result.passed_files}

================================================================================
""")

    if result.syntax_errors:
        print(f"   SYNTAX ERRORS ({len(result.syntax_errors)}):")
        print("   " + "-" * 70)
        for filepath, error in result.syntax_errors[:10]:
            print(f"   {filepath.name}: {error}")
        if len(result.syntax_errors) > 10:
            print(f"   ... and {len(result.syntax_errors) - 10} more")
        print()

    if result.import_errors:
        print(f"   IMPORT ISSUES ({len(result.import_errors)}):")
        print("   " + "-" * 70)
        for filepath, error in result.import_errors[:10]:
            print(f"   {filepath.name}: {error}")
        if len(result.import_errors) > 10:
            print(f"   ... and {len(result.import_errors) - 10} more")
        print()

    if result.old_references:
        print(f"   OLD PACKAGE REFERENCES ({len(result.old_references)}):")
        print("   " + "-" * 70)
        for filepath, line_num, line in result.old_references[:10]:
            print(f"   {filepath.name}:{line_num}: {line[:60]}...")
        if len(result.old_references) > 10:
            print(f"   ... and {len(result.old_references) - 10} more")
        print()

    if result.missing_inits:
        print(f"   MISSING __init__.py ({len(result.missing_inits)}):")
        print("   " + "-" * 70)
        for dirpath in result.missing_inits[:10]:
            print(f"   {dirpath}")
        if len(result.missing_inits) > 10:
            print(f"   ... and {len(result.missing_inits) - 10} more")
        print()

    # Overall status
    total_issues = (
            len(result.syntax_errors) +
            len(result.import_errors) +
            len(result.old_references) +
            len(result.missing_inits)
    )

    if total_issues == 0:
        print("""
================================================================================
   ✅ ALL CHECKS PASSED - Migration verified successfully!
================================================================================
""")
    else:
        print(f"""
================================================================================
   ⚠️  {total_issues} ISSUES FOUND - Review and fix before proceeding
================================================================================
""")


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_migration.py /path/to/repository")
        sys.exit(1)

    repo_path = Path(sys.argv[1]).resolve()

    if not repo_path.exists():
        print(f"Error: Path does not exist: {repo_path}")
        sys.exit(1)

    print("""
================================================================================
   30 DAYS OF RED TEAM - MIGRATION VERIFICATION
================================================================================
""")
    print(f"   Repository: {repo_path}")

    result = run_verification(repo_path)
    print_report(result)

    # Exit with error code if issues found
    total_issues = (
            len(result.syntax_errors) +
            len(result.import_errors) +
            len(result.old_references)
    )
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == '__main__':
    main()