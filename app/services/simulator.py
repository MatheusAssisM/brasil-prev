"""Game simulation service - orchestrates matches and formats results."""

from typing import List
from collections import defaultdict

from app.game.models import Player
from app.game.engine import GameEngine
from app.game.strategies import (
    ImpulsiveStrategy,
    DemandingStrategy,
    CautiousStrategy,
    RandomStrategy,
)
from app.utils.randomizer import generate_board, roll_dice
from app.core.config import GameConfig


class GameSimulator:
    """Service that orchestrates game simulations and formats results."""

    @staticmethod
    def create_default_players() -> List[Player]:
        """Create the standard 4 players with different strategies."""
        return [
            Player("Impulsive Player", ImpulsiveStrategy(), GameConfig.INITIAL_BALANCE),
            Player("Demanding Player", DemandingStrategy(GameConfig.DEMANDING_RENT_THRESHOLD), GameConfig.INITIAL_BALANCE),
            Player("Cautious Player", CautiousStrategy(GameConfig.CAUTIOUS_RESERVE_THRESHOLD), GameConfig.INITIAL_BALANCE),
            Player("Random Player", RandomStrategy(), GameConfig.INITIAL_BALANCE),
        ]

    @staticmethod
    def run_single_simulation() -> dict:
        """
        Run a single game simulation with default players.

        Returns:
            Dictionary with complete game statistics
        """
        players = GameSimulator.create_default_players()
        board = generate_board()
        engine = GameEngine(players, board)
        engine.set_dice_roller(roll_dice)

        engine.play_game()
        return engine.get_game_result()

    @staticmethod
    def run_batch_simulation(num_simulations: int) -> dict:
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
            result = GameSimulator.run_single_simulation()

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
