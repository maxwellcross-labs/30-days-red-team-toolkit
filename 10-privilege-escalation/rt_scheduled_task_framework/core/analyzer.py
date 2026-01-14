import os
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

import sys

sys.path.append(str(Path(__file__).parent.parent))
from base import TaskExploitBase
from enumerator import TaskEnumerator


@dataclass
class ExploitOpportunity:
    """Represents an exploitation opportunity."""
    task_name: str
    task_user: str
    opportunity_type: str
    severity: str  # high, medium, low
    target_path: str
    description: str
    exploitation_method: str
    next_run: str = "Unknown"

    def to_dict(self) -> Dict:
        return {
            'task_name': self.task_name,
            'task_user': self.task_user,
            'type': self.opportunity_type,
            'severity': self.severity,
            'target_path': self.target_path,
            'description': self.description,
            'exploitation': self.exploitation_method,
            'next_run': self.next_run
        }


class TaskAnalyzer(TaskExploitBase):
    """Analyze scheduled tasks for exploitation opportunities."""

    def __init__(self, output_dir: str = "task_exploits", verbose: bool = False):
        """
        Initialize the task analyzer.

        Args:
            output_dir: Directory for storing output files
            verbose: Enable verbose logging
        """
        super().__init__(output_dir, verbose)
        self.enumerator = TaskEnumerator(output_dir, verbose)

        self.findings = {
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }

        self.log("Task Analyzer initialized", "SUCCESS")

    def analyze_all_tasks(self) -> List[ExploitOpportunity]:
        """
        Analyze all tasks for exploitation opportunities.

        Returns:
            List of exploitation opportunities
        """
        self.log("Analyzing scheduled tasks for vulnerabilities...")

        opportunities = []
        privileged_tasks = self.enumerator.get_privileged_tasks()

        self.log(f"Analyzing {len(privileged_tasks)} privileged tasks...")

        for task in privileged_tasks:
            task_opps = self._analyze_task(task)
            opportunities.extend(task_opps)

        # Categorize findings
        for opp in opportunities:
            self.findings[opp.severity].append(opp.to_dict())

        self.log(f"Found {len(opportunities)} exploitation opportunities", "SUCCESS")
        return opportunities

    def _analyze_task(self, task: Dict) -> List[ExploitOpportunity]:
        """
        Analyze a single task for vulnerabilities.

        Args:
            task: Task dictionary

        Returns:
            List of opportunities for this task
        """
        opportunities = []
        command = task.get('command', '')

        if not command:
            return opportunities

        # Check for writable scripts
        if self.enumerator.is_script_command(command):
            script_opp = self._check_writable_script(task, command)
            if script_opp:
                opportunities.append(script_opp)

        # Check for writable executable directory
        exe_opp = self._check_writable_exe_directory(task, command)
        if exe_opp:
            opportunities.append(exe_opp)

        # Check for DLL hijacking opportunities
        dll_opp = self._check_dll_hijacking(task, command)
        if dll_opp:
            opportunities.append(dll_opp)

        return opportunities

    def _check_writable_script(self, task: Dict, command: str) -> Optional[ExploitOpportunity]:
        """
        Check if task runs a writable script.

        Args:
            task: Task dictionary
            command: Task command

        Returns:
            ExploitOpportunity or None
        """
        script_path = self.enumerator.extract_script_path(command)

        if not script_path:
            return None

        if not os.path.exists(script_path):
            if self.verbose:
                self.log(f"Script not found: {script_path}", "WARNING")
            return None

        if self.is_writable(script_path):
            self.log(f"FOUND: Writable script - {task['name']}", "SUCCESS")

            return ExploitOpportunity(
                task_name=task['name'],
                task_user=task.get('user', 'Unknown'),
                opportunity_type='writable_script',
                severity='high',
                target_path=script_path,
                description=f"Task runs writable script as {task.get('user', 'Unknown')}",
                exploitation_method="Modify script to inject payload while preserving functionality",
                next_run=task.get('next_run', 'Unknown')
            )

        return None

    def _check_writable_exe_directory(self, task: Dict, command: str) -> Optional[ExploitOpportunity]:
        """
        Check if task executable is in a writable directory.

        Args:
            task: Task dictionary
            command: Task command

        Returns:
            ExploitOpportunity or None
        """
        exe_path = self.enumerator.extract_exe_path(command)

        if not exe_path:
            return None

        if not os.path.exists(exe_path):
            return None

        exe_dir = os.path.dirname(exe_path)

        if self.is_writable(exe_dir):
            self.log(f"FOUND: Writable exe directory - {task['name']}", "SUCCESS")

            return ExploitOpportunity(
                task_name=task['name'],
                task_user=task.get('user', 'Unknown'),
                opportunity_type='writable_exe_directory',
                severity='medium',
                target_path=exe_dir,
                description=f"Task executable in writable directory",
                exploitation_method="DLL hijacking or binary replacement",
                next_run=task.get('next_run', 'Unknown')
            )

        return None

    def _check_dll_hijacking(self, task: Dict, command: str) -> Optional[ExploitOpportunity]:
        """
        Check for DLL hijacking opportunities.

        Args:
            task: Task dictionary
            command: Task command

        Returns:
            ExploitOpportunity or None
        """
        exe_path = self.enumerator.extract_exe_path(command)

        if not exe_path:
            return None

        if not os.path.exists(exe_path):
            return None

        exe_dir = os.path.dirname(exe_path)

        # Check if we can write to the exe directory for DLL planting
        if self.is_writable(exe_dir):
            # This is already covered by writable_exe_directory
            # but we note the specific DLL hijacking potential
            return None

        # Check PATH directories for hijacking
        path_dirs = os.environ.get('PATH', '').split(';')

        for path_dir in path_dirs:
            if path_dir and os.path.exists(path_dir):
                if self.is_writable(path_dir):
                    # Found writable PATH directory before system dirs
                    if self.verbose:
                        self.log(f"Writable PATH dir: {path_dir}", "INFO")

                    return ExploitOpportunity(
                        task_name=task['name'],
                        task_user=task.get('user', 'Unknown'),
                        opportunity_type='path_dll_hijacking',
                        severity='low',
                        target_path=path_dir,
                        description=f"Writable directory in PATH before system directories",
                        exploitation_method="Plant malicious DLL in writable PATH directory",
                        next_run=task.get('next_run', 'Unknown')
                    )

        return None

    def get_high_priority_findings(self) -> List[Dict]:
        """Get high priority findings."""
        return self.findings['high']

    def get_medium_priority_findings(self) -> List[Dict]:
        """Get medium priority findings."""
        return self.findings['medium']

    def get_all_findings(self) -> Dict[str, List]:
        """Get all findings categorized by severity."""
        return self.findings

    def display_findings(self) -> None:
        """Display formatted findings report."""
        print("\n" + "=" * 60)
        print("EXPLOITATION OPPORTUNITIES")
        print("=" * 60)

        if self.findings['high']:
            print(f"\n[HIGH PRIORITY] - {len(self.findings['high'])} findings")
            print("-" * 60)

            for i, finding in enumerate(self.findings['high'], 1):
                print(f"\n{i}. {finding['type'].upper()}")
                print(f"   Task: {finding['task_name']}")
                print(f"   Target: {finding['target_path']}")
                print(f"   User: {finding['task_user']}")
                print(f"   Next Run: {finding['next_run']}")
                print(f"   Exploitation: {finding['exploitation']}")

        if self.findings['medium']:
            print(f"\n[MEDIUM PRIORITY] - {len(self.findings['medium'])} findings")
            print("-" * 60)

            for i, finding in enumerate(self.findings['medium'], 1):
                print(f"\n{i}. {finding['type'].upper()}")
                print(f"   Task: {finding['task_name']}")
                print(f"   Target: {finding['target_path']}")
                print(f"   User: {finding['task_user']}")
                print(f"   Exploitation: {finding['exploitation']}")

        if self.findings['low']:
            print(f"\n[LOW PRIORITY] - {len(self.findings['low'])} findings")
            print("-" * 60)

            for i, finding in enumerate(self.findings['low'], 1):
                print(f"\n{i}. {finding['type'].upper()}")
                print(f"   Task: {finding['task_name']}")
                print(f"   Target: {finding['target_path']}")

        if not any(self.findings.values()):
            print("\n[-] No exploitation opportunities found")
            print("    All scheduled tasks appear to be configured securely")

    def export_analysis(self, filename: str = None) -> str:
        """
        Export analysis results to file.

        Args:
            filename: Optional filename

        Returns:
            Path to exported file
        """
        import json

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"task_analysis_{timestamp}.json"

        filepath = self.output_dir / filename

        report = {
            'timestamp': datetime.now().isoformat(),
            'findings': self.findings,
            'summary': {
                'high': len(self.findings['high']),
                'medium': len(self.findings['medium']),
                'low': len(self.findings['low']),
                'total': sum(len(v) for v in self.findings.values())
            }
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"Analysis exported to: {filepath}", "SUCCESS")
        return str(filepath)


if __name__ == "__main__":
    analyzer = TaskAnalyzer(verbose=True)

    print("\n" + "=" * 60)
    print("Scheduled Task Vulnerability Analysis")
    print("=" * 60 + "\n")

    opportunities = analyzer.analyze_all_tasks()
    analyzer.display_findings()