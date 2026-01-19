from .core.checker import RegistryChecker
from .core.exploiter import MSIExploiter
from .payloads.msfvenom import MsfvenomPayload
from .payloads.wix import WixPayload

__version__ = "1.0.0"
__all__ = [
    "RegistryChecker",
    "MSIExploiter",
    "MsfvenomPayload",
    "WixPayload"
]
