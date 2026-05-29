from hypothesis import given, strategies as st

from intermediate.lab_10.discounts import apply_discount


class TestDiscountProperties:
    @given(
        price=st.floats(min_value=0, max_value=1_000_000),
        percentage=st.floats(min_value=0, max_value=100),
    )
    def test_percentage_never_negative(self, price, percentage):
        """El resultado nunca puede ser negativo."""
        result = apply_discount(price, "percentage", percentage)
        assert result >= 0

    @given(
        price=st.floats(min_value=0, max_value=1_000_000),
        discount=st.floats(min_value=0, max_value=1_000_000),
    )
    def test_fixed_never_negative(self, price, discount):
        """El resultado nunca puede ser negativo."""
        result = apply_discount(price, "fixed", discount)
        assert result >= 0

    @given(price=st.floats(min_value=0, max_value=1_000_000))
    def test_zero_discount_returns_same_price(self, price):
        """Un descuento de 0% no cambia el precio."""
        result = apply_discount(price, "percentage", 0)
        assert result == price

    @given(price=st.floats(min_value=0, max_value=1_000_000))
    def test_full_discount_returns_zero(self, price):
        """Un descuento de 100% da cero."""
        result = apply_discount(price, "percentage", 100)
        assert result == 0.0