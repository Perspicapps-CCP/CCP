import uuid

import faker

from sales import mappers
from sales.models import Sale, SaleItem
from sales.schemas import SaleDetailSchema

fake = faker.Faker()


def test_sale_to_schema():
    """
    Test the sale_to_schema function.
    """
    # Create a mock Sale object
    sale_id = uuid.uuid4()
    sale = Sale(
        id=sale_id,
        seller_id=uuid.uuid4(),
        order_number=fake.random_int(min=1000, max=9999),
        address_id=uuid.uuid4(),
        total_value=fake.pydecimal(
            left_digits=5, right_digits=2, positive=True
        ),
        currency="USD",
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
        items=[
            SaleItem(
                id=uuid.uuid4(),
                sale_id=sale_id,
                product_id=uuid.uuid4(),
                quantity=fake.random_int(min=1, max=10),
                unit_price=fake.pydecimal(
                    left_digits=3, right_digits=2, positive=True
                ),
                total_value=fake.pydecimal(
                    left_digits=4, right_digits=2, positive=True
                ),
                created_at=fake.date_time(),
                updated_at=fake.date_time(),
            )
            for _ in range(2)
        ],
    )

    # Call the function to test
    result = mappers.sale_to_schema(sale)

    # Assert the result is of type SaleDetailSchema
    assert isinstance(result, SaleDetailSchema)
    assert result.id == sale.id
    assert result.order_number == sale.order_number
    assert result.total_value == sale.total_value
    assert result.currency == sale.currency
    assert len(result.items) == len(sale.items)
    for i, item in enumerate(result.items):
        assert item.id == sale.items[i].id
        assert item.product.id == sale.items[i].product_id
        assert item.quantity == sale.items[i].quantity
        assert item.unit_price == sale.items[i].unit_price
        assert item.total_value == sale.items[i].total_value
