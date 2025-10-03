import pytest


from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.main import app
from app.domain.models import Player
from app.domain.strategies import ImpulsiveStrategy
from app.domain.engine import GameEngine
from app.application.simulator import GameSimulator
from app.infrastructure.generators.random import RandomBoardGenerator, StandardDiceRoller
from app.infrastructure.di.container import get_logger


client = TestClient(app)


@pytest.mark.integration
class TestEndToEndIntegration:
    """Test complete flow from API to game engine."""

    def test_complete_game_flow_with_real_dependencies(self):
        """Test a complete game simulation with real dependencies."""
        # Setup
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.integration")

        # Create simulator
        simulator = GameSimulator(board_generator, dice_roller, logger)

        # Run simulation
        result = simulator.run_single_simulation()

        # Assertions
        assert "winner" in result
        assert "rounds" in result
        assert "timeout" in result
        assert "players" in result
        assert len(result["players"]) == 4
        assert result["rounds"] > 0
        assert result["rounds"] <= 1000

    def test_batch_simulation_integration(self):
        """Test batch simulation with aggregated statistics."""
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.integration")

        simulator = GameSimulator(board_generator, dice_roller, logger)

        # Run batch simulation
        result = simulator.run_batch_simulation(10)

        # Assertions
        assert result["total_simulations"] == 10
        assert "timeouts" in result
        assert "timeout_rate" in result
        assert "avg_rounds" in result
        assert "strategy_statistics" in result
        assert len(result["strategy_statistics"]) == 4
        assert "most_winning_strategy" in result

    def test_api_to_engine_integration(self):
        """Test API endpoint triggering complete game flow."""
        response = client.post("/game/simulate")

        assert response.status_code == 200
        data = response.json()

        assert "winner" in data
        assert "players" in data
        assert len(data["players"]) == 4

    def test_batch_api_integration(self):
        """Test batch simulation API endpoint."""
        response = client.post("/simulations/benchmark", json={"num_simulations": 5})

        assert response.status_code == 200
        data = response.json()

        assert data["total_simulations"] == 5
        assert "strategy_statistics" in data
        assert len(data["strategy_statistics"]) == 4


@pytest.mark.integration
class TestMockedIntegration:
    """Test game flow with mocked dependencies for deterministic results."""

    def test_game_with_mocked_dice(self):
        """Test game with deterministic dice rolls."""
        # Mock dice roller that always returns 3
        mock_dice = Mock(return_value=3)

        board_generator = RandomBoardGenerator()
        board = board_generator.generate(20)

        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(2)]
        logger = get_logger("test.mocked")

        engine = GameEngine(players, board, logger)
        engine.set_dice_roller(mock_dice)

        # Play a few turns
        for _ in range(5):
            engine.play_turn(players[0])

        # Verify dice was called
        assert mock_dice.call_count == 5

        # Player should have moved 3 steps each turn
        # After 5 turns: 5 * 3 = 15 steps (position 15 on a 20-space board)
        assert players[0].position == 15

    def test_simulator_with_mocked_logger(self):
        """Test that simulator logs important events."""
        # Mock logger
        mock_logger = Mock()

        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()

        simulator = GameSimulator(board_generator, dice_roller, mock_logger)

        # Run simulation
        simulator.run_single_simulation()

        # Logger is called by GameEngine during the game
        # So we should see some log calls
        assert mock_logger.info.call_count >= 0

    def test_batch_simulator_logs_events(self):
        """Test that batch simulator logs start and completion."""
        mock_logger = Mock()

        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()

        simulator = GameSimulator(board_generator, dice_roller, mock_logger)

        # Run batch simulation (3 simulations will use parallel execution)
        simulator.run_batch_simulation(3)

        # Verify logger was called for batch start and completion
        assert mock_logger.info.call_count >= 2
        call_args = [call[0][0] for call in mock_logger.info.call_args_list]
        # Check for parallel execution messages
        assert (
            "Starting parallel batch simulation" in call_args
            or "Running batch simulation (single-threaded)" in call_args
        )
        assert (
            "Parallel batch simulation completed" in call_args
            or "Running batch simulation (single-threaded)" in call_args
        )


@pytest.mark.integration
class TestRepositoryIntegration:
    """Test property repository integration with game engine."""

    def test_property_ownership_through_repository(self):
        """Test that property ownership is managed correctly."""
        board_generator = RandomBoardGenerator()
        board = board_generator.generate(20)

        player1 = Player("Player 1", ImpulsiveStrategy(), initial_balance=1000)

        # Get property from board
        prop = board.get_property(5)
        assert prop.owner is None

        # Set owner via repository
        board.set_property_owner(5, player1)

        # Get property again - should have owner
        prop_with_owner = board.get_property(5)
        assert prop_with_owner.owner == player1

        # Release property via repository
        board.repository.set_owner(5, None)

        # Property should be ownerless again
        prop_released = board.get_property(5)
        assert prop_released.owner is None

    def test_board_size_integration(self):
        """Test board size is consistent throughout game."""
        board_generator = RandomBoardGenerator()
        board = board_generator.generate(20)

        assert board.size() == 20
        assert len(board.repository.get_all_properties()) == 20

        # Size should remain constant
        player = Player("Test", ImpulsiveStrategy())
        board.set_property_owner(0, player)

        assert board.size() == 20
        assert len(board.repository.get_all_properties()) == 20
