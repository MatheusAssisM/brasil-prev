from typing import List

from app.game.models import Player
from app.game.strategies import (
    ImpulsiveStrategy,
    DemandingStrategy,
    CautiousStrategy,
    RandomStrategy,
)
from app.core.config import GameConfig


class PlayerFactory:
    """Factory for creating players with different strategies."""

    @staticmethod
    def create_impulsive_player(
        name: str = "Impulsive Player",
        balance: int = GameConfig.INITIAL_BALANCE
    ) -> Player:
        """
        Create a player with impulsive strategy.

        Args:
            name: Player name
            balance: Initial balance

        Returns:
            Player with impulsive strategy
        """
        return Player(name, ImpulsiveStrategy(), balance)

    @staticmethod
    def create_demanding_player(
        name: str = "Demanding Player",
        balance: int = GameConfig.INITIAL_BALANCE,
        rent_threshold: int = GameConfig.DEMANDING_RENT_THRESHOLD
    ) -> Player:
        """
        Create a player with demanding strategy.

        Args:
            name: Player name
            balance: Initial balance
            rent_threshold: Minimum rent required to buy property

        Returns:
            Player with demanding strategy
        """
        return Player(name, DemandingStrategy(rent_threshold), balance)

    @staticmethod
    def create_cautious_player(
        name: str = "Cautious Player",
        balance: int = GameConfig.INITIAL_BALANCE,
        reserve_threshold: int = GameConfig.CAUTIOUS_RESERVE_THRESHOLD
    ) -> Player:
        """
        Create a player with cautious strategy.

        Args:
            name: Player name
            balance: Initial balance
            reserve_threshold: Minimum balance to maintain after purchase

        Returns:
            Player with cautious strategy
        """
        return Player(name, CautiousStrategy(reserve_threshold), balance)

    @staticmethod
    def create_random_player(
        name: str = "Random Player",
        balance: int = GameConfig.INITIAL_BALANCE
    ) -> Player:
        """
        Create a player with random strategy.

        Args:
            name: Player name
            balance: Initial balance

        Returns:
            Player with random strategy
        """
        return Player(name, RandomStrategy(), balance)

    @staticmethod
    def create_default_players() -> List[Player]:
        """
        Create the standard 4 players with different strategies.

        Returns:
            List of 4 players with impulsive, demanding, cautious,
            and random strategies
        """
        return [
            PlayerFactory.create_impulsive_player(),
            PlayerFactory.create_demanding_player(),
            PlayerFactory.create_cautious_player(),
            PlayerFactory.create_random_player(),
        ]
