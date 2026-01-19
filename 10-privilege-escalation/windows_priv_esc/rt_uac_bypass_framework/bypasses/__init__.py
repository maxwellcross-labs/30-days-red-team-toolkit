from .fodhelper import FodhelperBypass
from .eventvwr import EventvwrBypass
from .sdclt import SdcltBypass
from .computerdefaults import ComputerDefaultsBypass
from .slui import SluiBypass
from .diskcleanup import DiskCleanupBypass

# All available bypass classes
BYPASS_METHODS = {
    'fodhelper': FodhelperBypass,
    'eventvwr': EventvwrBypass,
    'sdclt': SdcltBypass,
    'computerdefaults': ComputerDefaultsBypass,
    'slui': SluiBypass,
    'diskcleanup': DiskCleanupBypass
}

__all__ = [
    "FodhelperBypass",
    "EventvwrBypass",
    "SdcltBypass",
    "ComputerDefaultsBypass",
    "SluiBypass",
    "DiskCleanupBypass",
    "BYPASS_METHODS"
]