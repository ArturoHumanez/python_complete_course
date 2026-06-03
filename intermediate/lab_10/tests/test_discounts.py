import pytest
from intermediate.lab_10.discounts import apply_discount


class TestApplyDiscount:
    def test_percentage_discount(self):
        result = apply_discount(1000, "percentage", 10)
        assert result == 900.0

    def test_fixed_discount(self):
        result = apply_discount(1000, "fixed", 150)
        assert result == 850.0

    def test_discount_cannot_go_negative(self):
        result = apply_discount(100, "fixed", 200)
        assert result == 0.0

    def test_invalid_discount_type(self):
        with pytest.raises(ValueError, match="Tipo de descuento inválido"):
            apply_discount(1000, "bogus", 10)

    @pytest.mark.parametrize(
        "price, disc_type, value, expected",
        [
            (500, "percentage", 0, 500.0),
            (500, "percentage", 100, 0.0),
            (0, "fixed", 50, 0.0),
            (1000, "percentage", 50, 500.0),
        ],
    )
    def test_edge_cases(self, price, disc_type, value, expected):
        assert apply_discount(price, disc_type, value) == expected