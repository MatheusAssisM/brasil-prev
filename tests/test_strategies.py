from app.domain.models import Player, Property
from app.domain.strategies import (
    ImpulsiveStrategy,
    DemandingStrategy,
    CautiousStrategy,
    RandomStrategy,
)


class TestImpulsiveStrategy:
    """Test the Impulsive strategy."""

    def test_always_buys(self):
        """Impulsive player should always want to buy."""
        strategy = ImpulsiveStrategy()
        player = Player("Test", strategy, initial_balance=300)
        property = Property(cost=100, rent=50)

        assert strategy.should_buy(player, property) is True

    def test_strategy_name(self):
        """Check strategy name."""
        strategy = ImpulsiveStrategy()
        assert strategy.get_name() == "impulsive"


class TestDemandingStrategy:
    """Test the Demanding strategy."""

    def test_buys_high_rent_property(self):
        """Demanding player should buy properties with rent > threshold."""
        strategy = DemandingStrategy(rent_threshold=50)
        player = Player("Test", strategy, initial_balance=300)
        property = Property(cost=100, rent=60)

        assert strategy.should_buy(player, property) is True

    def test_rejects_low_rent_property(self):
        """Demanding player should reject properties with rent <= threshold."""
        strategy = DemandingStrategy(rent_threshold=50)
        player = Player("Test", strategy, initial_balance=300)
        property = Property(cost=100, rent=40)

        assert strategy.should_buy(player, property) is False

    def test_strategy_name(self):
        """Check strategy name."""
        strategy = DemandingStrategy()
        assert strategy.get_name() == "demanding"


class TestCautiousStrategy:
    """Test the Cautious strategy."""

    def test_buys_when_safe_balance_remains(self):
        """Cautious player should buy if balance remains above threshold."""
        strategy = CautiousStrategy(reserve_threshold=80)
        player = Player("Test", strategy, initial_balance=300)
        property = Property(cost=100, rent=50)

        # 300 - 100 = 200, which is >= 80
        assert strategy.should_buy(player, property) is True

    def test_rejects_when_unsafe_balance(self):
        """Cautious player should reject if balance would drop too low."""
        strategy = CautiousStrategy(reserve_threshold=80)
        player = Player("Test", strategy, initial_balance=150)
        property = Property(cost=100, rent=50)

        # 150 - 100 = 50, which is < 80
        assert strategy.should_buy(player, property) is False

    def test_strategy_name(self):
        """Check strategy name."""
        strategy = CautiousStrategy()
        assert strategy.get_name() == "cautious"


class TestRandomStrategy:
    """Test the Random strategy."""

    def test_random_behavior(self):
        """Random player should return varying results."""
        strategy = RandomStrategy()
        player = Player("Test", strategy, initial_balance=300)
        property = Property(cost=100, rent=50)

        # Run multiple times and check we get both True and False
        results = [strategy.should_buy(player, property) for _ in range(100)]

        # Should have both True and False in results (probabilistic test)
        assert True in results
        assert False in results

    def test_strategy_name(self):
        """Check strategy name."""
        strategy = RandomStrategy()
        assert strategy.get_name() == "random"
