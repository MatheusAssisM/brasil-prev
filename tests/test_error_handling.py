"""Error handling and edge case tests."""

from fastapi.testclient import TestClient

from app.main import app
from app.core.exceptions import GameConfigurationError
from app.application.simulator import GameSimulator
from app.infrastructure.generators.random import RandomBoardGenerator, StandardDiceRoller
from app.infrastructure.di.container import get_logger


client = TestClient(app)


class TestAPIErrorHandling:
    """Test error handling in API endpoints."""

    def test_batch_simulation_invalid_count(self):
        """Test batch simulation with invalid simulation count (pydantic validation)."""
        response = client.post("/game/stats", json={"num_simulations": 0})

        # Pydantic validation or business logic should catch this
        # Returns either 422 (validation) or 500 (business logic error)
        assert response.status_code in [422, 500]

    def test_batch_simulation_negative_count(self):
        """Test batch simulation with negative count (pydantic validation)."""
        response = client.post("/game/stats", json={"num_simulations": -5})

        # Pydantic validation or business logic should catch this
        assert response.status_code in [422, 500]

    def test_batch_simulation_with_default_value(self):
        """Test batch simulation uses default when no value provided."""
        # BatchSimulationRequest has default=300
        response = client.post("/game/stats", json={})

        # Should succeed with default value
        assert response.status_code == 200
        data = response.json()
        assert data["total_simulations"] == 300

    def test_batch_simulation_invalid_type(self):
        """Test batch simulation with wrong type."""
        response = client.post("/game/stats", json={"num_simulations": "not a number"})

        # Should return 422 validation error
        assert response.status_code == 422

    def test_single_simulation_success(self):
        """Test that single simulation endpoint works correctly."""
        response = client.post("/game/simulate")

        assert response.status_code == 200
        data = response.json()
        assert "winner" in data
        assert "players" in data


class TestSimulatorErrorHandling:
    """Test error handling in simulator service."""

    def test_batch_simulation_zero_count(self):
        """Test that zero simulations raises error."""
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.error")

        simulator = GameSimulator(board_generator, dice_roller, logger)

        try:
            simulator.run_batch_simulation(0)
            assert False, "Should have raised GameConfigurationError"
        except GameConfigurationError as e:
            assert "positive" in str(e).lower()

    def test_batch_simulation_negative_count(self):
        """Test that negative simulations raises error."""
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.error")

        simulator = GameSimulator(board_generator, dice_roller, logger)

        try:
            simulator.run_batch_simulation(-10)
            assert False, "Should have raised GameConfigurationError"
        except GameConfigurationError as e:
            assert "positive" in str(e).lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_game_with_all_players_eliminated_early(self):
        """Test game behavior when all players are eliminated quickly."""
        # This is hard to test deterministically without mocking heavily
        # But we can at least ensure the game handles it gracefully
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.edge")

        simulator = GameSimulator(board_generator, dice_roller, logger)

        # Run multiple simulations - at least one should complete
        result = simulator.run_batch_simulation(10)

        assert result["total_simulations"] == 10
        # Most games should complete (not timeout)
        assert result["timeout_rate"] < 1.0

    def test_batch_simulation_single_run(self):
        """Test batch simulation with just 1 simulation."""
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.edge")

        simulator = GameSimulator(board_generator, dice_roller, logger)

        result = simulator.run_batch_simulation(1)

        assert result["total_simulations"] == 1
        assert len(result["strategy_statistics"]) == 4

    def test_batch_simulation_large_count(self):
        """Test batch simulation with larger count."""
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.edge")

        simulator = GameSimulator(board_generator, dice_roller, logger)

        result = simulator.run_batch_simulation(50)

        assert result["total_simulations"] == 50
        assert len(result["strategy_statistics"]) == 4
        # At least some strategy should have won
        assert result["most_winning_strategy"] is not None

    def test_strategy_statistics_no_wins(self):
        """Test that strategy stats handle zero wins correctly."""
        # Run very few simulations where one strategy might not win
        board_generator = RandomBoardGenerator()
        dice_roller = StandardDiceRoller()
        logger = get_logger("test.edge")

        simulator = GameSimulator(board_generator, dice_roller, logger)

        result = simulator.run_batch_simulation(2)

        # Check that all strategies are in stats even if they didn't win
        assert len(result["strategy_statistics"]) == 4
        for stat in result["strategy_statistics"]:
            assert "strategy" in stat
            assert "wins" in stat
            assert "win_rate" in stat
            assert stat["win_rate"] >= 0.0
            assert stat["win_rate"] <= 1.0


class TestFactoryEdgeCases:
    """Test factory pattern edge cases."""

    def test_factory_creates_players_with_correct_strategies(self):
        """Test that factory creates players with proper strategies."""
        from app.domain.factories import PlayerFactory

        impulsive = PlayerFactory.create_impulsive_player()
        assert impulsive.strategy.get_name() == "impulsive"

        demanding = PlayerFactory.create_demanding_player()
        assert demanding.strategy.get_name() == "demanding"

        cautious = PlayerFactory.create_cautious_player()
        assert cautious.strategy.get_name() == "cautious"

        random_player = PlayerFactory.create_random_player()
        assert random_player.strategy.get_name() == "random"

    def test_factory_creates_default_players(self):
        """Test default player set creation."""
        from app.domain.factories import PlayerFactory

        players = PlayerFactory.create_default_players()

        assert len(players) == 4
        strategies = [p.strategy.get_name() for p in players]
        assert "impulsive" in strategies
        assert "demanding" in strategies
        assert "cautious" in strategies
        assert "random" in strategies

    def test_factory_custom_balance(self):
        """Test creating players with custom balance."""
        from app.domain.factories import PlayerFactory

        player = PlayerFactory.create_impulsive_player(balance=500)
        assert player.balance == 500

    def test_factory_custom_name(self):
        """Test creating players with custom name."""
        from app.domain.factories import PlayerFactory

        player = PlayerFactory.create_impulsive_player(name="Custom Name")
        assert player.name == "Custom Name"


class TestRepositoryEdgeCases:
    """Test repository edge cases."""

    def test_repository_set_owner_multiple_times(self):
        """Test setting property owner multiple times."""
        from app.domain.models import Player
        from app.domain.strategies import ImpulsiveStrategy

        board_generator = RandomBoardGenerator()
        board = board_generator.generate(20)

        player1 = Player("Player 1", ImpulsiveStrategy())
        player2 = Player("Player 2", ImpulsiveStrategy())

        # Set owner to player1
        board.set_property_owner(0, player1)
        assert board.get_property(0).owner == player1

        # Change owner to player2
        board.set_property_owner(0, player2)
        assert board.get_property(0).owner == player2

        # Release property
        board.set_property_owner(0, None)
        assert board.get_property(0).owner is None

    def test_repository_get_all_properties_returns_correct_count(self):
        """Test get_all_properties returns all properties via repository."""
        board_generator = RandomBoardGenerator()
        board = board_generator.generate(20)

        properties = board.repository.get_all_properties()

        assert len(properties) == 20
        # All properties should be valid
        for prop in properties:
            assert prop.cost >= 50
            assert prop.cost <= 200
            assert prop.rent >= 10
            assert prop.rent <= 100
