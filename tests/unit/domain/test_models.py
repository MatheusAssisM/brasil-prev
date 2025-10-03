from app.domain.models import Player, Property, GameState
import pytest

from app.domain.strategies import ImpulsiveStrategy
from app.infrastructure.generators.random import RandomBoardGenerator
from app.core.exceptions import (
    InvalidPropertyError,
    InvalidPlayerError,
    InvalidMoveError,
    GameConfigurationError,
)


@pytest.mark.unit
class TestProperty:
    """Test Property model."""

    def test_property_creation(self):
        """Test creating a property."""
        prop = Property(cost=100, rent=50)
        assert prop.cost == 100
        assert prop.rent == 50
        assert prop.owner is None

    def test_property_ownership(self):
        """Test property ownership (using immutable dataclass pattern)."""
        prop = Property(cost=100, rent=50)
        player = Player("Test", ImpulsiveStrategy())

        assert not prop.is_owned()

        # Create new property with owner
        prop_with_owner = prop.with_owner(player)
        assert prop_with_owner.is_owned()
        assert prop_with_owner.owner == player

        # Reset owner
        prop_without_owner = prop_with_owner.reset_owner()
        assert not prop_without_owner.is_owned()
        assert prop_without_owner.owner is None

    def test_property_negative_cost_raises_error(self):
        """Test creating property with negative cost raises error."""
        with pytest.raises(InvalidPropertyError) as exc_info:
            Property(cost=-100, rent=50)

        assert "cost" in str(exc_info.value).lower()

    def test_property_zero_cost_raises_error(self):
        """Test creating property with zero cost raises error."""
        with pytest.raises(InvalidPropertyError) as exc_info:
            Property(cost=0, rent=50)

        assert "cost" in str(exc_info.value).lower()

    def test_property_negative_rent_raises_error(self):
        """Test creating property with negative rent raises error."""
        with pytest.raises(InvalidPropertyError) as exc_info:
            Property(cost=100, rent=-50)

        assert "rent" in str(exc_info.value).lower()


