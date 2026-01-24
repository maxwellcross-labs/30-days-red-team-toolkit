from ..scripts import templates
from ..config import proxychains
from ..utils import io


class PivotManager:
    def __init__(self, output_dir="msf_pivoting"):
        self.output_dir = io.ensure_dir(output_dir)
        print(f"[+] MSF Pivoting Manager initialized at: {self.output_dir}")

    def create_route(self, session_id, network, netmask):
        print(f"[*] Generating route script for Session {session_id}...")
        content = templates.get_route_script(session_id, network, netmask)
        filepath = self.output_dir / f"route_session{session_id}.rc"

        io.write_file(filepath, content)
        io.log_instruction([f"msf6 > resource {filepath}"])

    def create_socks(self, session_id, port):
        print(f"[*] Generating SOCKS script (Port {port})...")
        content = templates.get_socks_script(session_id, port)
        filepath = self.output_dir / f"socks_session{session_id}.rc"

        io.write_file(filepath, content)
        conf_path = proxychains.create_config(self.output_dir, port)

        io.log_instruction([
            f"msf6 > resource {filepath}",
            f"Config saved: {conf_path}"
        ])

    def create_portfwd(self, session_id, local, r_host, r_port):
        print(f"[*] Generating PortFwd script...")
        content = templates.get_portfwd_script(session_id, local, r_host, r_port)
        filepath = self.output_dir / f"portfwd_session{session_id}.rc"

        io.write_file(filepath, content)
        io.log_instruction([
            f"msf6 > resource {filepath}",
            f"Access via: localhost:{local}"
        ])

    def create_complete_setup(self, session_id, network, netmask, socks_port):
        print(f"[*] Generating Complete Pivot Suite...")
        content = templates.get_complete_script(session_id, network, netmask, socks_port)
        filepath = self.output_dir / f"complete_pivot_session{session_id}.rc"

        io.write_file(filepath, content)
        proxychains.create_config(self.output_dir, socks_port)

        io.log_instruction([
            f"msf6 > resource {filepath}",
            "Includes: Route, AutoRoute, and SOCKS"
        ])