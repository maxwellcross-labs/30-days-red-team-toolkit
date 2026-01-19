"""
Configuration Module
====================

Central configuration for the Linux privilege escalation framework.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import os


@dataclass
class Config:
    """
    Framework configuration settings.

    Attributes:
        output_dir: Directory for reports and findings
        timeout: Default timeout for subprocess commands
        verbose: Enable verbose output
        quiet: Suppress non-critical output
        search_depth: Maximum directory depth for searches
        excluded_dirs: Directories to skip during enumeration
        gtfobins_binaries: Known exploitable SUID/sudo binaries
        common_suid_binaries: Standard system SUID binaries (not exploitable)
        privileged_groups: Groups that grant elevated access
        dangerous_capabilities: Linux capabilities enabling privesc
    """

    output_dir: Path = field(default_factory=lambda: Path("/tmp/privesc_enum"))
    timeout: int = 60
    verbose: bool = False
    quiet: bool = False
    search_depth: int = 10

    # Directories to exclude from searches (performance optimization)
    excluded_dirs: List[str] = field(default_factory=lambda: [
        '/proc', '/sys', '/dev', '/run', '/snap'
    ])

    # GTFOBins - Binaries known to be exploitable for privilege escalation
    # Reference: https://gtfobins.github.io/
    gtfobins_binaries: List[str] = field(default_factory=lambda: [
        # Shells & Interpreters
        'bash', 'sh', 'dash', 'zsh', 'csh', 'tcsh', 'fish',
        'python', 'python2', 'python3', 'perl', 'ruby', 'lua',
        'php', 'node', 'tclsh', 'wish',

        # Text Editors
        'vim', 'vi', 'nano', 'pico', 'ed', 'emacs', 'ne',

        # File Viewers
        'more', 'less', 'head', 'tail', 'cat', 'tac',
        'nl', 'od', 'xxd', 'hexdump',

        # File Operations
        'cp', 'mv', 'dd', 'install', 'rsync',

        # Text Processing
        'awk', 'gawk', 'mawk', 'nawk',
        'sed', 'cut', 'sort', 'uniq', 'tr',

        # Archivers
        'tar', 'zip', 'unzip', 'gzip', 'gunzip', 'bzip2',
        'ar', 'cpio', 'zstd',

        # Network Tools
        'wget', 'curl', 'nc', 'netcat', 'ncat', 'socat',
        'ftp', 'tftp', 'scp', 'sftp', 'ssh', 'telnet',

        # System Tools
        'find', 'xargs', 'watch', 'time', 'timeout', 'strace', 'ltrace',
        'nmap', 'man', 'info', 'env', 'nice', 'ionice',

        # Terminal Tools
        'screen', 'tmux', 'script', 'rlwrap', 'expect',

        # Development Tools
        'git', 'svn', 'hg', 'gcc', 'g++', 'make', 'cmake',
        'gdb', 'strace', 'ltrace',

        # Container/Virtualization
        'docker', 'lxc', 'lxd', 'podman', 'runc',

        # Package Managers
        'apt', 'apt-get', 'dpkg', 'yum', 'dnf', 'rpm',
        'pip', 'pip3', 'gem', 'npm', 'cpan',

        # Misc
        'ld.so', 'openssl', 'base64', 'xdotool', 'xclip',
        'dialog', 'whiptail', 'jq', 'column'
    ])

    # Standard system SUID binaries (typically not exploitable on their own)
    common_suid_binaries: List[str] = field(default_factory=lambda: [
        'sudo', 'su', 'passwd', 'mount', 'umount', 'pkexec',
        'polkit-agent-helper-1', 'fusermount', 'fusermount3',
        'newgrp', 'chsh', 'chfn', 'gpasswd', 'unix_chkpwd',
        'at', 'crontab', 'ssh-keysign', 'pam_timestamp_check',
        'ping', 'ping6', 'traceroute', 'traceroute6'
    ])

    # Groups that grant elevated privileges
    privileged_groups: List[str] = field(default_factory=lambda: [
        'sudo', 'wheel', 'admin', 'adm',
        'docker', 'lxd', 'lxc', 'podman',
        'disk', 'video', 'audio',
        'shadow', 'root'
    ])

    # Dangerous Linux capabilities
    dangerous_capabilities: List[str] = field(default_factory=lambda: [
        'cap_setuid',  # Change UID
        'cap_setgid',  # Change GID
        'cap_dac_override',  # Bypass file permission checks
        'cap_dac_read_search',  # Bypass file read permission
        'cap_sys_admin',  # Sysadmin operations (container escape)
        'cap_sys_ptrace',  # Trace/inject into processes
        'cap_sys_module',  # Load kernel modules
        'cap_net_raw',  # Raw sockets (packet capture)
        'cap_net_bind_service',  # Bind to privileged ports
        'cap_chown',  # Change file ownership
        'cap_fowner',  # Bypass permission checks for file owner
        'cap_fsetid',  # Don't clear SUID/SGID bits
        'cap_setfcap',  # Set file capabilities
        'cap_mknod'  # Create special files
    ])

    def __post_init__(self):
        """Ensure output directory exists"""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(exist_ok=True, mode=0o755)

    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        return cls(
            output_dir=Path(os.environ.get('PRIVESC_OUTPUT', '/tmp/privesc_enum')),
            timeout=int(os.environ.get('PRIVESC_TIMEOUT', '60')),
            verbose=os.environ.get('PRIVESC_VERBOSE', '').lower() in ('1', 'true', 'yes'),
            quiet=os.environ.get('PRIVESC_QUIET', '').lower() in ('1', 'true', 'yes')
        )

    def is_gtfobins(self, binary_name: str) -> bool:
        """Check if binary is in GTFOBins list"""
        return binary_name in self.gtfobins_binaries

    def is_common_suid(self, binary_name: str) -> bool:
        """Check if binary is a common system SUID binary"""
        return binary_name in self.common_suid_binaries

    def is_privileged_group(self, group_name: str) -> bool:
        """Check if group grants elevated privileges"""
        return group_name in self.privileged_groups

    def is_dangerous_capability(self, capability: str) -> bool:
        """Check if capability is dangerous"""
        return capability in self.dangerous_capabilities