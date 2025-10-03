from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    timestamp: datetime
    game_id: str

    def to_dict(self) -> dict:
        """Convert event to dictionary for logging."""
        return {
            "event_type": self.__class__.__name__,
            "timestamp": self.timestamp.isoformat(),
            "game_id": self.game_id,
        }


@dataclass(frozen=True)
class PropertyPurchased(DomainEvent):
    """Event raised when a player purchases a property."""

    player_name: str
    player_strategy: str
    property_cost: int
    property_rent: int
    player_balance_after: int
    position: int

    def to_dict(self) -> dict:
        """Convert event to dictionary for logging."""
        base = super().to_dict()
        base.update(
            {
                "player_name": self.player_name,
                "player_strategy": self.player_strategy,
                "property_cost": self.property_cost,
                "property_rent": self.property_rent,
                "player_balance_after": self.player_balance_after,
                "position": self.position,
            }
        )
        return base


@dataclass(frozen=True)
class RentPaid(DomainEvent):
    """Event raised when a player pays rent to another player."""

    payer_name: str
    payer_strategy: str
    owner_name: str
    owner_strategy: str
    rent_amount: int
    payer_balance_after: int
    owner_balance_after: int
    position: int

    def to_dict(self) -> dict:
        """Convert event to dictionary for logging."""
        base = super().to_dict()
        base.update(
            {
                "payer_name": self.payer_name,
                "payer_strategy": self.payer_strategy,
                "owner_name": self.owner_name,
                "owner_strategy": self.owner_strategy,
                "rent_amount": self.rent_amount,
                "payer_balance_after": self.payer_balance_after,
                "owner_balance_after": self.owner_balance_after,
                "position": self.position,
            }
        )
        return base


@dataclass(frozen=True)
class PlayerEliminated(DomainEvent):
    """Event raised when a player is eliminated from the game."""

    player_name: str
    player_strategy: str
    final_balance: int
    properties_owned: int
    round_number: int

    def to_dict(self) -> dict:
        """Convert event to dictionary for logging."""
        base = super().to_dict()
        base.update(
            {
                "player_name": self.player_name,
                "player_strategy": self.player_strategy,
                "final_balance": self.final_balance,
                "properties_owned": self.properties_owned,
                "round_number": self.round_number,
            }
        )
        return base


@dataclass(frozen=True)
class RoundCompleted(DomainEvent):
    """Event raised when a game round is completed."""

    round_number: int
    active_players: int
    total_players: int

    def to_dict(self) -> dict:
        """Convert event to dictionary for logging."""
        base = super().to_dict()
        base.update(
            {
                "round_number": self.round_number,
                "active_players": self.active_players,
                "total_players": self.total_players,
            }
        )
        return base


@dataclass(frozen=True)
class GameStarted(DomainEvent):
    """Event raised when a game starts."""

    num_players: int
    player_strategies: list[str]
    board_size: int

    def to_dict(self) -> dict:
        """Convert event to dictionary for logging."""
        base = super().to_dict()
        base.update(
            {
                "num_players": self.num_players,
                "player_strategies": self.player_strategies,
                "board_size": self.board_size,
            }
        )
        return base


@dataclass(frozen=True)
class GameFinished(DomainEvent):
    """Event raised when a game finishes."""

    winner_name: str | None
    total_rounds: int
    timeout: bool
    active_players: int

    def to_dict(self) -> dict:
        """Convert event to dictionary for logging."""
        base = super().to_dict()
        base.update(
            {
                "winner_name": self.winner_name,
                "total_rounds": self.total_rounds,
                "timeout": self.timeout,
                "active_players": self.active_players,
            }
        )
        return base
