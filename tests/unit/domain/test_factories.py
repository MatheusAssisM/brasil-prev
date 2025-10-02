import pytest

from app.domain.factories import PlayerFactory


@pytest.mark.unit
class TestPlayerFactory:
    """Test PlayerFactory creation methods."""

    def test_create_impulsive_player(self):
        """Test creating impulsive player."""
        player = PlayerFactory.create_impulsive_player()
        assert player.strategy.get_name() == "impulsive"
        assert player.balance == 300

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
        assert player.balance == 500

    def test_factory_custom_name(self):
        """Test creating player with custom name."""
        player = PlayerFactory.create_impulsive_player(name="Custom Name")
        assert player.name == "Custom Name"
