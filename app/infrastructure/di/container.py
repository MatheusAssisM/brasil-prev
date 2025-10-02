from functools import lru_cache

from fastapi import Depends

from app.core.interfaces import DiceRoller, BoardGenerator, SimulatorService, Logger
from app.infrastructure.generators.random import StandardDiceRoller, RandomBoardGenerator
from app.infrastructure.logging.logger import StructuredLogger
from app.application.simulator import GameSimulator


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


def get_logger(name: str = "app") -> Logger:
    """
    Get logger instance.

    Args:
        name: Logger name

    Returns:
        Logger implementation
    """
    return StructuredLogger(name)


def get_simulator_service(
    dice_roller: DiceRoller = Depends(get_dice_roller),
    board_generator: BoardGenerator = Depends(get_board_generator),
) -> SimulatorService:
    """
    Get simulator service instance with dependencies injected.

    Args:
        dice_roller: DiceRoller instance (injected via Depends)
        board_generator: BoardGenerator instance (injected via Depends)

    Returns:
        SimulatorService implementation
    """
    logger = get_logger("app.application.simulator")
    return GameSimulator(board_generator, dice_roller, logger)
