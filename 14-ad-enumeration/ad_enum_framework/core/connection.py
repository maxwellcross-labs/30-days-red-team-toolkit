"""
LDAP connection management
"""

import sys

try:
    from ldap3 import Server, Connection, ALL, NTLM
except ImportError:
    print("[!] ldap3 module required: pip install ldap3")
    sys.exit(1)


class LDAPConnection:
    """Manages LDAP connections to domain controllers"""

    def __init__(self, domain, username, password, dc_ip=None):
        self.domain = domain
        self.username = username
        self.password = password
        self.dc_ip = dc_ip or domain
        self.base_dn = ','.join([f"DC={part}" for part in domain.split('.')])
        self.conn = None
        self.server = None

    def connect(self):
        """Establish LDAP connection to domain controller"""
        print(f"\n{'=' * 60}")
        print(f"CONNECTING TO DOMAIN CONTROLLER")
        print(f"{'=' * 60}")

        try:
            self.server = Server(self.dc_ip, get_info=ALL, use_ssl=False)
            user = f"{self.domain}\\{self.username}"

            print(f"[*] Connecting to {self.dc_ip} as {user}")

            self.conn = Connection(
                self.server,
                user=user,
                password=self.password,
                authentication=NTLM,
                auto_bind=True
            )

            print(f"[+] Connected successfully!")
            print(f"[+] Base DN: {self.base_dn}")
            return True

        except Exception as e:
            print(f"[-] Connection failed: {e}")
            return False

    def disconnect(self):
        """Close LDAP connection"""
        if self.conn:
            self.conn.unbind()
            print(f"[+] Connection closed")

    def get_connection(self):
        """Return the active connection"""
        return self.conn

    def get_base_dn(self):
        """Return the base DN"""
        return self.base_dn