from typing import Dict


class InsufficientStockToAllocateException(Exception):
    """Exception raised when there is not enough stock to allocate."""

    def __init__(self, available_stock: Dict, requested_stock: Dict):
        self.available_stock = available_stock
        self.requested_stock = requested_stock
        super().__init__("Not enough stock to allocate")

    def errors(self):
        errors = []

        for product_id, requested_quantity in self.requested_stock.items():
            available_quantity = self.available_stock.get(product_id, 0)
            if requested_quantity > available_quantity:
                errors.append(
                    {
                        "product_id": str(product_id),
                        "available_quantity": available_quantity,
                        "requested_quantity": requested_quantity,
                    }
                )
        return errors