@pytest.mark.unit
class TestPlayer:
    """Test Player model."""

    def test_player_creation(self):
        """Test creating a player."""
        strategy = ImpulsiveStrategy()
        player = Player("Test Player", strategy, initial_balance=300)

        assert player.name == "Test Player"
        assert player.balance == 300
        assert player.position == 0
        assert len(player.properties) == 0
        assert player.is_active is True

    def test_player_movement(self):
        """Test player movement on board."""
        player = Player("Test", ImpulsiveStrategy())
        board_size = 20

        # Move forward
        new_pos = player.move(5, board_size)
        assert new_pos == 5
        assert player.position == 5

        # Move with wraparound and salary
        initial_balance = player.balance
        new_pos = player.move(18, board_size)
        assert new_pos == 3  # (5 + 18) % 20
        assert player.balance == initial_balance + 100  # Got salary

    def test_player_can_buy(self):
        """Test if player can afford property."""
        player = Player("Test", ImpulsiveStrategy(), initial_balance=150)

        assert player.can_buy(100) is True
        assert player.can_buy(150) is True
        assert player.can_buy(200) is False

    def test_player_buy_property(self):
        """Test player buying property."""
        strategy = ImpulsiveStrategy()
        player = Player("Test", strategy, initial_balance=300)
        prop = Property(cost=100, rent=50)

        result = player.buy_property(prop)

        assert result is True
        assert player.balance == 200
        assert len(player.properties) == 1
        # Note: owner assignment is now handled by GameEngine/Board

    def test_player_pay_rent(self):
        """Test player paying rent."""
        player = Player("Test", ImpulsiveStrategy(), initial_balance=100)

        player.pay_rent(50)
        assert player.balance == 50
        assert player.is_active is True

        player.pay_rent(100)
        assert player.balance == -50
        assert player.is_active is False  # Eliminated

    def test_player_receive_rent(self):
        """Test player receiving rent."""
        player = Player("Test", ImpulsiveStrategy(), initial_balance=100)

        player.receive_rent(50)
        assert player.balance == 150

    def test_player_elimination(self):
        """Test player elimination."""
        player = Player("Test", ImpulsiveStrategy())
        prop1 = Property(cost=100, rent=50)
        prop2 = Property(cost=100, rent=50)

        # Manually add properties to player
        player.properties = [prop1, prop2]

        released_properties = player.eliminate()

        assert player.is_active is False
        assert len(player.properties) == 0
        assert len(released_properties) == 2
        # Note: owner reset is now handled by GameEngine/Board repository

    def test_player_empty_name_raises_error(self):
        """Test creating player with empty name raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            Player("", ImpulsiveStrategy())

        assert "name" in str(exc_info.value).lower()

    def test_player_whitespace_name_raises_error(self):
        """Test creating player with whitespace name raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            Player("   ", ImpulsiveStrategy())

        assert "name" in str(exc_info.value).lower()

    def test_player_negative_balance_raises_error(self):
        """Test creating player with negative balance raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            Player("Test", ImpulsiveStrategy(), initial_balance=-100)

        assert "balance" in str(exc_info.value).lower()

    def test_player_none_strategy_raises_error(self):
        """Test creating player with None strategy raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            Player("Test", None)

        assert "strategy" in str(exc_info.value).lower()

    def test_player_move_negative_steps_raises_error(self):
        """Test moving player with negative steps raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidMoveError) as exc_info:
            player.move(-5, 20)

        assert "steps" in str(exc_info.value).lower()

    def test_player_move_zero_steps_raises_error(self):
        """Test moving player with zero steps raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidMoveError) as exc_info:
            player.move(0, 20)

        assert "steps" in str(exc_info.value).lower()

    def test_player_move_invalid_board_size_raises_error(self):
        """Test moving player with invalid board size raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidMoveError) as exc_info:
            player.move(5, 0)

        assert "board size" in str(exc_info.value).lower()

    def test_player_move_negative_salary_raises_error(self):
        """Test moving player with negative salary raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidMoveError) as exc_info:
            player.move(5, 20, round_salary=-100)

        assert "salary" in str(exc_info.value).lower()

    def test_player_can_buy_negative_cost_raises_error(self):
        """Test can_buy with negative cost raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidPropertyError) as exc_info:
            player.can_buy(-100)

        assert "cost" in str(exc_info.value).lower()

    def test_player_buy_property_none_raises_error(self):
        """Test buying None property raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidPropertyError) as exc_info:
            player.buy_property(None)

        assert "property" in str(exc_info.value).lower()

    def test_player_pay_rent_negative_raises_error(self):
        """Test paying negative rent raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidPropertyError) as exc_info:
            player.pay_rent(-50)

        assert "rent" in str(exc_info.value).lower()

    def test_player_receive_rent_negative_raises_error(self):
        """Test receiving negative rent raises error."""
        player = Player("Test", ImpulsiveStrategy())

        with pytest.raises(InvalidPropertyError) as exc_info:
            player.receive_rent(-50)

        assert "rent" in str(exc_info.value).lower()


@pytest.mark.unit
class TestBoard:
    """Test Board model."""

    def test_board_creation(self):
        """Test creating a board."""
        generator = RandomBoardGenerator()
        board = generator.generate(num_properties=20)

        assert board.size() == 20
        # Board now uses repository pattern, access via get_property

    def test_board_properties_are_random(self):
        """Test that board generates properties with varying costs."""
        generator = RandomBoardGenerator()
        board = generator.generate(num_properties=20)

        # Access properties through repository
        costs = [board.get_property(i).cost for i in range(board.size())]
        rents = [board.get_property(i).rent for i in range(board.size())]

        # Check there's variety (not all the same)
        assert len(set(costs)) > 1
        assert len(set(rents)) > 1

        # Check values are in expected ranges
        assert all(50 <= cost <= 200 for cost in costs)
        assert all(10 <= rent <= 100 for rent in rents)

    def test_get_property(self):
        """Test getting property by position."""
        generator = RandomBoardGenerator()
        board = generator.generate(num_properties=20)

        prop = board.get_property(5)
        assert isinstance(prop, Property)


@pytest.mark.unit
class TestGameState:
    """Test GameState model."""

    def test_game_state_creation(self):
        """Test creating game state."""
        generator = RandomBoardGenerator()
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(4)]
        board = generator.generate(20)
        state = GameState(players, board)

        assert len(state.players) == 4
        assert state.round_count == 0
        assert state.max_rounds == 1000
        assert state.winner is None
        assert state.game_over is False

    def test_get_active_players(self):
        """Test getting active players."""
        generator = RandomBoardGenerator()
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(4)]
        board = generator.generate(20)
        state = GameState(players, board)

        # All active initially
        assert len(state.get_active_players()) == 4

        # Eliminate one
        players[0].is_active = False
        assert len(state.get_active_players()) == 3

    def test_victory_condition_one_player(self):
        """Test victory when only one player remains."""
        generator = RandomBoardGenerator()
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(4)]
        board = generator.generate(20)
        state = GameState(players, board)

        # Eliminate all but one
        for player in players[:-1]:
            player.is_active = False

        result = state.check_victory_condition()

        assert result is True
        assert state.game_over is True
        assert state.winner == players[-1]

    def test_victory_condition_max_rounds(self):
        """Test victory when max rounds reached."""
        generator = RandomBoardGenerator()
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(4)]
        board = generator.generate(20)
        state = GameState(players, board)

        # Set different balances
        players[0].balance = 500
        players[1].balance = 300
        players[2].balance = 200
        players[3].balance = 100

        state.round_count = 1000

        result = state.check_victory_condition()

        assert result is True
        assert state.game_over is True
        assert state.winner == players[0]  # Highest balance

    def test_increment_round(self):
        """Test incrementing round counter."""
        generator = RandomBoardGenerator()
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(4)]
        board = generator.generate(20)
        state = GameState(players, board)

        state.increment_round()
        assert state.round_count == 1

        state.increment_round()
        assert state.round_count == 2

    def test_game_state_empty_players_raises_error(self):
        """Test creating game state with empty players raises error."""
        generator = RandomBoardGenerator()
        board = generator.generate(20)

        with pytest.raises(GameConfigurationError) as exc_info:
            GameState([], board)

        assert "empty" in str(exc_info.value).lower()

    def test_game_state_none_board_raises_error(self):
        """Test creating game state with None board raises error."""
        players = [Player("Test", ImpulsiveStrategy())]

        with pytest.raises(GameConfigurationError) as exc_info:
            GameState(players, None)

        assert "board" in str(exc_info.value).lower()

    def test_game_state_negative_max_rounds_raises_error(self):
        """Test creating game state with negative max rounds raises error."""
        generator = RandomBoardGenerator()
        players = [Player("Test", ImpulsiveStrategy())]
        board = generator.generate(20)

        with pytest.raises(GameConfigurationError) as exc_info:
            GameState(players, board, max_rounds=-100)

        assert "max rounds" in str(exc_info.value).lower()

    def test_game_state_zero_max_rounds_raises_error(self):
        """Test creating game state with zero max rounds raises error."""
        generator = RandomBoardGenerator()
        players = [Player("Test", ImpulsiveStrategy())]
        board = generator.generate(20)

        with pytest.raises(GameConfigurationError) as exc_info:
            GameState(players, board, max_rounds=0)

        assert "max rounds" in str(exc_info.value).lower()

    def test_victory_condition_no_players_left(self):
        """Test victory when no players are left (draw)."""
        generator = RandomBoardGenerator()
        players = [Player(f"Player {i}", ImpulsiveStrategy()) for i in range(2)]
        board = generator.generate(20)
        state = GameState(players, board)

        # Eliminate all players
        for player in players:
            player.is_active = False

        result = state.check_victory_condition()

        assert result is True
        assert state.game_over is True
        assert state.winner is None
