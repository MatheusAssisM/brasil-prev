import pytest
from app.domain.value_objects import Money, Position


@pytest.mark.unit
class TestMoney:
    """Test Money value object."""

    def test_money_creation(self):
        """Test creating Money instance."""
        money = Money(100)
        assert money.amount == 100
        assert int(money) == 100

    def test_money_add(self):
        """Test adding Money instances."""
        m1 = Money(100)
        m2 = Money(50)
        result = m1.add(m2)
        assert result.amount == 150

    def test_money_add_int(self):
        """Test adding int to Money."""
        m1 = Money(100)
        result = m1.add(50)
        assert result.amount == 150

    def test_money_subtract(self):
        """Test subtracting Money instances."""
        m1 = Money(100)
        m2 = Money(30)
        result = m1.subtract(m2)
        assert result.amount == 70

    def test_money_subtract_int(self):
        """Test subtracting int from Money."""
        m1 = Money(100)
        result = m1.subtract(30)
        assert result.amount == 70

    def test_money_is_positive(self):
        """Test is_positive method."""
        assert Money(100).is_positive() is True
        assert Money(0).is_positive() is False
        assert Money(-10).is_positive() is False

    def test_money_is_negative(self):
        """Test is_negative method."""
        assert Money(-10).is_negative() is True
        assert Money(0).is_negative() is False
        assert Money(10).is_negative() is False

    def test_money_is_zero(self):
        """Test is_zero method."""
        assert Money(0).is_zero() is True
        assert Money(10).is_zero() is False
        assert Money(-10).is_zero() is False

    def test_money_is_sufficient_for(self):
        """Test is_sufficient_for method."""
        m = Money(100)
        assert m.is_sufficient_for(Money(50)) is True
        assert m.is_sufficient_for(100) is True
        assert m.is_sufficient_for(Money(150)) is False
        assert m.is_sufficient_for(200) is False

    def test_money_comparisons(self):
        """Test Money comparison operators."""
        m1 = Money(100)
        m2 = Money(50)
        m3 = Money(100)

        assert m1 > m2
        assert m1 >= m2
        assert m1 >= m3
        assert m2 < m1
        assert m2 <= m1
        assert m1 <= m3

        assert m1 > 50
        assert m1 >= 100
        assert m2 < 100

    def test_money_str_repr(self):
        """Test string representations."""
        m = Money(100)
        assert str(m) == "$100"
        assert repr(m) == "Money(amount=100)"

    def test_money_invalid_type_add(self):
        """Test adding invalid type raises error."""
        m = Money(100)
        with pytest.raises(TypeError):
            m.add("invalid")  # type: ignore

    def test_money_invalid_type_subtract(self):
        """Test subtracting invalid type raises error."""
        m = Money(100)
        with pytest.raises(TypeError):
            m.subtract("invalid")  # type: ignore

    def test_money_invalid_type_comparison(self):
        """Test comparing with invalid type."""
        m = Money(100)
        with pytest.raises(TypeError):
            m.is_sufficient_for("invalid")  # type: ignore

    def test_money_non_int_creation(self):
        """Test creating Money with non-int raises error."""
        with pytest.raises(TypeError):
            Money("100")  # type: ignore


@pytest.mark.unit
class TestPosition:
    """Test Position value object."""

    def test_position_creation(self):
        """Test creating Position instance."""
        pos = Position(5)
        assert pos.value == 5
        assert int(pos) == 5

    def test_position_move_simple(self):
        """Test simple movement without wraparound."""
        pos = Position(5)
        new_pos, completed = pos.move(3, 20)
        assert new_pos.value == 8
        assert completed is False

    def test_position_move_with_wraparound(self):
        """Test movement with board wraparound."""
        pos = Position(18)
        new_pos, completed = pos.move(5, 20)
        assert new_pos.value == 3  # (18 + 5) % 20
        assert completed is True

    def test_position_move_exact_wraparound(self):
        """Test movement that exactly completes one round."""
        pos = Position(0)
        new_pos, completed = pos.move(20, 20)
        assert new_pos.value == 0
        assert completed is True

    def test_position_negative_raises_error(self):
        """Test creating Position with negative value raises error."""
        with pytest.raises(ValueError):
            Position(-1)

    def test_position_non_int_raises_error(self):
        """Test creating Position with non-int raises error."""
        with pytest.raises(TypeError):
            Position("5")  # type: ignore

    def test_position_move_invalid_steps(self):
        """Test moving with invalid steps raises error."""
        pos = Position(5)
        with pytest.raises(ValueError):
            pos.move(0, 20)
        with pytest.raises(ValueError):
            pos.move(-1, 20)

    def test_position_move_invalid_board_size(self):
        """Test moving with invalid board size raises error."""
        pos = Position(5)
        with pytest.raises(ValueError):
            pos.move(3, 0)
        with pytest.raises(ValueError):
            pos.move(3, -10)

    def test_position_str_repr(self):
        """Test string representations."""
        pos = Position(10)
        assert str(pos) == "Position(10)"
        assert repr(pos) == "Position(value=10)"
