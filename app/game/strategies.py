import random
from typing import TYPE_CHECKING

from app.core.interfaces import PurchaseStrategy

if TYPE_CHECKING:
    from app.game.models import Player, Property


class ImpulsiveStrategy(PurchaseStrategy):
    """
    Impulsive player always buys any property they can afford.
    """

    def should_buy(self, player: 'Player', property: 'Property') -> bool:
        """Always returns True - buys whenever possible."""
        return True

    def get_name(self) -> str:
        return "impulsive"


class DemandingStrategy(PurchaseStrategy):
    """
    Demanding player only buys properties with rent above a threshold.
    """

    def __init__(self, rent_threshold: int = 50):
        self.rent_threshold = rent_threshold

    def should_buy(self, player: 'Player', property: 'Property') -> bool:
        """Buy only if rent is greater than the threshold."""
        return property.rent > self.rent_threshold

    def get_name(self) -> str:
        return "demanding"


class CautiousStrategy(PurchaseStrategy):
    """
    Cautious player only buys if they'll have a safe balance remaining.
    """

    def __init__(self, reserve_threshold: int = 80):
        self.reserve_threshold = reserve_threshold

    def should_buy(self, player: 'Player', property: 'Property') -> bool:
        """Buy only if balance after purchase remains above threshold."""
        balance_after_purchase = player.balance - property.cost
        return balance_after_purchase >= self.reserve_threshold

    def get_name(self) -> str:
        return "cautious"


class RandomStrategy(PurchaseStrategy):
    """
    Random player has a 50% chance of buying any property they can afford.
    """

    def should_buy(self, player: 'Player', property: 'Property') -> bool:
        """Randomly decide with 50% probability."""
        return random.random() < 0.5

    def get_name(self) -> str:
        return "random"
