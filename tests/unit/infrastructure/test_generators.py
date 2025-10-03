import pytest

from app.infrastructure.generators.random import RandomBoardGenerator, StandardDiceRoller
from app.core.exceptions import GameConfigurationError


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

    def test_generate_with_none_uses_default(self):
        """Test that passing None uses default number of properties."""
        generator = RandomBoardGenerator()
        board = generator.generate(None)

        assert board.size() == 20  # GameConfig.NUM_PROPERTIES default

    def test_generate_with_negative_raises_error(self):
        """Test that negative num_properties raises error."""
        generator = RandomBoardGenerator()

        with pytest.raises(GameConfigurationError) as exc_info:
            generator.generate(-5)

        assert "positive" in str(exc_info.value).lower()


@pytest.mark.unit
class TestStandardDiceRoller:
    """Test StandardDiceRoller."""

    def test_dice_roll_is_in_valid_range(self):
        """Test that dice rolls return values between 1 and 6."""
        roller = StandardDiceRoller()

        for _ in range(100):
            roll = roller.roll()
            assert 1 <= roll <= 6
