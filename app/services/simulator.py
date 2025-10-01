from typing import Dict, Any, List
from collections import defaultdict

from app.core.interfaces import SimulatorService, DiceRoller, BoardGenerator
from app.game.models import Player
from app.game.engine import GameEngine
from app.game.strategies import (
    ImpulsiveStrategy,
    DemandingStrategy,
    CautiousStrategy,
    RandomStrategy,
)
from app.core.config import GameConfig


class GameSimulator(SimulatorService):
    """Service that orchestrates game simulations and formats results."""

    def __init__(
        self,
        players: List[Player],
        board_generator: BoardGenerator,
        dice_roller: DiceRoller
    ):
        """
        Initialize simulator with dependencies.

        Args:
            players: List of players for the game
            board_generator: Board generator instance
            dice_roller: Dice roller instance
        """
        self.players = players
        self.board_generator = board_generator
        self.dice_roller = dice_roller

    def run_single_simulation(self) -> Dict[str, Any]:
        """
        Run a single game simulation.

        Returns:
            Dictionary with complete game statistics
        """
        board = self.board_generator.generate(20)

        players = [
            Player("Impulsive Player", ImpulsiveStrategy(), GameConfig.INITIAL_BALANCE),
            Player("Demanding Player", DemandingStrategy(GameConfig.DEMANDING_RENT_THRESHOLD), GameConfig.INITIAL_BALANCE),
            Player("Cautious Player", CautiousStrategy(GameConfig.CAUTIOUS_RESERVE_THRESHOLD), GameConfig.INITIAL_BALANCE),
            Player("Random Player", RandomStrategy(), GameConfig.INITIAL_BALANCE),
        ]

        engine = GameEngine(players, board)
        engine.set_dice_roller(self.dice_roller.roll)

        engine.play_game()
        return engine.get_game_result()

    def run_batch_simulation(self, num_simulations: int) -> Dict[str, Any]:
        """
        Run multiple game simulations and aggregate statistics.

        Args:
            num_simulations: Number of games to simulate

        Returns:
            Dictionary with aggregated statistics
        """
        # Track statistics
        strategy_wins = defaultdict(int)
        strategy_rounds_when_won = defaultdict(list)
        total_rounds = 0
        total_timeouts = 0

        # Run simulations
        for _ in range(num_simulations):
            result = self.run_single_simulation()

            total_rounds += result["rounds"]
            if result["timeout"]:
                total_timeouts += 1

            if result["winner"]:
                # Find winner's strategy
                winner_player = next(
                    p for p in result["players"] if p["name"] == result["winner"]
                )
                strategy_wins[winner_player["strategy"]] += 1
                strategy_rounds_when_won[winner_player["strategy"]].append(
                    result["rounds"]
                )

        # Calculate statistics per strategy
        strategy_stats = []
        for strategy in ["impulsive", "demanding", "cautious", "random"]:
            wins = strategy_wins[strategy]
            win_rate = wins / num_simulations if num_simulations > 0 else 0
            rounds_list = strategy_rounds_when_won[strategy]
            avg_rounds = sum(rounds_list) / len(rounds_list) if rounds_list else 0

            strategy_stats.append(
                {
                    "strategy": strategy,
                    "wins": wins,
                    "win_rate": win_rate,
                    "timeouts": total_timeouts,  # Shared across all
                    "avg_rounds_when_won": avg_rounds,
                }
            )

        # Determine most winning strategy
        most_winning = max(strategy_stats, key=lambda s: s["wins"])

        return {
            "total_simulations": num_simulations,
            "timeouts": total_timeouts,
            "timeout_rate": total_timeouts / num_simulations if num_simulations > 0 else 0,
            "avg_rounds": total_rounds / num_simulations if num_simulations > 0 else 0,
            "strategy_statistics": strategy_stats,
            "most_winning_strategy": most_winning["strategy"] if most_winning["wins"] > 0 else None,
        }
