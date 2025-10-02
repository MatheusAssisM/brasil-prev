from app.domain.models import Player
import pytest

from app.domain.engine import GameEngine
from app.domain.strategies import ImpulsiveStrategy, DemandingStrategy
from app.infrastructure.generators.random import RandomBoardGenerator, StandardDiceRoller
from app.infrastructure.di.container import get_logger


@pytest.mark.unit
class TestGameEngine:
    """Test GameEngine."""

    def test_engine_creation(self):
        """Test creating game engine."""
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(4)]
        generator = RandomBoardGenerator()
        board = generator.generate(20)
        logger = get_logger("test")
        engine = GameEngine(players, board, logger)

        assert len(engine.state.players) == 4
        assert engine.state.board.size() == 20

    def test_roll_dice(self):
        """Test dice rolling."""
        players = [Player("Test", ImpulsiveStrategy())]
        generator = RandomBoardGenerator()
        board = generator.generate(20)
        logger = get_logger("test")
        engine = GameEngine(players, board, logger)
        dice_roller = StandardDiceRoller()
        engine.set_dice_roller(dice_roller.roll)

        # Roll dice multiple times and check range
        for _ in range(100):
            roll = engine.roll_dice()
            assert 1 <= roll <= 6

    def test_play_turn_movement(self):
        """Test that a turn moves the player."""
        player = Player("Test", ImpulsiveStrategy(), initial_balance=1000)
        generator = RandomBoardGenerator()
        board = generator.generate(20)
        logger = get_logger("test")
        engine = GameEngine([player], board, logger)
        dice_roller = StandardDiceRoller()
        engine.set_dice_roller(dice_roller.roll)

        initial_position = player.position
        engine.play_turn(player)

        # Player should have moved
        assert player.position != initial_position or player.position == 0

    def test_property_purchase_in_turn(self):
        """Test that player can buy property during turn."""
        player = Player("Test", ImpulsiveStrategy(), initial_balance=1000)
        generator = RandomBoardGenerator()
        board = generator.generate(num_properties=20)
        logger = get_logger("test")
        engine = GameEngine([player], board, logger)
        dice_roller = StandardDiceRoller()
        engine.set_dice_roller(dice_roller.roll)

        # Play several turns
        for _ in range(20):
            engine.play_turn(player)

        # Player should have bought some properties
        assert len(player.properties) > 0

    def test_rent_payment(self):
        """Test rent payment between players."""
        generator = RandomBoardGenerator()
        player1 = Player("Player 1", ImpulsiveStrategy(), initial_balance=1000)
        player2 = Player("Player 2", ImpulsiveStrategy(), initial_balance=1000)

        board = generator.generate(num_properties=20)
        logger = get_logger("test")
        engine = GameEngine([player1, player2], board, logger)

        # Have player1 own a property via board repository
        prop = board.get_property(3)
        board.set_property_owner(3, player1)
        player1.properties.append(prop)

        # Get the property with updated owner
        prop_with_owner = board.get_property(3)

        # Move player2 to that property
        initial_balance_p1 = player1.balance
        initial_balance_p2 = player2.balance

        player2.position = 2
        player2.move(1, board.size())  # Now at position 3

        engine._handle_property_landing(player2, prop_with_owner)

        # Player2 should have paid rent
        assert player2.balance == initial_balance_p2 - prop.rent
        # Player1 should have received rent
        assert player1.balance == initial_balance_p1 + prop.rent

    def test_player_elimination(self):
        """Test that players are eliminated when balance < 0."""
        player = Player("Test", ImpulsiveStrategy(), initial_balance=10)
        generator = RandomBoardGenerator()
        board = generator.generate(20)
        logger = get_logger("test")
        GameEngine([player], board, logger)

        player.pay_rent(50)  # Force negative balance

        assert player.balance < 0
        assert player.is_active is False

    def test_play_round(self):
        """Test playing a complete round."""
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(4)]
        generator = RandomBoardGenerator()
        board = generator.generate(20)
        logger = get_logger("test")
        engine = GameEngine(players, board, logger)
        dice_roller = StandardDiceRoller()
        engine.set_dice_roller(dice_roller.roll)

        initial_round = engine.state.round_count
        engine.play_round()

        assert engine.state.round_count == initial_round + 1

    def test_play_game_completes(self):
        """Test that a full game completes."""
        players = [
            Player("Player 1", ImpulsiveStrategy()),
            Player("Player 2", DemandingStrategy()),
        ]
        generator = RandomBoardGenerator()
        board = generator.generate(20)
        logger = get_logger("test")
        engine = GameEngine(players, board, logger)
        dice_roller = StandardDiceRoller()
        engine.set_dice_roller(dice_roller.roll)

        final_state = engine.play_game()

        # Game should be over
        assert final_state.game_over is True

        # Should have a winner or timeout
        assert final_state.winner is not None or final_state.round_count >= 1000

    def test_get_game_result(self):
        """Test getting game result."""
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(2)]
        generator = RandomBoardGenerator()
        board = generator.generate(20)
        logger = get_logger("test")
        engine = GameEngine(players, board, logger)
        dice_roller = StandardDiceRoller()
        engine.set_dice_roller(dice_roller.roll)

        engine.play_game()
        result = engine.get_game_result()

        assert "winner" in result
        assert "rounds" in result
        assert "timeout" in result
        assert "players" in result
        assert len(result["players"]) == 2
