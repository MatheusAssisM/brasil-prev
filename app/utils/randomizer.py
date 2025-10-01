"""Utilities for randomization (dice rolls, property generation, etc.)."""

import random
from typing import List

from app.game.models import Property, Board
from app.core.config import GameConfig


def roll_dice() -> int:
    """Roll a standard 6-sided die."""
    return random.randint(1, 6)


def generate_random_property() -> Property:
    """Generate a property with random cost and rent values."""
    cost = random.randint(GameConfig.MIN_PROPERTY_COST, GameConfig.MAX_PROPERTY_COST)
    rent = random.randint(GameConfig.MIN_PROPERTY_RENT, GameConfig.MAX_PROPERTY_RENT)
    return Property(cost=cost, rent=rent)


def generate_board(num_properties: int = None) -> Board:
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

    properties = [generate_random_property() for _ in range(num_properties)]
    return Board(properties)
