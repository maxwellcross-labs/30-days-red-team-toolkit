from ..utils.process import run_command

class SSHForwarder:
    @staticmethod
    def start_local_forward(pivot, local_port, target_host, target_port):
        """ssh -L local:target:port ..."""
        cmd = [
            'ssh', '-i', pivot.key_path,
            '-L', f'{local_port}:{target_host}:{target_port}',
            '-N', '-f',
            f"{pivot.user}@{pivot.ip}"
        ]
        return run_command(cmd)

    @staticmethod
    def start_dynamic_forward(pivot, socks_port):
        """ssh -D port ..."""
        cmd = [
            'ssh', '-i', pivot.key_path,
            '-D', str(socks_port),
            '-N', '-f',
            f"{pivot.user}@{pivot.ip}"
        ]
        return run_command(cmd)