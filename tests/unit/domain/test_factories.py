import pytest

from app.domain.factories import PlayerFactory
from app.core.exceptions import InvalidPlayerError


@pytest.mark.unit
class TestPlayerFactory:
    """Test PlayerFactory creation methods."""

    def test_create_impulsive_player(self):
        """Test creating impulsive player."""
        player = PlayerFactory.create_impulsive_player()
        assert player.strategy.get_name() == "impulsive"
        assert int(player.balance) == 300

    def test_create_demanding_player(self):
        """Test creating demanding player."""
        player = PlayerFactory.create_demanding_player()
        assert player.strategy.get_name() == "demanding"

    def test_create_cautious_player(self):
        """Test creating cautious player."""
        player = PlayerFactory.create_cautious_player()
        assert player.strategy.get_name() == "cautious"

    def test_create_random_player(self):
        """Test creating random player."""
        player = PlayerFactory.create_random_player()
        assert player.strategy.get_name() == "random"

    def test_create_default_players(self):
        """Test creating default set of players."""
        players = PlayerFactory.create_default_players()

        assert len(players) == 4
        strategies = [p.strategy.get_name() for p in players]
        assert "impulsive" in strategies
        assert "demanding" in strategies
        assert "cautious" in strategies
        assert "random" in strategies

    def test_factory_custom_balance(self):
        """Test creating player with custom balance."""
        player = PlayerFactory.create_impulsive_player(balance=500)
        assert int(player.balance) == 500

    def test_factory_custom_name(self):
        """Test creating player with custom name."""
        player = PlayerFactory.create_impulsive_player(name="Custom Name")
        assert player.name == "Custom Name"

    def test_create_impulsive_player_empty_name_raises_error(self):
        """Test creating impulsive player with empty name raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_impulsive_player(name="")

        assert "name" in str(exc_info.value).lower()

    def test_create_impulsive_player_negative_balance_raises_error(self):
        """Test creating impulsive player with negative balance raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_impulsive_player(balance=-100)

        assert "balance" in str(exc_info.value).lower()

    def test_create_demanding_player_empty_name_raises_error(self):
        """Test creating demanding player with empty name raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_demanding_player(name="  ")

        assert "name" in str(exc_info.value).lower()

    def test_create_demanding_player_negative_balance_raises_error(self):
        """Test creating demanding player with negative balance raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_demanding_player(balance=-50)

        assert "balance" in str(exc_info.value).lower()

    def test_create_demanding_player_negative_threshold_raises_error(self):
        """Test creating demanding player with negative rent threshold raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_demanding_player(rent_threshold=-10)

        assert "threshold" in str(exc_info.value).lower()

    def test_create_cautious_player_empty_name_raises_error(self):
        """Test creating cautious player with empty name raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_cautious_player(name="")

        assert "name" in str(exc_info.value).lower()

    def test_create_cautious_player_negative_balance_raises_error(self):
        """Test creating cautious player with negative balance raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_cautious_player(balance=-200)

        assert "balance" in str(exc_info.value).lower()

    def test_create_cautious_player_negative_reserve_raises_error(self):
        """Test creating cautious player with negative reserve threshold raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_cautious_player(reserve_threshold=-20)

        assert "threshold" in str(exc_info.value).lower()

    def test_create_random_player_empty_name_raises_error(self):
        """Test creating random player with empty name raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_random_player(name="")

        assert "name" in str(exc_info.value).lower()

    def test_create_random_player_negative_balance_raises_error(self):
        """Test creating random player with negative balance raises error."""
        with pytest.raises(InvalidPlayerError) as exc_info:
            PlayerFactory.create_random_player(balance=-75)

        assert "balance" in str(exc_info.value).lower()
