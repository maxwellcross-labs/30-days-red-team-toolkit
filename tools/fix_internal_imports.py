#!/usr/bin/env python3
"""
================================================================================
30 Days of Red Team - Fix Internal Package Imports
================================================================================

This script converts absolute imports within packages to relative imports.

Problem:
    from core.database import Database  # Fails - 'core' not in sys.path

Solution:
    from .database import Database      # Works - relative to current package

This is needed because after renaming packages to rt_*, the internal
imports that assumed the package was at sys.path root no longer work.

Usage:
    python fix_internal_imports.py /path/to/30-days-red-team-toolkit

================================================================================
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

# Common internal module names that should use relative imports
INTERNAL_MODULES = {
    'core',
    'utils',
    'config',
    'helpers',
    'database',
    'handlers',
    'modules',
    'methods',
    'templates',
    'generators',
    'scanners',
    'exploits',
    'checks',
    'bypass',
    'shells',
    'payloads',
    'reporting',
    'interactive',
    'tracking',
    'web',
    'evasion',
    'analyzers',
    'platforms',
    'cleaners',
    'techniques',
    'detection',
    'output',
    'management',
    'persistence',
    'keygen',
    'triggers',
    'archiving',
    'encryption',
    'obfuscation',
    'preparation',
    'discovery',
    'enumeration',
    'harvesters',
    'miners',
    'decryptors',
    'parsers',
    'loaders',
    'encoders',
    'queue',
    'throttling',
    'deployers',
    'challenges',
    'labs',
    'phases',
    'ctf',
}

SKIP_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', 'tools', 'examples', 'tests', 'scripts'}


@dataclass
class PackageInfo:
    """Information about a Python package."""
    root: Path
    name: str
    modules: Set[str]  # Submodule/subpackage names


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    return any(skip in path.parts for skip in SKIP_DIRS)


def find_packages(repo_root: Path) -> List[PackageInfo]:
    """Find all Python packages and their internal structure."""
    packages = []

    # Look for rt_* directories that are packages
    for dirpath in repo_root.rglob('rt_*'):
        if not dirpath.is_dir() or should_skip(dirpath):
            continue

        # Check if it's a Python package
        if not (dirpath / '__init__.py').exists():
            continue

        # Get all submodules/subpackages
        modules = set()
        for item in dirpath.iterdir():
            if item.is_dir() and (item / '__init__.py').exists():
                modules.add(item.name)
            elif item.is_file() and item.suffix == '.py' and item.name != '__init__.py':
                modules.add(item.stem)

        packages.append(PackageInfo(
            root=dirpath,
            name=dirpath.name,
            modules=modules
        ))

    return packages


def get_relative_depth(file_path: Path, package_root: Path) -> int:
    """
    Calculate how many levels deep a file is within a package.
    Returns the number of dots needed for relative imports to package root.
    """
    try:
        rel_path = file_path.relative_to(package_root)
        # Count directory levels (subtract 1 for the file itself)
        return len(rel_path.parts) - 1
    except ValueError:
        return 0


def convert_to_relative_import(
        line: str,
        file_path: Path,
        package: PackageInfo
) -> Tuple[str, bool]:
    """
    Convert an absolute import to a relative import if applicable.
    Returns (new_line, was_changed).
    """
    original = line

    # Calculate depth for relative imports
    depth = get_relative_depth(file_path, package.root)

    # Determine the correct number of dots
    # Files directly in package root use single dot
    # Files in subdirectories need more dots to go up

    # Get the directory this file is in (relative to package root)
    try:
        rel_path = file_path.relative_to(package.root)
        current_subpackage = rel_path.parts[0] if len(rel_path.parts) > 1 else None
    except ValueError:
        current_subpackage = None

    # Check for imports that should be relative
    for module in INTERNAL_MODULES:
        # Pattern: from module.submodule import X
        pattern = rf'^(\s*from\s+){module}(\.?\S*)\s+(import\s+.+)$'
        match = re.match(pattern, line)

        if match:
            indent = match.group(1)
            rest_of_module = match.group(2)  # .submodule or empty
            import_part = match.group(3)

            # Check if this module exists in the package
            if module in package.modules or module == current_subpackage:
                # Determine correct relative prefix
                if current_subpackage and current_subpackage == module:
                    # Same subpackage - use single dot
                    dots = '.'
                elif current_subpackage:
                    # Different subpackage - go up one level
                    dots = '..'
                else:
                    # In package root
                    dots = '.'

                new_line = f"{indent}{dots}{module}{rest_of_module} {import_part}"
                return new_line, True

        # Pattern: import module.submodule
        pattern = rf'^(\s*import\s+){module}(\.?\S*)(\s*)$'
        match = re.match(pattern, line)

        if match:
            indent = match.group(1)
            rest = match.group(2)
            trailing = match.group(3)

            if module in package.modules:
                # Convert to from . import style
                if rest:
                    # import core.database -> from .core import database
                    parts = rest.lstrip('.').split('.')
                    if parts:
                        new_line = f"{indent.replace('import', 'from .')}{module} import {parts[0]}{trailing}"
                        return new_line, True

    return original, False


def fix_file_imports(file_path: Path, package: PackageInfo) -> int:
    """Fix imports in a single file. Returns number of changes."""
    changes = 0

    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            new_line, changed = convert_to_relative_import(line, file_path, package)
            new_lines.append(new_line)
            if changed:
                changes += 1

        if changes > 0:
            new_content = '\n'.join(new_lines)
            file_path.write_text(new_content, encoding='utf-8')

        return changes

    except Exception as e:
        print(f"  [ERROR] {file_path}: {e}")
        return 0


def fix_package_imports(package: PackageInfo) -> int:
    """Fix all imports within a package."""
    total_changes = 0

    for pyfile in package.root.rglob('*.py'):
        if should_skip(pyfile):
            continue

        changes = fix_file_imports(pyfile, package)
        if changes > 0:
            print(f"  [FIXED] {pyfile.relative_to(package.root)} ({changes} imports)")
            total_changes += changes

    return total_changes


def fix_specific_patterns(repo_root: Path) -> int:
    """
    Fix specific import patterns that are common across the codebase.
    This handles the most common cases directly.
    """
    changes = 0

    # Common patterns to fix: from X import Y where X is a sibling module
    sibling_patterns = [
        # from core.X import Y -> from .X import Y (when in core/)
        # from core.X import Y -> from .core.X import Y (when in package root)
        (r'^(\s*)from core\.(\w+) import (.+)$', r'\1from .core.\2 import \3'),
        (r'^(\s*)from utils\.(\w+) import (.+)$', r'\1from .utils.\2 import \3'),
        (r'^(\s*)from config import (.+)$', r'\1from .config import \2'),
        (r'^(\s*)from database import (.+)$', r'\1from .database import \2'),
        (r'^(\s*)from handlers\.(\w+) import (.+)$', r'\1from .handlers.\2 import \3'),
        (r'^(\s*)from modules\.(\w+) import (.+)$', r'\1from .modules.\2 import \3'),
        (r'^(\s*)from methods\.(\w+) import (.+)$', r'\1from .methods.\2 import \3'),
        (r'^(\s*)from generators\.(\w+) import (.+)$', r'\1from .generators.\2 import \3'),
        (r'^(\s*)from templates\.(\w+) import (.+)$', r'\1from .templates.\2 import \3'),
        (r'^(\s*)from evasion\.(\w+) import (.+)$', r'\1from .evasion.\2 import \3'),
        (r'^(\s*)from bypass\.(\w+) import (.+)$', r'\1from .bypass.\2 import \3'),
        (r'^(\s*)from shells\.(\w+) import (.+)$', r'\1from .shells.\2 import \3'),
        (r'^(\s*)from payloads\.(\w+) import (.+)$', r'\1from .payloads.\2 import \3'),
        (r'^(\s*)from scanners\.(\w+) import (.+)$', r'\1from .scanners.\2 import \3'),
        (r'^(\s*)from exploits\.(\w+) import (.+)$', r'\1from .exploits.\2 import \3'),
        (r'^(\s*)from checks\.(\w+) import (.+)$', r'\1from .checks.\2 import \3'),
        (r'^(\s*)from reporting\.(\w+) import (.+)$', r'\1from .reporting.\2 import \3'),
        (r'^(\s*)from tracking\.(\w+) import (.+)$', r'\1from .tracking.\2 import \3'),
        (r'^(\s*)from web\.(\w+) import (.+)$', r'\1from .web.\2 import \3'),
        (r'^(\s*)from detection\.(\w+) import (.+)$', r'\1from .detection.\2 import \3'),
        (r'^(\s*)from output\.(\w+) import (.+)$', r'\1from .output.\2 import \3'),
        (r'^(\s*)from persistence\.(\w+) import (.+)$', r'\1from .persistence.\2 import \3'),
        (r'^(\s*)from harvesters\.(\w+) import (.+)$', r'\1from .harvesters.\2 import \3'),
        (r'^(\s*)from decryptors\.(\w+) import (.+)$', r'\1from .decryptors.\2 import \3'),
        (r'^(\s*)from parsers\.(\w+) import (.+)$', r'\1from .parsers.\2 import \3'),
        (r'^(\s*)from loaders\.(\w+) import (.+)$', r'\1from .loaders.\2 import \3'),
        (r'^(\s*)from encoders\.(\w+) import (.+)$', r'\1from .encoders.\2 import \3'),
        (r'^(\s*)from cleaners\.(\w+) import (.+)$', r'\1from .cleaners.\2 import \3'),
        (r'^(\s*)from techniques\.(\w+) import (.+)$', r'\1from .techniques.\2 import \3'),
        (r'^(\s*)from analyzers\.(\w+) import (.+)$', r'\1from .analyzers.\2 import \3'),
        (r'^(\s*)from platforms\.(\w+) import (.+)$', r'\1from .platforms.\2 import \3'),
        (r'^(\s*)from archiving\.(\w+) import (.+)$', r'\1from .archiving.\2 import \3'),
        (r'^(\s*)from encryption\.(\w+) import (.+)$', r'\1from .encryption.\2 import \3'),
        (r'^(\s*)from obfuscation\.(\w+) import (.+)$', r'\1from .obfuscation.\2 import \3'),
        (r'^(\s*)from preparation\.(\w+) import (.+)$', r'\1from .preparation.\2 import \3'),
        (r'^(\s*)from discovery\.(\w+) import (.+)$', r'\1from .discovery.\2 import \3'),
        (r'^(\s*)from enumeration\.(\w+) import (.+)$', r'\1from .enumeration.\2 import \3'),
        (r'^(\s*)from queue\.(\w+) import (.+)$', r'\1from .queue.\2 import \3'),
        (r'^(\s*)from throttling\.(\w+) import (.+)$', r'\1from .throttling.\2 import \3'),
        (r'^(\s*)from interactive\.(\w+) import (.+)$', r'\1from .interactive.\2 import \3'),
        (r'^(\s*)from recon\.(\w+) import (.+)$', r'\1from .recon.\2 import \3'),
        (r'^(\s*)from shell\.(\w+) import (.+)$', r'\1from .shell.\2 import \3'),
        (r'^(\s*)from triggers\.(\w+) import (.+)$', r'\1from .triggers.\2 import \3'),
        (r'^(\s*)from miners\.(\w+) import (.+)$', r'\1from .miners.\2 import \3'),
        (r'^(\s*)from creators\.(\w+) import (.+)$', r'\1from .creators.\2 import \3'),
        (r'^(\s*)from checkers\.(\w+) import (.+)$', r'\1from .checkers.\2 import \3'),

        # Single module imports
        (r'^(\s*)from core import (.+)$', r'\1from .core import \2'),
        (r'^(\s*)from utils import (.+)$', r'\1from .utils import \2'),
        (r'^(\s*)from helpers import (.+)$', r'\1from .helpers import \2'),
        (r'^(\s*)from database import (.+)$', r'\1from .database import \2'),
        (r'^(\s*)from config import (.+)$', r'\1from .config import \2'),
        (r'^(\s*)from server import (.+)$', r'\1from .server import \2'),
        (r'^(\s*)from handler import (.+)$', r'\1from .handler import \2'),
        (r'^(\s*)from scanner import (.+)$', r'\1from .scanner import \2'),
        (r'^(\s*)from exploiter import (.+)$', r'\1from .exploiter import \2'),
        (r'^(\s*)from uploader import (.+)$', r'\1from .uploader import \2'),
        (r'^(\s*)from stabilizer import (.+)$', r'\1from .stabilizer import \2'),
        (r'^(\s*)from collector import (.+)$', r'\1from .collector import \2'),
        (r'^(\s*)from filter import (.+)$', r'\1from .filter import \2'),
        (r'^(\s*)from manifest import (.+)$', r'\1from .manifest import \2'),
        (r'^(\s*)from scheduler import (.+)$', r'\1from .scheduler import \2'),
        (r'^(\s*)from generator import (.+)$', r'\1from .generator import \2'),
        (r'^(\s*)from encoder import (.+)$', r'\1from .encoder import \2'),
        (r'^(\s*)from transmitter import (.+)$', r'\1from .transmitter import \2'),
        (r'^(\s*)from timing import (.+)$', r'\1from .timing import \2'),
    ]

    for pyfile in repo_root.rglob('*.py'):
        if should_skip(pyfile):
            continue

        # Only process files inside rt_* packages
        if not any(part.startswith('rt_') for part in pyfile.parts):
            continue

        try:
            content = pyfile.read_text(encoding='utf-8')
            original = content

            for pattern, replacement in sibling_patterns:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            if content != original:
                pyfile.write_text(content, encoding='utf-8')
                changes += 1
                rel_path = pyfile.relative_to(repo_root)
                print(f"  [FIXED] {rel_path}")

        except Exception as e:
            print(f"  [ERROR] {pyfile}: {e}")

    return changes


def fix_double_dot_imports(repo_root: Path) -> int:
    """
    Fix imports in nested directories that need to go up multiple levels.
    For files in package/subdir/file.py that import from package/other/
    """
    changes = 0

    # Pattern for files that are in subdirectories and import from sibling subdirectories
    # These need .. instead of .

    for pyfile in repo_root.rglob('*.py'):
        if should_skip(pyfile):
            continue

        # Only process files inside rt_* packages
        parts = pyfile.parts
        rt_index = None
        for i, part in enumerate(parts):
            if part.startswith('rt_'):
                rt_index = i
                break

        if rt_index is None:
            continue

        # Check if file is in a subdirectory of the package
        depth_in_package = len(parts) - rt_index - 1  # -1 for the file itself

        if depth_in_package <= 1:
            continue  # File is directly in package or one level deep

        try:
            content = pyfile.read_text(encoding='utf-8')
            original = content

            # For files 2+ levels deep, imports from sibling top-level directories
            # need .. prefix. But we already added . prefix, so we need to check
            # if the import target exists at the package root

            # This is complex - for now, let's fix the most common case:
            # Files in package/subdir/file.py importing from package/core/
            # These show up as "from .core" but should be "from ..core"

            # Actually, the simpler fix is to check if the import works
            # and if not, try adding another dot

            # For now, let's handle the specific case of files in subdirs
            # that need to import from sibling subdirs

            lines = content.split('\n')
            new_lines = []
            file_dir = pyfile.parent.name  # e.g., "web", "tracking"

            for line in lines:
                # If we're in a subdir and importing from a sibling subdir
                # Check if the pattern from .X matches a sibling directory
                match = re.match(r'^(\s*)from \.(\w+)(\.\w+)? import (.+)$', line)
                if match:
                    indent = match.group(1)
                    module = match.group(2)
                    submodule = match.group(3) or ''
                    imports = match.group(4)

                    # Get the package root
                    package_root = pyfile.parents[depth_in_package - 1]

                    # Check if module exists at package root (sibling to current dir)
                    sibling_path = package_root / module
                    current_path = pyfile.parent / module

                    if sibling_path.exists() and not current_path.exists():
                        # Need to go up one level - change . to ..
                        new_line = f"{indent}from ..{module}{submodule} import {imports}"
                        new_lines.append(new_line)
                        continue

                new_lines.append(line)

            new_content = '\n'.join(new_lines)

            if new_content != original:
                pyfile.write_text(new_content, encoding='utf-8')
                changes += 1
                print(f"  [FIXED] {pyfile.relative_to(repo_root)} (depth adjustment)")

        except Exception as e:
            print(f"  [ERROR] {pyfile}: {e}")

    return changes


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_internal_imports.py /path/to/repository")
        sys.exit(1)

    repo_path = Path(sys.argv[1]).resolve()

    if not repo_path.exists():
        print(f"Error: Path does not exist: {repo_path}")
        sys.exit(1)

    print("""
