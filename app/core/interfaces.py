from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class PurchaseStrategy(ABC):
    """
    Abstract interface for player purchase decision strategies.

    This interface ensures that player behavior is decoupled from
    the Player domain model, following the Strategy Pattern.
    """

    @abstractmethod
    def should_buy(self, player: Player, property: Property) -> bool:
        """
        Determine if the player should purchase the property.

        Args:
            player: The player making the decision
            property: The property being considered for purchase

        Returns:
            True if the player should buy, False otherwise
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name/type of this strategy."""
        pass


class DiceRoller(ABC):
    """Abstract interface for dice rolling."""

    @abstractmethod
    def roll(self) -> int:
        """
        Roll dice and return the result.

        Returns:
            Integer representing the dice roll result
        """
        pass


class BoardGenerator(ABC):
    """Abstract interface for board generation."""

    @abstractmethod
    def generate(self, num_properties: int) -> Board:
        """
        Generate a game board with properties.

        Args:
            num_properties: Number of properties on the board

        Returns:
            Board instance with generated properties
        """
        pass


class SimulatorService(ABC):
    """Abstract interface for game simulation service."""

    @abstractmethod
    def run_single_simulation(self) -> Dict[str, Any]:
        """
        Run a single game simulation.

        Returns:
            Dictionary with game statistics
        """
        pass

    @abstractmethod
    def run_batch_simulation(self, num_simulations: int) -> Dict[str, Any]:
        """
        Run multiple game simulations and aggregate statistics.

        Args:
            num_simulations: Number of games to simulate

        Returns:
            Dictionary with aggregated statistics
        """
        pass


class PropertyRepository(ABC):
    """Abstract repository for property management."""

    @abstractmethod
    def get_property(self, position: int) -> Property:
        """Get property at a specific position."""
        pass

    @abstractmethod
    def get_all_properties(self) -> List[Property]:
        """Get all properties."""
        pass

    @abstractmethod
    def set_owner(self, position: int, player: Optional[Player]) -> None:
        """Set the owner of a property at a specific position."""
        pass

    @abstractmethod
    def get_owner(self, position: int) -> Optional[Player]:
        """Get the owner of a property at a specific position."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get the total number of properties."""
        pass


class Logger(ABC):
    """Abstract interface for logging."""

    @abstractmethod
    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        pass

    @abstractmethod
    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        pass

    @abstractmethod
    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    def error(
        self, msg: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False
    ) -> None:
        """Log error message."""
        pass
