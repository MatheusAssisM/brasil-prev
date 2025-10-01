from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.core.interfaces import PurchaseStrategy, PropertyRepository


@dataclass(frozen=True)
class Property:
    """Represents a property on the board (immutable)."""

    cost: int
    rent: int
    owner: Optional[Player] = field(default=None, compare=False)

    def is_owned(self) -> bool:
        """Check if property has an owner."""
        return self.owner is not None

    def with_owner(self, player: Optional[Player]) -> Property:
        """Return a new Property instance with a different owner."""
        return Property(cost=self.cost, rent=self.rent, owner=player)

    def reset_owner(self) -> Property:
        """Return a new Property instance with no owner."""
        return Property(cost=self.cost, rent=self.rent, owner=None)


class Player:
    """Represents a player in the game."""

    def __init__(
        self,
        name: str,
        strategy: PurchaseStrategy,
        initial_balance: int = 300
    ):
        self.name = name
        self.strategy = strategy
        self.balance = initial_balance
        self.position = 0
        self.properties: List[Property] = []
        self.is_active = True

    def move(
        self, steps: int, board_size: int, round_salary: int = 100
    ) -> int:
        """Move player forward by steps, handling board wraparound."""
        old_position = self.position
        self.position = (self.position + steps) % board_size

        # Check if player completed a full round (passed position 0)
        if (self.position < old_position or
                (old_position + steps >= board_size)):
            self.balance += round_salary

        return self.position

    def can_buy(self, property_cost: int) -> bool:
        """Check if player has enough balance to buy a property."""
        return self.balance >= property_cost

    def buy_property(self, property: Property) -> bool:
        """
        Attempt to buy a property using the player's strategy.

        Note: This method returns True if purchase is desired and
        affordable. The actual owner assignment should be handled by
        the caller (GameEngine).
        """
        if not self.can_buy(property.cost):
            return False

        if self.strategy.should_buy(self, property):
            self.balance -= property.cost
            self.properties.append(property)
            return True

        return False

    def pay_rent(self, amount: int) -> None:
        """Pay rent to another player."""
        self.balance -= amount
        if self.balance < 0:
            self.is_active = False

    def receive_rent(self, amount: int) -> None:
        """Receive rent from another player."""
        self.balance += amount

    def eliminate(self) -> List[Property]:
        """
        Eliminate player and return properties to be released.

        Returns:
            List of properties that need to be released
        """
        self.is_active = False
        properties_to_release = self.properties.copy()
        self.properties.clear()
        return properties_to_release


class Board:
    """Represents the game board with properties using repository pattern."""

    def __init__(self, repository: PropertyRepository):
        """
        Initialize board with a property repository.

        Args:
            repository: PropertyRepository implementation for managing properties
        """
        self._repository = repository

    def get_property(self, position: int) -> Property:
        """Get property at a specific position."""
        return self._repository.get_property(position)

    def set_property_owner(
        self, position: int, player: Optional[Player]
    ) -> None:
        """Set the owner of a property at a specific position."""
        self._repository.set_owner(position, player)

    def size(self) -> int:
        """Return the number of properties on the board."""
        return self._repository.size()

    @property
    def repository(self):
        """Expose repository for advanced operations."""
        return self._repository


class GameState:
    """Tracks the current state of the game."""

    def __init__(self, players: List[Player], board: Board, max_rounds: int = 1000):
        self.players = players
        self.board = board
        self.round_count = 0
        self.max_rounds = max_rounds
        self.winner: Optional[Player] = None
        self.game_over = False

    def get_active_players(self) -> List[Player]:
        """Get list of players still active in the game."""
        return [p for p in self.players if p.is_active]

    def check_victory_condition(self) -> bool:
        """Check if game has ended and determine winner."""
        active_players = self.get_active_players()

        # Only one player left
        if len(active_players) == 1:
            self.winner = active_players[0]
            self.game_over = True
            return True

        # All players eliminated
        if len(active_players) == 0:
            self.game_over = True
            return True

        # Max rounds reached
        if self.round_count >= self.max_rounds:
            # Winner is the player with highest balance
            self.winner = max(active_players, key=lambda p: p.balance)
            self.game_over = True
            return True

        return False

    def increment_round(self) -> None:
        """Increment the round counter."""
        self.round_count += 1