================================================================================
   30 DAYS OF RED TEAM - FIX INTERNAL PACKAGE IMPORTS
================================================================================
""")
    print(f"   Repository: {repo_path}\n")

    total_fixes = 0

    # Phase 1: Apply common patterns
    print("[*] Phase 1: Converting absolute imports to relative imports...")
    fixes = fix_specific_patterns(repo_path)
    total_fixes += fixes
    print(f"    Fixed {fixes} files\n")

    # Phase 2: Fix nested directory imports
    print("[*] Phase 2: Fixing nested directory imports...")
    fixes = fix_double_dot_imports(repo_path)
    total_fixes += fixes
    print(f"    Fixed {fixes} files\n")

    # Phase 3: Package-aware fixes
    print("[*] Phase 3: Package-aware import fixes...")
    packages = find_packages(repo_path)
    print(f"    Found {len(packages)} packages")

    for package in packages:
        pkg_fixes = fix_package_imports(package)
        if pkg_fixes > 0:
            print(f"    {package.name}: {pkg_fixes} fixes")
            total_fixes += pkg_fixes

    print(f"""
================================================================================
   IMPORT FIXES COMPLETE
================================================================================

   Total files fixed: {total_fixes}

   Next steps:
   1. Test imports: python -c "from rt_phishing_framework.core import campaign"
   2. Run verify_migration.py again
   3. If issues remain, check specific files manually

   Common remaining issues:
   - Circular imports (need restructuring)
   - Dynamic imports (importlib)
   - Conditional imports

================================================================================
""")


if __name__ == '__main__':
    main()