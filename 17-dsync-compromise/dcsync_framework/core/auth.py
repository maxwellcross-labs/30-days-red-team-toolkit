"""
Authentication Builder — Constructs secretsdump.py auth arguments
from the available credential material (password, hash, AES key, Kerberos).
"""

from typing import List


class AuthBuilder:
    """Build Impacket authentication argument lists."""

    def __init__(
        self,
        domain: str,
        username: str,
        dc_ip: str,
        password: str = "",
        ntlm_hash: str = "",
        aes_key: str = "",
        use_kerberos: bool = False,
    ):
        self.domain = domain
        self.username = username
        self.dc_ip = dc_ip
        self.password = password
        self.ntlm_hash = ntlm_hash
        self.aes_key = aes_key
        self.use_kerberos = use_kerberos

    def build(self) -> List[str]:
        """
        Return the auth portion of a secretsdump.py command.

        Returns an empty list if no auth method is available.
        """
        target = f"{self.domain}/{self.username}@{self.dc_ip}"

        if self.use_kerberos:
            return [target, "-k", "-no-pass"]
        if self.aes_key:
            return [target, "-aesKey", self.aes_key]
        if self.ntlm_hash:
            return [target, "-hashes", f":{self.ntlm_hash}"]
        if self.password:
            return [f"{self.domain}/{self.username}:{self.password}@{self.dc_ip}"]

        print("[-] No authentication method provided")
        return []

    @property
    def auth_label(self) -> str:
        if self.use_kerberos:
            return "Kerberos"
        return "NTLM/Password"