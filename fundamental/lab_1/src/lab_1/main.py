def calcular_total(items, tax_rate=0.16):
    """calcula el total de una orden"""
    total = 0
    for i in items:
        total += i["price"] * i["quantity"]
    total_con_tax = total + (total * tax_rate)
    return total_con_tax


class order:
    def __init__(self, id, customer, items):
        self.id = id
        self.customer = customer
        self.items = items
        self.total = calcular_total(items)

    def to_dict(self):
        return {
            "id": self.id,
            "customer": self.customer,
            "total": self.total,
            "items": self.items,
        }


x = order(1, "Juan", [{"price": 100, "quantity": 2}, {"price": 50, "quantity": 1}])
print(x.to_dict())
