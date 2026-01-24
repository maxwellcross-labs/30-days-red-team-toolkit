from pathlib import Path


def create_config(output_dir: Path, socks_port: int) -> Path:
    config_file = output_dir / "proxychains.conf"

    content = f"""# Proxychains config for Metasploit SOCKS
strict_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 {socks_port}
"""

    with open(config_file, 'w') as f:
        f.write(content)

    return config_file