#!/usr/bin/env python3
"""
================================================================================
30 Days of Red Team - Repository Import Fixer
================================================================================

This script fixes the import collision issues across the entire monorepo by:
1. Renaming package directories to use 'rt_' prefix
2. Updating all import statements in Python files
3. Updating all references in README files
4. Updating setup.py and pyproject.toml files
5. Creating proper __init__.py files where missing
6. Generating a migration report

Usage:
    python refactor_repository.py /path/to/30-days-of-red-team

    # Dry run (preview changes without applying):
    python refactor_repository.py /path/to/30-days-of-red-team --dry-run

    # Verbose output:
    python refactor_repository.py /path/to/30-days-of-red-team --verbose

Author: 30 Days of Red Team Series
================================================================================
"""

import os
import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field

# =============================================================================
# CONFIGURATION - All packages that need renaming
# =============================================================================

RENAME_MAP: Dict[str, str] = {
    # 01-reconnaissance
    'rt_tech_fingerprinter': 'rt_tech_fingerprinter',

    # 02-weaponization
    'rt_advanced_obfuscator': 'rt_advanced_obfuscator',
    'rt_macro_generator': 'rt_macro_generator',
    'rt_payload_generator': 'rt_payload_generator',
    'rt_shellcode_encoder': 'rt_shellcode_encoder',

    # 03-delivery
    'rt_attachment_weaponizer': 'rt_attachment_weaponizer',
    'rt_domain_reputation': 'rt_domain_reputation',
    'rt_phishing_framework': 'rt_phishing_framework',
    'rt_template_generator': 'rt_template_generator',

    # 04-exploitation
    'rt_reverse_shell_handler': 'rt_reverse_shell_handler',
    'rt_service_exploiter': 'rt_service_exploiter',
    'rt_vulnerability_scanner': 'rt_vulnerability_scanner',
    'rt_webshell_uploader': 'rt_webshell_uploader',

    # 05-persistence
    'rt_credential_harvester': 'rt_credential_harvester',
    'rt_data_exfiltrator': 'rt_data_exfiltrator',
    'rt_linux_persistence_tools': 'rt_linux_persistence_tools',
    'rt_network_discovery': 'rt_network_discovery',
    'rt_shell_stabilizer': 'rt_shell_stabilizer',
    'rt_situational_awareness': 'rt_situational_awareness',
    'rt_windows_persistence_tools': 'rt_windows_persistence_tools',

    # Sub-packages within persistence tools
    'rt_cron_persistence': 'rt_cron_persistence',
    'rt_master_persistence': 'rt_master_persistence',
    'rt_shell_persistence': 'rt_shell_persistence',
    'rt_ssh_persistence': 'rt_ssh_persistence',
    'rt_systemd_persistence': 'rt_systemd_persistence',
    'rt_registry_persistence': 'rt_registry_persistence',
    'rt_scheduled_task_persistence': 'rt_scheduled_task_persistence',
    'rt_service_persistence': 'rt_service_persistence',
    'rt_wmi_persistence': 'rt_wmi_persistence',

    # 06-c2-infrastructure
    'rt_c2_server': 'rt_c2_server',
    'rt_c2_agent': 'rt_c2_agent',
    'rt_c2_payload_generator': 'rt_c2_payload_generator',

    # 07-data-exfiltration
    'rt_automated_collection': 'rt_automated_collection',
    'rt_bandwidth_throttling_manager': 'rt_bandwidth_throttling_manager',
    'rt_chunked_exfil': 'rt_chunked_exfil',
    'rt_cloud_exfil': 'rt_cloud_exfil',
    'rt_dns_exfil': 'rt_dns_exfil',
    'rt_encrypted_archive_builder': 'rt_encrypted_archive_builder',
    'rt_steganography': 'rt_steganography',

    # 08-opsec-anti-forensics
    'rt_linux_log_cleanup': 'rt_linux_log_cleanup',
    'rt_memory_executor': 'rt_memory_executor',
    'rt_secure_delete': 'rt_secure_delete',
    'rt_timestamp_stomper': 'rt_timestamp_stomper',
    'rt_windows_log_manipulation': 'rt_windows_log_manipulation',

    # 09-credential-harvesting
    'rt_dpapi_decryptor': 'rt_dpapi_decryptor',
    'rt_dpapi_decryptor_framework': 'rt_dpapi_decryptor_framework',
    'rt_lsass_dumper': 'rt_lsass_dumper',
    'rt_lsass_dumper_framework': 'rt_lsass_dumper_framework',
    'rt_registry_miner': 'rt_registry_miner',
    'rt_registry_miner_framework': 'rt_registry_miner_framework',
    'rt_sam_extractor': 'rt_sam_extractor',
    'rt_sam_extractor_framework': 'rt_sam_extractor_framework',

    # 10-privilege-escalation
    'rt_win_privesc': 'rt_win_privesc',

    # Week-1-Final and Week-2-Final frameworks
    'rt_cleanup_framework': 'rt_cleanup_framework',
    'rt_exfiltration_framework': 'rt_exfiltration_framework',
    'rt_initial_access_framework': 'rt_initial_access_framework',
    'rt_lab_environment_framework': 'rt_lab_environment_framework',
    'rt_lateral_movement_framework': 'rt_lateral_movement_framework',
    'rt_post_exploitation_framework': 'rt_post_exploitation_framework',

    # Internal package directories (commonly cause issues)
    'rt_initial_access': 'rt_initial_access',
    'rt_lateral_movement': 'rt_lateral_movement',
    'rt_post_exploitation': 'rt_post_exploitation',
    'rt_exfiltration': 'rt_exfiltration',
    'rt_cleanup': 'rt_cleanup',
    'rt_lab_environment': 'rt_lab_environment',
}

