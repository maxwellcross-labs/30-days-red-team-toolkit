import os
import re
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

import sys

sys.path.append(str(Path(__file__).parent.parent))
from base import TaskExploitBase


class TaskEnumerator(TaskExploitBase):
    """Enumerate Windows scheduled tasks."""

    # Privileged users we're interested in
    PRIVILEGED_USERS = ['SYSTEM', 'ADMINISTRATOR', 'ADMIN', 'NT AUTHORITY']

    # Script extensions
    SCRIPT_EXTENSIONS = ['.bat', '.cmd', '.ps1', '.vbs', '.js', '.wsf']

    def __init__(self, output_dir: str = "task_exploits", verbose: bool = False):
        """
        Initialize the task enumerator.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.tasks_cache: List[Dict] = []
        self.log("Task Enumerator initialized", "SUCCESS")

    def enumerate_all_tasks(self, refresh: bool = False) -> List[Dict]:
        """
        Enumerate all scheduled tasks on the system.

        Args:
            refresh: Force refresh of cached tasks

        Returns:
            List of task dictionaries
        """
        if self.tasks_cache and not refresh:
            return self.tasks_cache

        self.log("Enumerating scheduled tasks...")

        cmd = 'schtasks /query /fo LIST /v'
        result = self.execute_command(cmd, timeout=60)

        if not result['success']:
            self.log("Failed to enumerate tasks", "ERROR")
            return []

        self.tasks_cache = self._parse_task_output(result['stdout'])

        self.log(f"Found {len(self.tasks_cache)} scheduled tasks", "SUCCESS")

        return self.tasks_cache

    def _parse_task_output(self, output: str) -> List[Dict]:
        """
        Parse schtasks output into structured data.

        Args:
            output: Raw schtasks output

        Returns:
            List of parsed task dictionaries
        """
        tasks = []
        current_task = {}

        for line in output.split('\n'):
            line = line.strip()

            if not line:
                if current_task and 'name' in current_task:
                    tasks.append(current_task)
                    current_task = {}
                continue

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                field_mapping = {
                    'TaskName': 'name',
                    'Task To Run': 'command',
                    'Run As User': 'user',
                    'Status': 'status',
                    'Schedule Type': 'schedule_type',
                    'Start Time': 'start_time',
                    'Next Run Time': 'next_run',
                    'Last Run Time': 'last_run',
                    'Last Result': 'last_result',
                    'Author': 'author',
                    'Comment': 'comment'
                }

                if key in field_mapping:
                    current_task[field_mapping[key]] = value

        # Add last task
        if current_task and 'name' in current_task:
            tasks.append(current_task)

        return tasks

    def get_privileged_tasks(self) -> List[Dict]:
        """
        Get tasks running as privileged users.

        Returns:
            List of privileged tasks
        """
        all_tasks = self.enumerate_all_tasks()
        privileged = []

        for task in all_tasks:
            user = task.get('user', '').upper()

            if any(priv in user for priv in self.PRIVILEGED_USERS):
                privileged.append(task)

        self.log(f"Found {len(privileged)} privileged tasks", "INFO")
        return privileged

    def get_task_details(self, task_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific task.

        Args:
            task_name: Name of the task

        Returns:
            Task dictionary or None
        """
        cmd = f'schtasks /query /tn "{task_name}" /fo LIST /v'
        result = self.execute_command(cmd)

        if not result['success']:
            return None

        tasks = self._parse_task_output(result['stdout'])
        return tasks[0] if tasks else None

    def get_task_xml(self, task_name: str) -> Optional[str]:
        """
        Get task XML definition.

        Args:
            task_name: Name of the task

        Returns:
            XML string or None
        """
        cmd = f'schtasks /query /tn "{task_name}" /xml'
        result = self.execute_command(cmd)

        if result['success']:
            return result['stdout']
        return None

    def extract_script_path(self, command: str) -> Optional[str]:
        """
        Extract script path from a task command.

        Args:
            command: Task command string

        Returns:
            Script path or None
        """
        command = command.strip('"').strip("'")

        # Handle PowerShell commands
        if 'powershell' in command.lower():
            match = re.search(r'-File\s+"?([^"]+\.ps1)"?', command, re.IGNORECASE)
            if match:
                return match.group(1).strip('"')

            match = re.search(r'"?([A-Za-z]:[^"]+\.ps1)"?', command)
            if match:
                return match.group(1).strip('"')

        # Handle cmd.exe commands
        if 'cmd' in command.lower():
            match = re.search(r'/c\s+"?([^"]+\.(bat|cmd))"?', command, re.IGNORECASE)
            if match:
                return match.group(1).strip('"')

        # Direct script path
        for ext in self.SCRIPT_EXTENSIONS:
            if ext in command.lower():
                match = re.search(r'"?([A-Za-z]:[^"]+' + re.escape(ext) + r')"?',
                                  command, re.IGNORECASE)
                if match:
                    return match.group(1).strip('"')

        return None

    def extract_exe_path(self, command: str) -> Optional[str]:
        """
        Extract executable path from a task command.

        Args:
            command: Task command string

        Returns:
            Executable path or None
        """
        command = command.strip('"').strip("'")

        # Look for .exe
        match = re.search(r'"?([A-Za-z]:[^"]+\.exe)"?', command, re.IGNORECASE)
        if match:
            return match.group(1).strip('"')

        # First word might be the executable
        parts = command.split()
        if parts and parts[0].lower().endswith('.exe'):
            return parts[0].strip('"')

        return None

    def is_script_command(self, command: str) -> bool:
        """
        Check if command executes a script.

        Args:
            command: Task command string

        Returns:
            True if script command, False otherwise
        """
        command_lower = command.lower()
        return any(ext in command_lower for ext in self.SCRIPT_EXTENSIONS)

    def export_tasks(self, filename: str = None) -> str:
        """
        Export enumerated tasks to a file.

        Args:
            filename: Optional filename

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tasks_enum_{timestamp}.txt"

        filepath = self.output_dir / filename
        tasks = self.enumerate_all_tasks()

        with open(filepath, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Windows Scheduled Tasks Enumeration\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tasks: {len(tasks)}\n")
            f.write("=" * 60 + "\n\n")

            for task in tasks:
                f.write(f"Task: {task.get('name', 'Unknown')}\n")
                f.write(f"  Command: {task.get('command', 'N/A')}\n")
                f.write(f"  User: {task.get('user', 'N/A')}\n")
                f.write(f"  Status: {task.get('status', 'N/A')}\n")
                f.write(f"  Next Run: {task.get('next_run', 'N/A')}\n")
                f.write("-" * 40 + "\n")

        self.log(f"Tasks exported to: {filepath}", "SUCCESS")
        return str(filepath)


if __name__ == "__main__":
    enumerator = TaskEnumerator(verbose=True)

    print("\n" + "=" * 60)
    print("Scheduled Task Enumeration")
    print("=" * 60 + "\n")

    # Get privileged tasks
    privileged = enumerator.get_privileged_tasks()

    print(f"\nPrivileged Tasks ({len(privileged)}):")
    for task in privileged[:10]:
        print(f"  - {task['name']} (User: {task.get('user', 'N/A')})")