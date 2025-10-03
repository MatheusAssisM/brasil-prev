from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Money:
    """
    Value Object representing monetary amounts.

    Encapsulates money with validation and safe operations.
    Immutable to prevent accidental modifications.
    """

    amount: int

    def __post_init__(self) -> None:
        """Validate money amount on creation."""
        if not isinstance(self.amount, int):
            raise TypeError(f"Money amount must be an integer, got {type(self.amount).__name__}")

    def add(self, other: Union[Money, int]) -> Money:
        """
        Add money amounts.

        Args:
            other: Money instance or integer to add

        Returns:
            New Money instance with sum
        """
        if isinstance(other, Money):
            return Money(self.amount + other.amount)
        if isinstance(other, int):
            return Money(self.amount + other)
        raise TypeError(f"Cannot add Money with {type(other).__name__}")

    def subtract(self, other: Union[Money, int]) -> Money:
        """
        Subtract money amounts.

        Args:
            other: Money instance or integer to subtract

        Returns:
            New Money instance with difference (can be negative)
        """
        if isinstance(other, Money):
            return Money(self.amount - other.amount)
        if isinstance(other, int):
            return Money(self.amount - other)
        raise TypeError(f"Cannot subtract {type(other).__name__} from Money")

    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > 0

    def is_negative(self) -> bool:
        """Check if amount is negative."""
        return self.amount < 0

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == 0

    def is_sufficient_for(self, cost: Union[Money, int]) -> bool:
        """
        Check if this amount is sufficient to cover a cost.

        Args:
            cost: Money instance or integer representing cost

        Returns:
            True if amount >= cost, False otherwise
        """
        if isinstance(cost, Money):
            return self.amount >= cost.amount
        if isinstance(cost, int):
            return self.amount >= cost
        raise TypeError(f"Cannot compare Money with {type(cost).__name__}")

    def __int__(self) -> int:
        """Convert to integer."""
        return self.amount

    def __lt__(self, other: Union[Money, int]) -> bool:
        """Less than comparison."""
        if isinstance(other, Money):
            return self.amount < other.amount
        if isinstance(other, int):
            return self.amount < other
        return NotImplemented

    def __le__(self, other: Union[Money, int]) -> bool:
        """Less than or equal comparison."""
        if isinstance(other, Money):
            return self.amount <= other.amount
        if isinstance(other, int):
            return self.amount <= other
        return NotImplemented

    def __gt__(self, other: Union[Money, int]) -> bool:
        """Greater than comparison."""
        if isinstance(other, Money):
            return self.amount > other.amount
        if isinstance(other, int):
            return self.amount > other
        return NotImplemented

    def __ge__(self, other: Union[Money, int]) -> bool:
        """Greater than or equal comparison."""
        if isinstance(other, Money):
            return self.amount >= other.amount
        if isinstance(other, int):
            return self.amount >= other
        return NotImplemented

    def __str__(self) -> str:
        """String representation."""
        return f"${self.amount}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Money(amount={self.amount})"


@dataclass(frozen=True)
class Position:
    """
    Value Object representing a position on the game board.

    Encapsulates board position with validation and wrapping logic.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate position on creation."""
        if not isinstance(self.value, int):
            raise TypeError(f"Position must be an integer, got {type(self.value).__name__}")
        if self.value < 0:
            raise ValueError(f"Position cannot be negative, got {self.value}")

    def move(self, steps: int, board_size: int) -> tuple[Position, bool]:
        """
        Move position forward by steps with board wrapping.

        Args:
            steps: Number of steps to move (must be positive)
            board_size: Size of the board for wrapping

        Returns:
            Tuple of (new_position, completed_round)
            completed_round is True if wrapped around the board
        """
        if steps <= 0:
            raise ValueError(f"Steps must be positive, got {steps}")
        if board_size <= 0:
            raise ValueError(f"Board size must be positive, got {board_size}")

        new_value = (self.value + steps) % board_size
        completed_round = new_value < self.value or (self.value + steps >= board_size)

        return Position(new_value), completed_round

    def __int__(self) -> int:
        """Convert to integer."""
        return self.value

    def __str__(self) -> str:
        """String representation."""
        return f"Position({self.value})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Position(value={self.value})"