# Directories to skip during processing
SKIP_DIRECTORIES: Set[str] = {
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    'env',
    '.env',
    'node_modules',
    '.idea',
    '.vscode',
    'dist',
    'build',
    '*.egg-info',
}

# File extensions to process for import updates
PYTHON_EXTENSIONS: Set[str] = {'.py', '.pyw'}
DOC_EXTENSIONS: Set[str] = {'.md', '.rst', '.txt'}
CONFIG_EXTENSIONS: Set[str] = {'.toml', '.cfg', '.ini'}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Change:
    """Represents a single change made by the script."""
    change_type: str  # 'rename_dir', 'update_import', 'update_doc', 'create_init'
    file_path: str
    old_value: str
    new_value: str
    line_number: Optional[int] = None


@dataclass
class MigrationReport:
    """Tracks all changes made during migration."""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    directories_renamed: List[Change] = field(default_factory=list)
    imports_updated: List[Change] = field(default_factory=list)
    docs_updated: List[Change] = field(default_factory=list)
    inits_created: List[Change] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def total_changes(self) -> int:
        return (len(self.directories_renamed) +
                len(self.imports_updated) +
                len(self.docs_updated) +
                len(self.inits_created))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def should_skip_path(path: Path) -> bool:
    """Check if a path should be skipped."""
    parts = path.parts
    for skip in SKIP_DIRECTORIES:
        if skip.startswith('*'):
            # Wildcard pattern
            pattern = skip[1:]
            if any(part.endswith(pattern) for part in parts):
                return True
        elif skip in parts:
            return True
    return False


def is_python_package(directory: Path) -> bool:
    """Check if a directory is a Python package."""
    return (directory / '__init__.py').exists()


def find_all_packages(root: Path) -> List[Path]:
    """Find all Python packages in the repository."""
    packages = []
    for dirpath in root.rglob('*'):
        if dirpath.is_dir() and not should_skip_path(dirpath):
            if is_python_package(dirpath):
                packages.append(dirpath)
    return packages


