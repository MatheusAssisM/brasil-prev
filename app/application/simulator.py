from typing import Dict, Any, List
from collections import defaultdict

from app.core.interfaces import SimulatorService, DiceRoller, BoardGenerator, Logger
from app.core.exceptions import GameConfigurationError
from app.domain.models import Player
from app.domain.engine import GameEngine
from app.domain.factories import PlayerFactory


class GameSimulator(SimulatorService):
    """Service that orchestrates game simulations and formats results."""

    def __init__(
        self,
        board_generator: BoardGenerator,
        dice_roller: DiceRoller,
        logger: Logger
    ):
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

    def run_batch_simulation(self, num_simulations: int) -> Dict[str, Any]:
        """
        Run multiple game simulations and aggregate statistics.

        Args:
            num_simulations: Number of games to simulate

        Returns:
            Dictionary with aggregated statistics
        """
        if num_simulations <= 0:
            raise GameConfigurationError(
                f"num_simulations must be positive, got {num_simulations}"
            )

        self.logger.info(
            "Starting batch simulation",
            extra={"num_simulations": num_simulations}
        )

        strategy_wins: Dict[str, int] = defaultdict(int)
        strategy_rounds_when_won: Dict[str, List[int]] = defaultdict(list)
        total_rounds = 0
        total_timeouts = 0

        for _ in range(num_simulations):
            result = self.run_single_simulation()

            total_rounds += result["rounds"]
            if result["timeout"]:
                total_timeouts += 1

            if result["winner"]:
                winner_player = next(
                    (p for p in result["players"] if p["name"] == result["winner"]),
                    None
                )
                if winner_player:
                    strategy_wins[winner_player["strategy"]] += 1
                    strategy_rounds_when_won[winner_player["strategy"]].append(
                        result["rounds"]
                    )

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

        most_winning = max(strategy_stats, key=lambda s: s["wins"])

        result = {
            "total_simulations": num_simulations,
            "timeouts": total_timeouts,
            "timeout_rate": total_timeouts / num_simulations,
            "avg_rounds": total_rounds / num_simulations,
            "strategy_statistics": strategy_stats,
            "most_winning_strategy": most_winning["strategy"] if most_winning["wins"] > 0 else None,
        }

        self.logger.info(
            "Batch simulation completed",
            extra={
                "num_simulations": num_simulations,
                "most_winning_strategy": result["most_winning_strategy"],
                "avg_rounds": result["avg_rounds"],
                "timeout_rate": result["timeout_rate"]
            }
        )

        return result
