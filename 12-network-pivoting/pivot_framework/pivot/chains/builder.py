from pathlib import Path


class ChainBuilder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def create_config(self, socks_port, filename_suffix, is_multihop=False, chain_ports=None):
        """Creates proxychains.conf"""
        filename = f"proxychains_{filename_suffix}.conf"
        config_file = self.output_dir / filename

        content = """# Proxychains configuration
strict_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
"""
        if is_multihop and chain_ports:
            for port in chain_ports:
                content += f"socks5 127.0.0.1 {port}\n"
        else:
            content += f"socks5 127.0.0.1 {socks_port}\n"

        with open(config_file, 'w') as f:
            f.write(content)

        return config_file