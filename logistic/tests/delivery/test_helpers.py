import uuid

from delivery import helpers
from delivery.schemas import (
    PayloadAddressSchema,
    PayloadSaleItemSchema,
    PayloadSaleSchema,
)
from faker import Faker

fake = Faker()
fake.seed_instance(123)


def fake_address():
    return PayloadAddressSchema(
        id=uuid.uuid4(),
        street=fake.address(),
        city=fake.city(),
        state=fake.state(),
        postal_code=fake.postcode(),
        country=fake.country(),
    )


def test_group_items_by_warehouse_empty_list():
    """
    Test grouping items when there are no items.
    """
    dummy_address = fake_address()

    # Create a sale with no items
    sale = PayloadSaleSchema(
        sales_id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        order_number=1,
        address=dummy_address,
        sales_items=[],
    )

    # Call the function
    result = helpers.group_items_by_warehouse(sale)

    # Verify result is an empty dict
    assert result == {}


def test_group_items_by_warehouse_single_warehouse():
    """
    Test grouping items when all items are from the same warehouse.
    """
    dummy_address = fake_address()

    warehouse_id = uuid.UUID("11111111-1234-5678-1234-567812345678")
    sale = PayloadSaleSchema(
        sales_id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        order_number=1,
        address=dummy_address,
        sales_items=[
            PayloadSaleItemSchema(
                sales_item_id=uuid.UUID(int=0),
                product_id=uuid.UUID("aaaaaaaa-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id,
                quantity=fake.random_int(min=1, max=10),
            ),
            PayloadSaleItemSchema(
                sales_item_id=uuid.UUID(int=0),
                product_id=uuid.UUID("bbbbbbbb-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id,
                quantity=fake.random_int(min=1, max=10),
            ),
        ],
    )

    # Call the function
    result = helpers.group_items_by_warehouse(sale)

    # Verify result contains the single warehouse and all items
    assert len(result) == 1
    assert warehouse_id in result
    assert len(result[warehouse_id]) == 2
    assert result[warehouse_id][0].product_id == uuid.UUID(
        "aaaaaaaa-1234-5678-1234-567812345678"
    )
    assert result[warehouse_id][1].product_id == uuid.UUID(
        "bbbbbbbb-1234-5678-1234-567812345678"
    )


def test_group_items_by_warehouse_multiple_warehouses():
    """
    Test grouping items when items are from multiple warehouses.
    """
    dummy_address = fake_address()
    # Create a sale with items from multiple warehouses
    warehouse_id1 = uuid.UUID("11111111-1234-5678-1234-567812345678")
    warehouse_id2 = uuid.UUID("22222222-1234-5678-1234-567812345678")

    sale = PayloadSaleSchema(
        sales_id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        order_number=1,
        address=dummy_address,
        sales_items=[
            PayloadSaleItemSchema(
                sales_item_id=uuid.UUID(int=0),
                product_id=uuid.UUID("aaaaaaaa-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id1,
                quantity=fake.random_int(min=1, max=10),
            ),
            PayloadSaleItemSchema(
                sales_item_id=uuid.UUID(int=0),
                product_id=uuid.UUID("bbbbbbbb-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id2,
                quantity=fake.random_int(min=1, max=10),
            ),
            PayloadSaleItemSchema(
                sales_item_id=uuid.UUID(int=0),
                product_id=uuid.UUID("cccccccc-1234-5678-1234-567812345678"),
                warehouse_id=warehouse_id1,
                quantity=fake.random_int(min=1, max=10),
            ),
        ],
    )

    # Call the function
    result = helpers.group_items_by_warehouse(sale)

    # Verify result contains both warehouses with correct items
    assert len(result) == 2
    assert warehouse_id1 in result
    assert warehouse_id2 in result

    # Verify warehouse_id1 has two items with correct product IDs
    assert len(result[warehouse_id1]) == 2
    assert result[warehouse_id1][0].product_id == uuid.UUID(
        "aaaaaaaa-1234-5678-1234-567812345678"
    )
    assert result[warehouse_id1][1].product_id == uuid.UUID(
        "cccccccc-1234-5678-1234-567812345678"
    )

    # Verify warehouse_id2 has one item with correct product ID
    assert len(result[warehouse_id2]) == 1
    assert result[warehouse_id2][0].product_id == uuid.UUID(
        "bbbbbbbb-1234-5678-1234-567812345678"
    )


def test_group_stops_by_warehouse_empty_list():
    """
    Test grouping stops when there are no pending delivery stops.
    """
    # Empty list of pending delivery stops
    pending_delivery_stops = []

    # Call the function
    result = helpers.group_stops_by_warehouse(pending_delivery_stops)

    # Verify result is an empty dict
    assert result == {}


def test_group_stops_by_warehouse_single_warehouse():
    """
    Test grouping stops when all stops are from the same warehouse.
    """
    # Create pending delivery stops with a single warehouse
    warehouse_id = uuid.UUID("11111111-1234-5678-1234-567812345678")
    stop_id1 = uuid.UUID("aaaaaaaa-1234-5678-1234-567812345678")
    stop_id2 = uuid.UUID("bbbbbbbb-1234-5678-1234-567812345678")
    sales_id = uuid.UUID("99999999-1234-5678-1234-567812345678")

    pending_delivery_stops = [
        (stop_id1, sales_id, warehouse_id),
        (stop_id2, sales_id, warehouse_id),
    ]

    # Call the function
    result = helpers.group_stops_by_warehouse(pending_delivery_stops)

    # Verify result contains the single warehouse and all stops
    assert len(result) == 1
    assert warehouse_id in result
    assert len(result[warehouse_id]) == 2
    assert stop_id1 in result[warehouse_id]
    assert stop_id2 in result[warehouse_id]


def test_group_stops_by_warehouse_multiple_warehouses():
    """
    Test grouping stops when stops are from multiple warehouses.
    """
    # Create pending delivery stops from multiple warehouses
    warehouse_id1 = uuid.UUID("11111111-1234-5678-1234-567812345678")
    warehouse_id2 = uuid.UUID("22222222-1234-5678-1234-567812345678")

    stop_id1 = uuid.UUID("aaaaaaaa-1234-5678-1234-567812345678")
    stop_id2 = uuid.UUID("bbbbbbbb-1234-5678-1234-567812345678")
    stop_id3 = uuid.UUID("cccccccc-1234-5678-1234-567812345678")

    sales_id = uuid.UUID("99999999-1234-5678-1234-567812345678")

    pending_delivery_stops = [
        (stop_id1, sales_id, warehouse_id1),
        (stop_id2, sales_id, warehouse_id2),
        (stop_id3, sales_id, warehouse_id1),
    ]

    # Call the function
    result = helpers.group_stops_by_warehouse(pending_delivery_stops)

    # Verify result contains both warehouses with correct stops
    assert len(result) == 2
    assert warehouse_id1 in result
    assert warehouse_id2 in result

    # Verify warehouse_id1 has two stops
    assert len(result[warehouse_id1]) == 2
    assert stop_id1 in result[warehouse_id1]
    assert stop_id3 in result[warehouse_id1]

    # Verify warehouse_id2 has one stop
    assert len(result[warehouse_id2]) == 1
    assert stop_id2 in result[warehouse_id2]


def test_group_stops_by_warehouse_preserve_order():
    """
    Test that the order of stops is preserved within each warehouse group.
    """
    # Create pending delivery stops with specific order
    warehouse_id = uuid.UUID("11111111-1234-5678-1234-567812345678")
    stop_id1 = uuid.UUID("aaaaaaaa-1234-5678-1234-567812345678")
    stop_id2 = uuid.UUID("bbbbbbbb-1234-5678-1234-567812345678")
    stop_id3 = uuid.UUID("cccccccc-1234-5678-1234-567812345678")
    sales_id = uuid.UUID("99999999-1234-5678-1234-567812345678")

    pending_delivery_stops = [
        (stop_id1, sales_id, warehouse_id),
        (stop_id2, sales_id, warehouse_id),
        (stop_id3, sales_id, warehouse_id),
    ]

    # Call the function
    result = helpers.group_stops_by_warehouse(pending_delivery_stops)

    # Verify the order is preserved
    assert result[warehouse_id] == [stop_id1, stop_id2, stop_id3]
