import random
from typing import Optional

from app.core.interfaces import DiceRoller, BoardGenerator
from app.game.models import Board, Property
from app.game.repositories import InMemoryPropertyRepository
from app.core.config import GameConfig


class StandardDiceRoller(DiceRoller):
    """Standard 6-sided dice roller implementation."""

    def roll(self) -> int:
        """Roll a standard 6-sided die."""
        return random.randint(1, 6)


class RandomBoardGenerator(BoardGenerator):
    """Board generator with random properties."""

    def generate(self, num_properties: Optional[int] = None) -> Board:
        """
        Generate a game board with random properties.

        Args:
            num_properties: Number of properties on the board.
                           Defaults to GameConfig.NUM_PROPERTIES

        Returns:
            Board instance with randomly generated properties
        """
        if num_properties is None:
            num_properties = GameConfig.NUM_PROPERTIES

        properties = []
        for _ in range(num_properties):
            cost = random.randint(
                GameConfig.MIN_PROPERTY_COST,
                GameConfig.MAX_PROPERTY_COST
            )
            rent = random.randint(
                GameConfig.MIN_PROPERTY_RENT,
                GameConfig.MAX_PROPERTY_RENT
            )
            properties.append(Property(cost=cost, rent=rent))

        repository = InMemoryPropertyRepository(properties)
        return Board(repository)
