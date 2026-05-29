def apply_discount(
    price: float, discount_type: str, value: float
) -> float:
    """Aplica un descuento a un precio."""
    if discount_type == "percentage":
        result = price * (1 - value / 100)
    elif discount_type == "fixed":
        result = price - value
    else:
        raise ValueError(f"Tipo de descuento inválido: '{discount_type}'")

    return max(result, 0.0)