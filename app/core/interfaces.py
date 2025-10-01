from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.game.models import Player, Property


class PurchaseStrategy(ABC):
    """
    Abstract interface for player purchase decision strategies.

    This interface ensures that player behavior is decoupled from
    the Player domain model, following the Strategy Pattern.
    """

    @abstractmethod
    def should_buy(self, player: 'Player', property: 'Property') -> bool:
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
