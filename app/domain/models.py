from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.core.interfaces import PurchaseStrategy, PropertyRepository
from app.core.exceptions import (
    InvalidPropertyError,
    InvalidPlayerError,
    InvalidMoveError,
    GameConfigurationError,
)
from app.domain.value_objects import Money, Position


@dataclass(frozen=True)
class Property:
    """Represents a property on the board (immutable)."""

    cost: Money
    rent: Money
    owner: Optional[Player] = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.cost, Money):
            raise InvalidPropertyError(f"Property cost must be Money, got {type(self.cost).__name__}")
        if not isinstance(self.rent, Money):
            raise InvalidPropertyError(f"Property rent must be Money, got {type(self.rent).__name__}")
        if not self.cost.is_positive():
            raise InvalidPropertyError(f"Property cost must be positive, got {self.cost.amount}")
        if self.rent.is_negative():
            raise InvalidPropertyError(f"Property rent cannot be negative, got {self.rent.amount}")

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

    def __init__(self, name: str, strategy: PurchaseStrategy, initial_balance: int = 300):
        if not name or not name.strip():
            raise InvalidPlayerError("Player name cannot be empty")
        if initial_balance < 0:
            raise InvalidPlayerError(f"Initial balance cannot be negative, got {initial_balance}")
        if strategy is None:
            raise InvalidPlayerError("Player strategy cannot be None")

        self.name = name
        self.strategy = strategy
        self.balance = Money(initial_balance)
        self.position = Position(0)
        self.properties: List[Property] = []
        self.is_active = True

    def move(self, steps: int, board_size: int, round_salary: int = 100) -> int:
        """Move player forward by steps, handling board wraparound."""
        if steps <= 0:
            raise InvalidMoveError(f"Steps must be positive, got {steps}")
        if board_size <= 0:
            raise InvalidMoveError(f"Board size must be positive, got {board_size}")
        if round_salary < 0:
            raise InvalidMoveError(f"Round salary cannot be negative, got {round_salary}")

        new_position, completed_round = self.position.move(steps, board_size)
        self.position = new_position

        if completed_round:
            self.balance = self.balance.add(round_salary)

        return int(self.position)

    def can_buy(self, property_cost: Money) -> bool:
        """Check if player has enough balance to buy a property."""
        if not isinstance(property_cost, Money):
            raise InvalidPropertyError(f"Property cost must be Money, got {type(property_cost).__name__}")
        if property_cost.is_negative():
            raise InvalidPropertyError(f"Property cost cannot be negative, got {property_cost.amount}")
        return self.balance.is_sufficient_for(property_cost)

    def buy_property(self, property: Property) -> bool:
        """
        Attempt to buy a property using the player's strategy.

        Note: This method returns True if purchase is desired and
        affordable. The actual owner assignment should be handled by
        the caller (GameEngine).
        """
        if property is None:
            raise InvalidPropertyError("Property cannot be None")

        if not self.can_buy(property.cost):
            return False

        if self.strategy.should_buy(self, property):
            self.balance = self.balance.subtract(property.cost)
            self.properties.append(property)
            return True

        return False

    def pay_rent(self, amount: Money) -> None:
        """Pay rent to another player."""
        if not isinstance(amount, Money):
            raise InvalidPropertyError(f"Rent amount must be Money, got {type(amount).__name__}")
        if amount.is_negative():
            raise InvalidPropertyError(f"Rent amount cannot be negative, got {amount.amount}")
        self.balance = self.balance.subtract(amount)
        if self.balance.is_negative():
            self.is_active = False

    def receive_rent(self, amount: Money) -> None:
        """Receive rent from another player."""
        if not isinstance(amount, Money):
            raise InvalidPropertyError(f"Rent amount must be Money, got {type(amount).__name__}")
        if amount.is_negative():
            raise InvalidPropertyError(f"Rent amount cannot be negative, got {amount.amount}")
        self.balance = self.balance.add(amount)

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

    def set_property_owner(self, position: int, player: Optional[Player]) -> None:
        """Set the owner of a property at a specific position."""
        self._repository.set_owner(position, player)

    def size(self) -> int:
        """Return the number of properties on the board."""
        return self._repository.size()

    @property
    def repository(self) -> PropertyRepository:
        """Expose repository for advanced operations."""
        return self._repository


class GameState:
    """Tracks the current state of the game."""

    def __init__(self, players: List[Player], board: Board, max_rounds: int = 1000):
        if not players:
            raise GameConfigurationError("Players list cannot be empty")
        if board is None:
            raise GameConfigurationError("Board cannot be None")
        if max_rounds <= 0:
            raise GameConfigurationError(f"Max rounds must be positive, got {max_rounds}")

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
        """Check if game has ended and determine winner (optimized with early returns)."""
        if self.game_over:
            return True

        active_players = self.get_active_players()
        num_active = len(active_players)

        # Case 1: Single winner
        if num_active == 1:
            self.winner = active_players[0]
            self.game_over = True
            return True

        # Case 2: No players left (draw)
        if num_active == 0:
            self.game_over = True
            self.winner = None
            return True

        # Case 3: Timeout - winner is player with highest balance
        if self.round_count >= self.max_rounds:
            self.winner = max(active_players, key=lambda p: int(p.balance)) if active_players else None
            self.game_over = True
            return True

        return False

    def increment_round(self) -> None:
        """Increment the round counter."""
        self.round_count += 1
