from abc import ABC, abstractmethod
import subprocess
from typing import Dict, Optional


class BaseTunnel(ABC):
    """Abstract base for tunnels"""

    def __init__(self):
        self.tunnel_info: Dict = {}
        self.is_active = False
        self.process = None

    @abstractmethod
    def start(self) -> bool:
        pass

    @abstractmethod
    def stop(self) -> bool:
        pass

    def get_info(self) -> Dict:
        return self.tunnel_info

    def is_running(self) -> bool:
        if self.process:
            return self.process.poll() is None
        return False