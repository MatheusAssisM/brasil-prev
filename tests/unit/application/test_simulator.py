import pytest
from collections import defaultdict

from app.core.exceptions import GameConfigurationError
from app.application.simulator import (
    GameSimulator,
    _execute_single_simulation,
    _process_game_result,
    run_simulation_batch,
)


@pytest.mark.unit
class TestGameSimulator:
    """Test GameSimulator service logic."""

    def test_batch_simulation_zero_count_raises_error(
        self, board_generator, dice_roller, test_logger
    ):
        """Test that zero simulations raises GameConfigurationError."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        with pytest.raises(GameConfigurationError) as exc_info:
            simulator.run_batch_simulation(0)

        assert "positive" in str(exc_info.value).lower()

    def test_batch_simulation_negative_count_raises_error(
        self, board_generator, dice_roller, test_logger
    ):
        """Test that negative simulations raises GameConfigurationError."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        with pytest.raises(GameConfigurationError) as exc_info:
            simulator.run_batch_simulation(-10)

        assert "positive" in str(exc_info.value).lower()

    def test_run_single_simulation(self, board_generator, dice_roller, test_logger):
        """Test that single simulation returns valid game result."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        result = simulator.run_single_simulation()

        assert "winner" in result
        assert "rounds" in result
        assert "timeout" in result
        assert "players" in result
        assert len(result["players"]) == 4
        assert result["rounds"] > 0

    def test_run_batch_simulation_with_custom_workers(
        self, board_generator, dice_roller, test_logger
    ):
        """Test batch simulation with custom number of workers."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        result = simulator.run_batch_simulation(10, num_workers=2)

        assert result["total_simulations"] == 10
        assert result["num_workers"] == 2
        assert result["parallelization_enabled"] is True
        assert "execution_time_seconds" in result
        assert "simulations_per_second" in result
        assert len(result["strategy_statistics"]) == 4

    def test_aggregate_strategy_statistics(self, board_generator, dice_roller, test_logger):
        """Test strategy statistics aggregation."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        strategy_wins = {"impulsive": 10, "demanding": 5, "cautious": 3, "random": 2}
        strategy_rounds = {
            "impulsive": [100, 150, 200],
            "demanding": [120, 180],
            "cautious": [90],
            "random": [],
        }

        stats = simulator._aggregate_strategy_statistics(
            strategy_wins, strategy_rounds, num_simulations=20, total_timeouts=5
        )

        assert len(stats) == 4
        assert stats[0]["strategy"] == "impulsive"
        assert stats[0]["wins"] == 10
        assert stats[0]["win_rate"] == 0.5
        assert stats[0]["avg_rounds_when_won"] == 150.0
        assert stats[3]["avg_rounds_when_won"] == 0

    def test_calculate_worker_chunks(self, board_generator, dice_roller, test_logger):
        """Test worker chunk calculation."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        chunks = simulator._calculate_worker_chunks(10, 3)
        assert sum(chunks) == 10
        assert len(chunks) == 3
        assert chunks == [4, 3, 3]

    def test_build_batch_result(self, board_generator, dice_roller, test_logger):
        """Test batch result building."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        strategy_stats = [
            {"strategy": "impulsive", "wins": 10, "win_rate": 0.5},
            {"strategy": "demanding", "wins": 5, "win_rate": 0.25},
            {"strategy": "cautious", "wins": 3, "win_rate": 0.15},
            {"strategy": "random", "wins": 2, "win_rate": 0.1},
        ]

        result = simulator._build_batch_result(
            num_simulations=20,
            num_workers=4,
            execution_time=1.5,
            strategy_stats=strategy_stats,
            total_timeouts=2,
            total_rounds=500,
        )

        assert result["total_simulations"] == 20
        assert result["num_workers"] == 4
        assert result["execution_time_seconds"] == 1.5
        assert result["most_winning_strategy"] == "impulsive"
        assert result["timeout_rate"] == 0.1
        assert result["avg_rounds"] == 25.0

    def test_build_batch_result_no_winners(self, board_generator, dice_roller, test_logger):
        """Test batch result building when no one wins."""
        simulator = GameSimulator(board_generator, dice_roller, test_logger)

        strategy_stats = [
            {"strategy": "impulsive", "wins": 0, "win_rate": 0.0},
            {"strategy": "demanding", "wins": 0, "win_rate": 0.0},
            {"strategy": "cautious", "wins": 0, "win_rate": 0.0},
            {"strategy": "random", "wins": 0, "win_rate": 0.0},
        ]

        result = simulator._build_batch_result(
            num_simulations=10,
            num_workers=2,
            execution_time=1.0,
            strategy_stats=strategy_stats,
            total_timeouts=10,
            total_rounds=100,
        )

        assert result["most_winning_strategy"] is None


@pytest.mark.unit
class TestModuleFunctions:
    """Test module-level functions in simulator."""

    def test_execute_single_simulation(self, board_generator, dice_roller, test_logger):
        """Test single simulation execution."""
        result = _execute_single_simulation(board_generator, dice_roller, test_logger)

        assert "winner" in result
        assert "rounds" in result
        assert "players" in result

    def test_process_game_result_with_winner(self):
        """Test processing game result with a winner."""
        result = {
            "winner": "Impulsive Player",
            "rounds": 150,
            "timeout": False,
            "players": [
                {"name": "Impulsive Player", "strategy": "impulsive"},
                {"name": "Demanding Player", "strategy": "demanding"},
            ],
        }

        strategy_wins = defaultdict(int)
        strategy_rounds = defaultdict(list)

        total_rounds, total_timeouts = _process_game_result(result, strategy_wins, strategy_rounds)

        assert total_rounds == 150
        assert total_timeouts == 0
        assert strategy_wins["impulsive"] == 1
        assert strategy_rounds["impulsive"] == [150]

    def test_process_game_result_timeout(self):
        """Test processing game result with timeout."""
        result = {
            "winner": None,
            "rounds": 1000,
            "timeout": True,
            "players": [],
        }

        strategy_wins = defaultdict(int)
        strategy_rounds = defaultdict(list)

        total_rounds, total_timeouts = _process_game_result(result, strategy_wins, strategy_rounds)

        assert total_rounds == 1000
        assert total_timeouts == 1

    def test_run_simulation_batch(self):
        """Test running a batch of simulations."""
        result = run_simulation_batch(5)

        assert result["num_simulations"] == 5
        assert "strategy_wins" in result
        assert "strategy_rounds_when_won" in result
        assert "total_rounds" in result
        assert "total_timeouts" in result
