import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.domain.models import Player, Property
from app.domain.value_objects import Money
from app.domain.strategies import (
    ImpulsiveStrategy,
    DemandingStrategy,
    CautiousStrategy,
    RandomStrategy,
)
from app.infrastructure.generators.random import RandomBoardGenerator, StandardDiceRoller
from app.infrastructure.di.container import get_logger


@pytest.fixture
def test_client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def board_generator():
    """Board generator fixture."""
    return RandomBoardGenerator()


@pytest.fixture
def dice_roller():
    """Dice roller fixture."""
    return StandardDiceRoller()


@pytest.fixture
def test_logger():
    """Test logger fixture."""
    return get_logger("test")


@pytest.fixture
def sample_property():
    """Sample property fixture."""
    return Property(cost=Money(100), rent=Money(50))


@pytest.fixture
def sample_player():
    """Sample player with impulsive strategy."""
    return Player("Test Player", ImpulsiveStrategy(), initial_balance=300)


@pytest.fixture
def sample_players():
    """Sample list of 4 players with different strategies."""
    return [
        Player("Impulsive Player", ImpulsiveStrategy()),
        Player("Demanding Player", DemandingStrategy()),
        Player("Cautious Player", CautiousStrategy()),
        Player("Random Player", RandomStrategy()),
    ]


@pytest.fixture
def sample_board(board_generator):
    """Sample board with 20 properties."""
    return board_generator.generate(20)


@pytest.fixture
def impulsive_strategy():
    """Impulsive strategy fixture."""
    return ImpulsiveStrategy()


@pytest.fixture
def demanding_strategy():
    """Demanding strategy fixture."""
    return DemandingStrategy(rent_threshold=50)


@pytest.fixture
def cautious_strategy():
    """Cautious strategy fixture."""
    return CautiousStrategy(reserve_threshold=80)


@pytest.fixture
def random_strategy():
    """Random strategy fixture."""
    return RandomStrategy()


@pytest.fixture
def money():
    """Helper to create Money instances easily in tests."""
    return Money


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
