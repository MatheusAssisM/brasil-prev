import pytest

from app.infrastructure.generators.random import RandomBoardGenerator, StandardDiceRoller


@pytest.mark.unit
class TestRandomBoardGenerator:
    """Test RandomBoardGenerator."""

    def test_generate_creates_board_with_correct_size(self):
        """Test that generated board has correct number of properties."""
        generator = RandomBoardGenerator()
        board = generator.generate(20)

        assert board.size() == 20

    def test_generated_properties_have_valid_values(self):
        """Test that generated properties have values in correct ranges."""
        generator = RandomBoardGenerator()
        board = generator.generate(20)

        properties = board.repository.get_all_properties()
        for prop in properties:
            assert 50 <= prop.cost <= 200
            assert 10 <= prop.rent <= 100


@pytest.mark.unit
class TestStandardDiceRoller:
    """Test StandardDiceRoller."""

    def test_dice_roll_is_in_valid_range(self):
        """Test that dice rolls return values between 1 and 6."""
        roller = StandardDiceRoller()

        for _ in range(100):
            roll = roller.roll()
            assert 1 <= roll <= 6
