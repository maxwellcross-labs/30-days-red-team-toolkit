"""
Output Parser — Extracts structured credential data from
secretsdump.py stdout for a specific target user.
"""


class SecretsDumpParser:
    """Parse secretsdump.py output into structured dicts."""

    @staticmethod
    def parse_user(output: str, target_user: str) -> dict:
        """
        Parse secretsdump.py output for a specific user.

        Returns dict with keys: username, rid, lm, ntlm, aes256, aes128.
        """
        result = {}

        for line in output.splitlines():
            # Hash line: domain\\user:RID:LM:NTLM:::
            if target_user.lower() in line.lower() and ":::" in line:
                parts = line.strip().split(":")
                if len(parts) >= 4:
                    result["username"] = parts[0]
                    result["rid"] = parts[1]
                    result["lm"] = parts[2]
                    result["ntlm"] = parts[3]

            # Kerberos keys
            if "aes256-cts" in line.lower() and target_user.lower() in output.lower():
                result["aes256"] = line.split(":")[-1].strip()
            if "aes128-cts" in line.lower() and target_user.lower() in output.lower():
                result["aes128"] = line.split(":")[-1].strip()

        return result