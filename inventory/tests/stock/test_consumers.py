import json
from typing import List
from unittest import mock
from uuid import UUID

import faker
import pytest
from sqlalchemy.orm import Session

from stock.consumers import AllocateStockConsumer
from stock.models import Stock, StockMovement
from warehouse.models import Address, Warehouse

fake = faker.Faker()


@pytest.fixture(autouse=True)
def setup_db(db_session: Session):
    with mock.patch("stock.consumers.SessionLocal") as get_session:
        get_session.return_value = db_session
        yield


@pytest.fixture
def warehouses(db_session: Session) -> List[Warehouse]:
    """
    Create a list of warehouses with addresses.
    """
    addresses = [
        Address(
            id=fake.uuid4(cast_to=None),
            street=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            postal_code=fake.postcode(),
            country=fake.country(),
            latitude=fake.latitude(),
            longitude=fake.longitude(),
        )
        for _ in range(5)
    ]
    warehouses = [
        Warehouse(
            id=fake.uuid4(cast_to=None),
            name=fake.company(),
            address_id=addresses[i].id,
            phone=fake.phone_number(),
        )
        for i in range(5)
    ]
    db_session.add_all(addresses)
    db_session.add_all(warehouses)
    db_session.commit()
    for warehouse in warehouses:
        db_session.refresh(warehouse)
    return warehouses


@pytest.fixture
def product_ids() -> List[UUID]:
    """
    Create a list of product IDs.
    """
    return [fake.uuid4(cast_to=None) for _ in range(5)]


@pytest.fixture
def stock(
    product_ids: List[UUID], warehouses: List[Warehouse], db_session: Session
) -> List[Stock]:
    """
    Create a list of stock items.
    """

    stocks = [
        Stock(
            product_id=product_id,
            warehouse_id=warehouse.id,
            quantity=fake.random_int(min=1, max=10),
        )
        for product_id in product_ids
        for warehouse in warehouses
    ]
    db_session.add_all(stocks)
    db_session.commit()
    for stock in stocks:
        db_session.refresh(stock)

    return (
        db_session.query(Stock)
        .order_by(
            Stock.product_id.asc(),
            Stock.quantity.desc(),
            Stock.warehouse_id.asc(),
        )
        .all()
    )


