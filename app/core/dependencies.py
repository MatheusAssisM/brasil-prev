from functools import lru_cache
from typing import List

from app.core.interfaces import DiceRoller, BoardGenerator, SimulatorService
from app.utils.implementations import StandardDiceRoller, RandomBoardGenerator
from app.services.simulator import GameSimulator
from app.game.models import Player
from app.game.factories import PlayerFactory
from fastapi import Depends


@lru_cache()
def get_dice_roller() -> DiceRoller:
    """
    Get dice roller instance (singleton).

    Returns:
        DiceRoller implementation
    """
    return StandardDiceRoller()


@lru_cache()
def get_board_generator() -> BoardGenerator:
    """
    Get board generator instance (singleton).

    Returns:
        BoardGenerator implementation
    """
    return RandomBoardGenerator()


def get_default_players() -> List[Player]:
    """
    Get list of default players for a game.

    Returns:
        List of Player instances with different strategies
    """
    return PlayerFactory.create_default_players()


def get_simulator_service(
    dice_roller: DiceRoller = Depends(get_dice_roller),
    board_generator: BoardGenerator = Depends(get_board_generator)
) -> SimulatorService:
    """
    Get simulator service instance with dependencies injected.

    Args:
        dice_roller: DiceRoller instance (injected via Depends)
        board_generator: BoardGenerator instance (injected via Depends)

    Returns:
        SimulatorService implementation
    """
    players = get_default_players()
    return GameSimulator(players, board_generator, dice_roller)
