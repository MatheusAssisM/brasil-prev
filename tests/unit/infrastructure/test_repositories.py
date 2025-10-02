import pytest

from app.domain.models import Player
from app.domain.strategies import ImpulsiveStrategy


@pytest.mark.unit
class TestPropertyRepository:
    """Test property repository operations."""

    def test_set_owner_multiple_times(self, board_generator):
        """Test setting property owner multiple times."""
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

    def test_get_all_properties_returns_correct_count(self, board_generator):
        """Test get_all_properties returns all properties via repository."""
        board = board_generator.generate(20)

        properties = board.repository.get_all_properties()

        assert len(properties) == 20
        for prop in properties:
            assert 50 <= prop.cost <= 200
            assert 10 <= prop.rent <= 100
