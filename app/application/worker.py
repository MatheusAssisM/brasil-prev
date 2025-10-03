from typing import Dict, Any, List
from collections import defaultdict

from app.domain.factories import PlayerFactory
from app.domain.engine import GameEngine


def run_simulation_batch(num_simulations: int) -> Dict[str, Any]:
    """
    Worker function to run a batch of simulations in a separate process.

    This function must be at module level to be pickled by ProcessPoolExecutor.

    Uses lazy import to avoid circular dependency with container.

    Args:
        num_simulations: Number of simulations to run in this batch

    Returns:
        Dictionary with aggregated results from this batch
    """
    from app.infrastructure.di.container import get_board_generator, get_dice_roller, get_logger

    board_gen = get_board_generator()
    dice_roll = get_dice_roller()
    logger = get_logger("app.application.worker")

    strategy_wins: Dict[str, int] = defaultdict(int)
    strategy_rounds_when_won: Dict[str, List[int]] = defaultdict(list)
    total_rounds = 0
    total_timeouts = 0

    for _ in range(num_simulations):
        board = board_gen.generate(20)
        players = PlayerFactory.create_default_players()
        engine = GameEngine(players, board, logger)
        engine.set_dice_roller(dice_roll.roll)
        engine.play_game()
        result = engine.get_game_result()

        total_rounds += result["rounds"]
        if result["timeout"]:
            total_timeouts += 1

        if result["winner"]:
            winner_player = next(
                (p for p in result["players"] if p["name"] == result["winner"]), None
            )
            if winner_player:
                strategy_wins[winner_player["strategy"]] += 1
                strategy_rounds_when_won[winner_player["strategy"]].append(result["rounds"])

    return {
        "num_simulations": num_simulations,
        "strategy_wins": dict(strategy_wins),
        "strategy_rounds_when_won": {k: list(v) for k, v in strategy_rounds_when_won.items()},
        "total_rounds": total_rounds,
        "total_timeouts": total_timeouts,
    }
