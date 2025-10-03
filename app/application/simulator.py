from typing import Dict, Any, List, Optional
from collections import defaultdict
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from app.core.interfaces import SimulatorService, DiceRoller, BoardGenerator, Logger
from app.core.exceptions import GameConfigurationError
from app.core.config import settings
from app.domain.engine import GameEngine
from app.domain.factories import PlayerFactory
from app.infrastructure.di.container import get_board_generator, get_dice_roller, get_logger


def _run_simulation_batch(num_simulations: int) -> Dict[str, Any]:
    """
    Worker function to run a batch of simulations in a separate process.

    This function must be at module level to be pickled by ProcessPoolExecutor.

    Args:
        num_simulations: Number of simulations to run in this batch

    Returns:
        Dictionary with aggregated results from this batch
    """

    board_gen = get_board_generator()
    dice_roll = get_dice_roller()
    logger = get_logger("app.application.simulator.worker")

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


class GameSimulator(SimulatorService):
    """Service that orchestrates game simulations and formats results."""

    def __init__(self, board_generator: BoardGenerator, dice_roller: DiceRoller, logger: Logger):
        """
        Initialize simulator with dependencies.

        Args:
            board_generator: Board generator instance
            dice_roller: Dice roller instance
            logger: Logger instance for logging simulation events
        """
        self.board_generator = board_generator
        self.dice_roller = dice_roller
        self.logger = logger

    def run_single_simulation(self) -> Dict[str, Any]:
        """
        Run a single game simulation.

        Returns:
            Dictionary with complete game statistics
        """
        board = self.board_generator.generate(20)
        players = PlayerFactory.create_default_players()
        engine = GameEngine(players, board, self.logger)
        engine.set_dice_roller(self.dice_roller.roll)
        engine.play_game()
        result = engine.get_game_result()

        return result

    def _aggregate_strategy_statistics(
        self,
        strategy_wins: Dict[str, int],
        strategy_rounds_when_won: Dict[str, List[int]],
        num_simulations: int,
        total_timeouts: int,
    ) -> List[Dict[str, Any]]:
        """
        Aggregate statistics for each strategy.

        Args:
            strategy_wins: Wins per strategy
            strategy_rounds_when_won: Rounds when each strategy won
            num_simulations: Total number of simulations
            total_timeouts: Total number of timeouts

        Returns:
            List of strategy statistics dictionaries
        """
        strategy_stats = []
        for strategy in ["impulsive", "demanding", "cautious", "random"]:
            wins = strategy_wins[strategy]
            win_rate = wins / num_simulations
            rounds_list = strategy_rounds_when_won[strategy]
            avg_rounds = sum(rounds_list) / len(rounds_list) if rounds_list else 0

            strategy_stats.append(
                {
                    "strategy": strategy,
                    "wins": wins,
                    "win_rate": win_rate,
                    "timeouts": total_timeouts,
                    "avg_rounds_when_won": avg_rounds,
                }
            )
        return strategy_stats

    def run_batch_simulation(self, num_simulations: int, num_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        Run multiple game simulations in parallel using multiple processes.

        Args:
            num_simulations: Number of games to simulate
            num_workers: Number of worker processes (None = auto-detect from settings)

        Returns:
            Dictionary with aggregated statistics including performance metrics
        """
        if num_simulations <= 0:
            raise GameConfigurationError(f"num_simulations must be positive, got {num_simulations}")

        start_time = time.perf_counter()

        if num_workers is None:
            num_workers = settings.MAX_WORKERS
        if num_workers == 0:
            num_workers = os.cpu_count() or 4

        self.logger.info(
            "Starting parallel batch simulation",
            extra={"num_simulations": num_simulations, "num_workers": num_workers},
        )

        simulations_per_worker = num_simulations // num_workers
        remainder = num_simulations % num_workers
        chunks = [simulations_per_worker + (1 if i < remainder else 0) for i in range(num_workers)]

        strategy_wins: Dict[str, int] = defaultdict(int)
        strategy_rounds_when_won: Dict[str, List[int]] = defaultdict(list)
        total_rounds = 0
        total_timeouts = 0

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(_run_simulation_batch, chunk_size) for chunk_size in chunks if chunk_size > 0]

            for future in as_completed(futures):
                batch_result = future.result()
                total_rounds += batch_result["total_rounds"]
                total_timeouts += batch_result["total_timeouts"]

                for strategy, wins in batch_result["strategy_wins"].items():
                    strategy_wins[strategy] += wins

                for strategy, rounds_list in batch_result["strategy_rounds_when_won"].items():
                    strategy_rounds_when_won[strategy].extend(rounds_list)

        execution_time = time.perf_counter() - start_time

        strategy_stats = self._aggregate_strategy_statistics(
            strategy_wins, strategy_rounds_when_won, num_simulations, total_timeouts
        )

        most_winning = max(strategy_stats, key=lambda s: s["wins"])
        most_winning_strategy = most_winning["strategy"] if most_winning["wins"] > 0 else None

        result = {
            "total_simulations": num_simulations,
            "timeouts": total_timeouts,
            "timeout_rate": total_timeouts / num_simulations,
            "avg_rounds": total_rounds / num_simulations,
            "strategy_statistics": strategy_stats,
            "most_winning_strategy": most_winning_strategy,
            "execution_time_seconds": round(execution_time, 3),
            "simulations_per_second": round(num_simulations / execution_time, 2),
            "parallelization_enabled": True,
            "num_workers": num_workers,
        }

        self.logger.info(
            "Parallel batch simulation completed",
            extra={
                "num_simulations": num_simulations,
                "num_workers": num_workers,
                "execution_time_seconds": result["execution_time_seconds"],
                "simulations_per_second": result["simulations_per_second"],
                "most_winning_strategy": result["most_winning_strategy"],
            },
        )

        return result