class TestAllocateStockConsumer:

    @pytest.fixture
    def consumer(self) -> AllocateStockConsumer:
        """
        Create an instance of the AllocateStockConsumer.
        """
        return AllocateStockConsumer()

    def test_invalid_payload(self, consumer: AllocateStockConsumer):
        """
        Test the consumer with an invalid payload.
        """
        invalid_payload = {
            "order_number": "invalid_order_number",
            "sale_id": "invalid_sale_id",
            "items": [
                {
                    "product_id": "invalid_product_id",
                    "quantity": "invalid_quantity",
                }
            ],
        }
        result = consumer.process_payload(invalid_payload)
        assert "error" in result
        assert result["code"] == "validation_error"
        errors = result["error"]
        assert any(error["loc"] == ("order_number",) for error in errors)
        assert any(error["loc"] == ("sale_id",) for error in errors)
        assert any(
            error["loc"] == ("items", 0, "product_id") for error in errors
        )
        assert any(
            error["loc"] == ("items", 0, "quantity") for error in errors
        )

    def test_not_enough_stock(
        self,
        consumer: AllocateStockConsumer,
        stock: List[Stock],
        product_ids: List[UUID],
    ):
        product_id = product_ids[0]
        total_avaliable = sum(
            [s.quantity for s in stock if s.product_id == product_id]
        )
        fake_product_id = fake.uuid4()
        other_stock = next(
            (s for s in stock if s.product_id != product_id), None
        )
        payload = {
            "order_number": 123,
            "sale_id": fake.uuid4(),
            "items": [
                # Amount to high
                {
                    "product_id": str(product_id),
                    "quantity": total_avaliable + 1,
                },
                # Invalid product
                {
                    "product_id": fake_product_id,
                    "quantity": 5,
                },
                # Correct
                {
                    "product_id": str(other_stock.product_id),
                    "quantity": other_stock.quantity,
                },
            ],
        }
        result = consumer.process_payload(payload)
        assert "error" in result
        assert result["code"] == "insufficient_stock"
        errors_by_product_ids = {
            error["product_id"]: error for error in result["error"]
        }
        # There is enough stock.
        assert str(other_stock.product_id) not in errors_by_product_ids
        assert (
            errors_by_product_ids[str(product_id)]["available_quantity"]
            == total_avaliable
        )
        assert (
            errors_by_product_ids[str(product_id)]["requested_quantity"]
            == total_avaliable + 1
        )
        assert (
            errors_by_product_ids[fake_product_id]["available_quantity"] == 0
        )
        assert (
            errors_by_product_ids[fake_product_id]["requested_quantity"] == 5
        )

    def test_reserve_stock(
        self,
        consumer: AllocateStockConsumer,
        stock: List[Stock],
        db_session: Session,
    ):
        # Save stock by product and warehouse IDs before reserving
        stocks_before = {
            (
                stock_item.product_id,
                stock_item.warehouse_id,
            ): stock_item.quantity
            for stock_item in stock
        }

        # Group stock by product and select the warehouse with
        #  the highest stock for each product
        product_to_warehouse = {}
        for (product_id, warehouse_id), _quantity in stocks_before.items():
            if product_id not in product_to_warehouse:
                product_to_warehouse[product_id] = warehouse_id

        # Prepare the payload to reserve all stock for each product
        # in its selected warehouse
        payload = {
            "order_number": 123,
            "sale_id": str(fake.uuid4()),
            "items": [
                {
                    "product_id": str(product_id),
                    "quantity": stocks_before[(product_id, warehouse_id)],
                }
                for product_id, warehouse_id in product_to_warehouse.items()
            ],
        }

        # Call the consumer to process the payload
        result = json.loads(consumer.process_payload(payload))

        # Assert the correct response is returned
        assert "error" not in result
        assert result["sale_id"] == payload["sale_id"]
        assert result["order_number"] == payload["order_number"]
        reserved_items = result["items"]
        assert len(reserved_items) == len(product_to_warehouse)

        for reserved_item in reserved_items:
            product_id = UUID(reserved_item["product_id"])
            warehouse_id = UUID(reserved_item["warehouse_id"])
            quantity_reserved = reserved_item["quantity"]

            # Assert the reserved product and warehouse match the payload
            assert product_id in product_to_warehouse
            assert warehouse_id == product_to_warehouse[product_id]
            assert (
                quantity_reserved == stocks_before[(product_id, warehouse_id)]
            )

        # Query the database to check stock after reservation
        stocks_after = {
            (
                stock_item.product_id,
                stock_item.warehouse_id,
            ): stock_item.quantity
            for stock_item in db_session.query(Stock).all()
        }

        # Assert stock is reserved in the correct warehouses
        for product_id, warehouse_id in product_to_warehouse.items():
            assert stocks_after[(product_id, warehouse_id)] == 0
            # There is a stock movemen
            assert (
                db_session.query(StockMovement)
                .filter(
                    StockMovement.stock_product_id == product_id,
                    StockMovement.stock_warehouse_id == warehouse_id,
                    StockMovement.quantity
                    == stocks_before[(product_id, warehouse_id)],
                )
                .count()
                == 1
            )

        # Assert stock in other warehouses remains unchanged
        for (prod_id, wh_id), quantity_before in stocks_before.items():
            if (prod_id, wh_id) not in product_to_warehouse.items():
                assert stocks_after[(prod_id, wh_id)] == quantity_before

    def test_reseve_stock_across_several_warehouses(
        self,
        consumer: AllocateStockConsumer,
        stock: List[Stock],
        db_session: Session,
    ):
        # Reserve across several warehouses
        stocks = [stock[0], stock[5], stock[10], stock[3], stock[8], stock[13]]
        per_product = {str(stock_item.product_id): 0 for stock_item in stocks}
        for stock_item in stocks:
            per_product[str(stock_item.product_id)] += stock_item.quantity

        payload = {
            "order_number": 123,
            "sale_id": str(fake.uuid4()),
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
                for product_id, quantity in per_product.items()
            ],
        }

        # Call the consumer to process the payload
        result = json.loads(consumer.process_payload(payload))

        # Assert the correct response is returned
        assert "error" not in result
        assert result["sale_id"] == payload["sale_id"]
        assert result["order_number"] == payload["order_number"]
        reserved_items = result["items"]
        assert len(reserved_items) == len(stocks)

        total_reserved_per_product = {
            reserved_item["product_id"]: {
                'total_reserved': 0,
                'warehouses_ids': [],
            }
            for reserved_item in reserved_items
        }
        for reserved_item in reserved_items:
            product_id = reserved_item["product_id"]
            quantity_reserved = reserved_item["quantity"]
            total_reserved_per_product[product_id][
                'total_reserved'
            ] += quantity_reserved
            total_reserved_per_product[product_id]['warehouses_ids'].append(
                reserved_item["warehouse_id"]
            )
        for product_id, item in total_reserved_per_product.items():
            assert item['total_reserved'] == per_product[product_id]
            assert len(item['warehouses_ids']) > 1