def create_backup(root: Path) -> Path:
    """Create a backup of the repository before making changes."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = root.parent / f"{root.name}_backup_{timestamp}"

    print(f"\n[*] Creating backup at: {backup_dir}")
    shutil.copytree(root, backup_dir, ignore=shutil.ignore_patterns(
        '.git', '__pycache__', '*.pyc', '.venv', 'venv', 'node_modules'
    ))

    return backup_dir


# =============================================================================
# CORE REFACTORING FUNCTIONS
# =============================================================================

def build_import_patterns() -> List[Tuple[re.Pattern, str]]:
    """Build regex patterns for all import statement variations."""
    patterns = []

    for old_name, new_name in RENAME_MAP.items():
        # Escape special regex characters in names
        old_escaped = re.escape(old_name)

        # Different import patterns to match
        pattern_templates = [
            # from package.module import something
            (rf'(from\s+){old_escaped}(\.)', rf'\1{new_name}\2'),

            # from package import something
            (rf'(from\s+){old_escaped}(\s+import)', rf'\1{new_name}\2'),

            # import package.module
            (rf'(import\s+){old_escaped}(\.)', rf'\1{new_name}\2'),

            # import package (standalone)
            (rf'(import\s+){old_escaped}(\s*$)', rf'\1{new_name}\2'),
            (rf'(import\s+){old_escaped}(\s*#)', rf'\1{new_name}\2'),
            (rf'(import\s+){old_escaped}(\s+as\s+)', rf'\1{new_name}\2'),

            # String references (for dynamic imports, entry points)
            (rf"(['\"]){old_escaped}(\.)", rf'\1{new_name}\2'),
            (rf"(['\"]){old_escaped}(['\"])", rf'\1{new_name}\2'),
        ]

        for pattern, replacement in pattern_templates:
            patterns.append((re.compile(pattern, re.MULTILINE), replacement))

    return patterns


def update_python_file(filepath: Path, patterns: List[Tuple[re.Pattern, str]],
                       report: MigrationReport, dry_run: bool = False) -> int:
    """Update import statements in a Python file."""
    changes = 0

    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content

        for pattern, replacement in patterns:
            new_content, count = pattern.subn(replacement, content)
            if count > 0:
                # Record each change
                for match in pattern.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    report.imports_updated.append(Change(
                        change_type='update_import',
                        file_path=str(filepath),
                        old_value=match.group(0),
                        new_value=pattern.sub(replacement, match.group(0)),
                        line_number=line_num
                    ))
                content = new_content
                changes += count

        if content != original_content and not dry_run:
            filepath.write_text(content, encoding='utf-8')

    except UnicodeDecodeError:
        report.warnings.append(f"Could not read file (encoding issue): {filepath}")
    except Exception as e:
        report.errors.append(f"Error processing {filepath}: {str(e)}")

    return changes


def update_documentation_file(filepath: Path, report: MigrationReport,
                              dry_run: bool = False) -> int:
    """Update package references in documentation files."""
    changes = 0

    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content

        for old_name, new_name in RENAME_MAP.items():
            # Match package names in various doc contexts
            patterns = [
                # Code blocks and inline code
                (rf'`{re.escape(old_name)}`', f'`{new_name}`'),
                (rf'`{re.escape(old_name)}\.', f'`{new_name}.'),

                # Directory references
                (rf'{re.escape(old_name)}/', f'{new_name}/'),

                # Import examples in docs
                (rf'from {re.escape(old_name)}', f'from {new_name}'),
                (rf'import {re.escape(old_name)}', f'import {new_name}'),

                # pip install references
                (rf'pip install {re.escape(old_name)}', f'pip install {new_name}'),
                (rf'pip install -e {re.escape(old_name)}', f'pip install -e {new_name}'),
            ]

            for pattern, replacement in patterns:
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    changes += count
                    report.docs_updated.append(Change(
                        change_type='update_doc',
                        file_path=str(filepath),
                        old_value=old_name,
                        new_value=new_name
                    ))

        if content != original_content and not dry_run:
            filepath.write_text(content, encoding='utf-8')

    except Exception as e:
        report.errors.append(f"Error processing doc {filepath}: {str(e)}")

    return changes


def update_setup_files(filepath: Path, report: MigrationReport,
                       dry_run: bool = False) -> int:
    """Update setup.py and pyproject.toml files."""
    changes = 0

    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content

        for old_name, new_name in RENAME_MAP.items():
            # setup.py patterns
            patterns = [
                # name='package_name'
                (rf"(name\s*=\s*['\"]){re.escape(old_name)}(['\"])",
                 rf'\1{new_name}\2'),

                # packages=['package_name']
                (rf"(['\"]){re.escape(old_name)}(['\"])",
                 rf'\1{new_name}\2'),

                # entry_points references
                (rf'{re.escape(old_name)}\.', f'{new_name}.'),
                (rf'{re.escape(old_name)}:', f'{new_name}:'),
            ]

            for pattern, replacement in patterns:
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    changes += count

        if content != original_content and not dry_run:
            filepath.write_text(content, encoding='utf-8')

    except Exception as e:
        report.errors.append(f"Error processing setup file {filepath}: {str(e)}")

    return changes


def rename_package_directories(root: Path, report: MigrationReport,
                               dry_run: bool = False, verbose: bool = False) -> int:
    """Rename package directories according to RENAME_MAP."""
    renamed = 0

    # Build list of directories to rename (deepest first to avoid path issues)
    dirs_to_rename: List[Tuple[Path, Path]] = []

    for dirpath in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if not dirpath.is_dir() or should_skip_path(dirpath):
            continue

        dir_name = dirpath.name
        if dir_name in RENAME_MAP:
            new_name = RENAME_MAP[dir_name]
            new_path = dirpath.parent / new_name

            # Only rename if it's a Python package or contains Python files
            if is_python_package(dirpath) or any(dirpath.glob('*.py')):
                dirs_to_rename.append((dirpath, new_path))

    # Perform renames
    for old_path, new_path in dirs_to_rename:
        if new_path.exists():
            report.warnings.append(
                f"Cannot rename {old_path} -> {new_path}: destination exists"
            )
            continue

        if verbose:
            print(f"  [RENAME] {old_path.name} -> {new_path.name}")

        report.directories_renamed.append(Change(
            change_type='rename_dir',
            file_path=str(old_path.parent),
            old_value=old_path.name,
            new_value=new_path.name
        ))

        if not dry_run:
            try:
                old_path.rename(new_path)
                renamed += 1
            except Exception as e:
                report.errors.append(f"Failed to rename {old_path}: {str(e)}")

    return renamed


def ensure_init_files(root: Path, report: MigrationReport,
                      dry_run: bool = False) -> int:
    """Ensure all package directories have __init__.py files."""
    created = 0

    for dirpath in root.rglob('*'):
        if not dirpath.is_dir() or should_skip_path(dirpath):
            continue

        # Check if directory contains Python files but no __init__.py
        has_python = any(dirpath.glob('*.py'))
        has_init = (dirpath / '__init__.py').exists()

        if has_python and not has_init:
            init_path = dirpath / '__init__.py'

            # Generate appropriate __init__.py content
            package_name = dirpath.name
            init_content = f'''"""
{package_name} - Part of 30 Days of Red Team Toolkit
"""

__version__ = "1.0.0"
'''

            report.inits_created.append(Change(
                change_type='create_init',
                file_path=str(init_path),
                old_value='',
                new_value='__init__.py'
            ))

            if not dry_run:
                init_path.write_text(init_content)
                created += 1

    return created


def update_relative_imports(root: Path, report: MigrationReport,
                            dry_run: bool = False) -> int:
    """
    Convert absolute imports within packages to relative imports
    where appropriate for better package isolation.
    """
    changes = 0

    # Find all packages and their modules
    for package_dir in root.rglob('*'):
        if not package_dir.is_dir() or should_skip_path(package_dir):
            continue

        if not is_python_package(package_dir):
            continue

        package_name = package_dir.name
        if not package_name.startswith('rt_'):
            continue

        # Process Python files within this package
        for pyfile in package_dir.rglob('*.py'):
            if pyfile.name == '__init__.py':
                continue

            try:
                content = pyfile.read_text(encoding='utf-8')
                original = content

                # Calculate relative path depth
                rel_path = pyfile.relative_to(package_dir)
                depth = len(rel_path.parts) - 1  # -1 for the file itself

                if depth > 0:
                    # Replace absolute package imports with relative
                    # from rt_package.submodule import X -> from ..submodule import X
                    dots = '.' * (depth + 1)

                    # Pattern: from rt_package_name.something import
                    pattern = rf'from\s+{re.escape(package_name)}\.(\S+)\s+import'
                    replacement = rf'from {dots}\1 import'

                    content, count = re.subn(pattern, replacement, content)
                    if count > 0:
                        changes += count

                if content != original and not dry_run:
                    pyfile.write_text(content, encoding='utf-8')

            except Exception as e:
                report.warnings.append(f"Could not process relative imports in {pyfile}: {e}")

    return changes


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_report(report: MigrationReport, output_path: Path) -> None:
    """Generate a detailed migration report."""
    report.end_time = datetime.now()
    duration = report.end_time - report.start_time

    report_content = f"""
