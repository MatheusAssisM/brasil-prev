import pytest

from app.core.exceptions import GameConfigurationError
from app.application.simulator import GameSimulator


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
