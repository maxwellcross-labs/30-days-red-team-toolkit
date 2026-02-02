"""
Base Phase Class
================

Abstract base class for all attack phases.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable

from ..models import AttackState


class BasePhase(ABC):
    """
    Abstract base class for attack phases.

    All phases should inherit from this class and implement
    the execute() method.
    """

    # Phase metadata
    PHASE_NUMBER: int = 0
    PHASE_NAME: str = "Base Phase"
    PHASE_DESCRIPTION: str = "Base phase class"

    def __init__(self, state: AttackState, logger: Optional[Callable] = None):
        """
        Initialize the phase.

        Args:
            state: The current attack state
            logger: Optional logging function (defaults to print)
        """
        self.state = state
        self._logger = logger or print

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message"""
        self._logger(message, level)

    def log_header(self) -> None:
        """Log the phase header"""
        self.log("=" * 60)
        self.log(f"PHASE {self.PHASE_NUMBER}: {self.PHASE_NAME}")
        self.log("=" * 60)

    @abstractmethod
    def execute(self, **kwargs) -> bool:
        """
        Execute the phase.

        Returns:
            True if phase completed successfully, False otherwise.
        """
        pass

    def validate_prerequisites(self) -> bool:
        """
        Validate that prerequisites for this phase are met.

        Override in subclasses to add specific checks.

        Returns:
            True if prerequisites are met, False otherwise.
        """
        return True

    def cleanup(self) -> None:
        """
        Perform any cleanup after phase execution.

        Override in subclasses if cleanup is needed.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(phase={self.PHASE_NUMBER})"