================================================================================
30 DAYS OF RED TEAM - IMPORT MIGRATION REPORT
================================================================================

Migration Start:  {report.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Migration End:    {report.end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration:         {duration.total_seconds():.2f} seconds

================================================================================
SUMMARY
================================================================================

Total Changes:           {report.total_changes()}
Directories Renamed:     {len(report.directories_renamed)}
Import Statements Fixed: {len(report.imports_updated)}
Documentation Updated:   {len(report.docs_updated)}
__init__.py Created:     {len(report.inits_created)}
Errors:                  {len(report.errors)}
Warnings:                {len(report.warnings)}

================================================================================
DIRECTORIES RENAMED
================================================================================
"""

    for change in report.directories_renamed:
        report_content += f"\n  {change.file_path}/\n"
        report_content += f"    {change.old_value} -> {change.new_value}\n"

    report_content += """
================================================================================
IMPORT STATEMENTS UPDATED
================================================================================
"""

    # Group by file
    files_updated: Dict[str, List[Change]] = {}
    for change in report.imports_updated:
        if change.file_path not in files_updated:
            files_updated[change.file_path] = []
        files_updated[change.file_path].append(change)

    for filepath, changes in files_updated.items():
        report_content += f"\n  {filepath} ({len(changes)} changes)\n"
        for change in changes[:5]:  # Show first 5
            report_content += f"    Line {change.line_number}: {change.old_value[:50]}...\n"
        if len(changes) > 5:
            report_content += f"    ... and {len(changes) - 5} more\n"

    if report.errors:
        report_content += """
================================================================================
ERRORS
================================================================================
"""
        for error in report.errors:
            report_content += f"\n  [ERROR] {error}\n"

    if report.warnings:
        report_content += """
================================================================================
WARNINGS
================================================================================
"""
        for warning in report.warnings:
            report_content += f"\n  [WARN] {warning}\n"

    report_content += """
================================================================================
NEXT STEPS
================================================================================

1. Review the changes in your IDE or diff tool
2. Run your test suite to verify nothing is broken
3. Check that all entry points in setup.py/pyproject.toml are correct
4. Update any external documentation or CI/CD scripts
5. Commit the changes with a descriptive message

If you encounter issues, restore from the backup created before migration.

================================================================================
"""

    output_path.write_text(report_content)
    print(f"\n[+] Report saved to: {output_path}")


def generate_json_report(report: MigrationReport, output_path: Path) -> None:
    """Generate a JSON report for programmatic processing."""
    data = {
        'start_time': report.start_time.isoformat(),
        'end_time': report.end_time.isoformat() if report.end_time else None,
        'summary': {
            'total_changes': report.total_changes(),
            'directories_renamed': len(report.directories_renamed),
            'imports_updated': len(report.imports_updated),
            'docs_updated': len(report.docs_updated),
            'inits_created': len(report.inits_created),
            'errors': len(report.errors),
            'warnings': len(report.warnings),
        },
        'directories_renamed': [
            {'path': c.file_path, 'old': c.old_value, 'new': c.new_value}
            for c in report.directories_renamed
        ],
        'imports_updated': [
            {'file': c.file_path, 'line': c.line_number, 'old': c.old_value, 'new': c.new_value}
            for c in report.imports_updated
        ],
        'errors': report.errors,
        'warnings': report.warnings,
    }

    output_path.write_text(json.dumps(data, indent=2))


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Fix import collisions in 30 Days of Red Team repository',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo                    # Run migration
  %(prog)s /path/to/repo --dry-run          # Preview changes
  %(prog)s /path/to/repo --no-backup        # Skip backup (dangerous!)
  %(prog)s /path/to/repo --verbose          # Show detailed progress
        """
    )

    parser.add_argument('repo_path', type=Path, help='Path to repository root')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without applying them')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip creating backup (use with caution)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed progress')
    parser.add_argument('--skip-relative', action='store_true',
                        help='Skip converting to relative imports')
    parser.add_argument('--output-dir', type=Path, default=None,
                        help='Directory for reports (default: repo root)')

    args = parser.parse_args()

    # Validate repository path
    if not args.repo_path.exists():
        print(f"[!] Error: Repository path does not exist: {args.repo_path}")
        sys.exit(1)

    repo_root = args.repo_path.resolve()
    output_dir = args.output_dir or repo_root

    print("""
================================================================================
   30 DAYS OF RED TEAM - REPOSITORY IMPORT FIXER
================================================================================
    """)

    print(f"[*] Repository: {repo_root}")
    print(f"[*] Mode: {'DRY RUN (no changes)' if args.dry_run else 'LIVE'}")
    print(f"[*] Packages to rename: {len(RENAME_MAP)}")

    # Initialize report
    report = MigrationReport()

    # Create backup unless skipped
    if not args.dry_run and not args.no_backup:
        backup_path = create_backup(repo_root)
        print(f"[+] Backup created at: {backup_path}")

    # Build import patterns once
    print("\n[*] Building import patterns...")
    import_patterns = build_import_patterns()
    print(f"[+] Generated {len(import_patterns)} import patterns")

    # Phase 1: Update imports in Python files FIRST (before renaming dirs)
    print("\n[*] Phase 1: Updating import statements in Python files...")
    python_files = list(repo_root.rglob('*.py'))
    python_files = [f for f in python_files if not should_skip_path(f)]

    total_import_changes = 0
    for i, pyfile in enumerate(python_files):
        if args.verbose:
            print(f"  Processing ({i + 1}/{len(python_files)}): {pyfile.name}")
        changes = update_python_file(pyfile, import_patterns, report, args.dry_run)
        total_import_changes += changes

    print(f"[+] Updated {total_import_changes} import statements in {len(python_files)} files")

    # Phase 2: Update setup.py and pyproject.toml files
    print("\n[*] Phase 2: Updating setup files...")
    setup_files = list(repo_root.rglob('setup.py')) + list(repo_root.rglob('pyproject.toml'))
    setup_files = [f for f in setup_files if not should_skip_path(f)]

    for setup_file in setup_files:
        if args.verbose:
            print(f"  Processing: {setup_file}")
        update_setup_files(setup_file, report, args.dry_run)

    print(f"[+] Processed {len(setup_files)} setup files")

    # Phase 3: Update documentation
    print("\n[*] Phase 3: Updating documentation files...")
    doc_files = []
    for ext in DOC_EXTENSIONS:
        doc_files.extend(repo_root.rglob(f'*{ext}'))
    doc_files = [f for f in doc_files if not should_skip_path(f)]

    for doc_file in doc_files:
        if args.verbose:
            print(f"  Processing: {doc_file.name}")
        update_documentation_file(doc_file, report, args.dry_run)

    print(f"[+] Processed {len(doc_files)} documentation files")

    # Phase 4: Rename directories (AFTER updating imports)
    print("\n[*] Phase 4: Renaming package directories...")
    renamed = rename_package_directories(repo_root, report, args.dry_run, args.verbose)
    print(f"[+] Renamed {renamed} directories")

    # Phase 5: Create missing __init__.py files
    print("\n[*] Phase 5: Creating missing __init__.py files...")
    inits_created = ensure_init_files(repo_root, report, args.dry_run)
    print(f"[+] Created {inits_created} __init__.py files")

    # Phase 6: Convert to relative imports (optional)
    if not args.skip_relative:
        print("\n[*] Phase 6: Optimizing relative imports...")
        relative_changes = update_relative_imports(repo_root, report, args.dry_run)
        print(f"[+] Converted {relative_changes} imports to relative")

    # Generate reports
    print("\n[*] Generating migration report...")
    report_path = output_dir / 'migration_report.txt'
    json_report_path = output_dir / 'migration_report.json'

    generate_report(report, report_path)
    generate_json_report(report, json_report_path)

    # Summary
    print(f"""
================================================================================
   MIGRATION {'PREVIEW' if args.dry_run else 'COMPLETE'}
================================================================================

   Total Changes:           {report.total_changes()}
   Directories Renamed:     {len(report.directories_renamed)}
   Import Statements Fixed: {len(report.imports_updated)}
   Documentation Updated:   {len(report.docs_updated)}
   __init__.py Created:     {len(report.inits_created)}

   Errors:                  {len(report.errors)}
   Warnings:                {len(report.warnings)}

   Reports saved to:
     - {report_path}
     - {json_report_path}
""")

    if args.dry_run:
        print("   [!] This was a DRY RUN. No changes were made.")
        print("   [!] Run without --dry-run to apply changes.\n")

    if report.errors:
        print("   [!] Some errors occurred. Check the report for details.\n")
        sys.exit(1)

    print("================================================================================\n")


if __name__ == '__main__':
    main()