import json
from unittest import mock
from uuid import UUID

import faker
import pytest
from sqlalchemy.orm import Session

from sales.consumers import CreateSaleDelivery
from sales.models import Sale, SaleDelivery

fake = faker.Faker()


@pytest.fixture(autouse=True)
def setup_db(db_session: Session):
    with mock.patch("sales.consumers.SessionLocal") as get_session:
        get_session.return_value = db_session
        yield


class TestCreateSaleDeliveryConsumer:

    @pytest.fixture
    def setup_sale(self, db_session):
        """
        Fixture to create a sale for testing.
        """
        sale = Sale(
            client_id=fake.uuid4(cast_to=None),
            seller_id=fake.uuid4(cast_to=None),
            address_id=fake.uuid4(cast_to=None),
            total_value=fake.pydecimal(left_digits=5, right_digits=2),
            currency=fake.currency_code(),
            order_number=fake.random_int(min=1, max=1000),
            status="pending",
        )
        db_session.add(sale)
        db_session.commit()
        return sale

    def test_invalid_payload(self):
        """
        Test processing an invalid payload.
        """
        consumer = CreateSaleDelivery()
        payload = {"invalid_field": "invalid_value"}  # Invalid payload

        result = consumer.process_payload(payload)

        assert "error" in result
        error = result["error"]
        assert any(
            [
                e['loc'] == ['sale_id'] and e['type'] == 'missing'
                for e in error
            ]
        )
        assert any(
            [
                e['loc'] == ['delivery_id'] and e['type'] == 'missing'
                for e in error
            ]
        )

    def test_invalid_sale_id(self):
        """
        Test processing a payload with an invalid sale ID.
        """
        consumer = CreateSaleDelivery()
        payload = {
            "sale_id": fake.uuid4(),
            "delivery_id": fake.uuid4(),
        }
        result = consumer.process_payload(payload)
        assert "error" in result
        assert result["error"][0]['msg'] == "Value error, Sale not found."

    def test_valid_delivery(self, db_session: Session, setup_sale: Sale):
        """
        Test processing a valid delivery payload.
        """
        consumer = CreateSaleDelivery()
        payload = {
            "sale_id": str(setup_sale.id),
            "delivery_id": fake.uuid4(),
        }

        result = json.loads(consumer.process_payload(payload))
        setup_sale = (
            db_session.query(Sale)
            .filter(Sale.id == UUID(payload["sale_id"]))
            .first()
        )

        assert "error" not in result
        assert result["sale_id"] == str(setup_sale.id)
        assert result["delivery_id"] == payload["delivery_id"]

        # Verify the delivery was associated with the sale
        delivery = (
            db_session.query(SaleDelivery)
            .filter_by(
                sale_id=setup_sale.id,
                delivery_id=UUID(payload["delivery_id"]),
            )
            .first()
        )
        assert delivery is not None

    def test_repeated_delivery(self, db_session, setup_sale):
        """
        Test processing a repeated delivery payload.
        """
        consumer = CreateSaleDelivery()
        delivery_id = fake.uuid4()

        # First delivery
        payload = {
            "sale_id": str(setup_sale.id),
            "delivery_id": str(delivery_id),
        }
        result = json.loads(consumer.process_payload(payload))
        assert "error" not in result

        # Repeated delivery
        result = json.loads(consumer.process_payload(payload))
        assert "error" not in result
        setup_sale = (
            db_session.query(Sale)
            .filter(Sale.id == UUID(payload["sale_id"]))
            .first()
        )
        # Verify only one delivery record exists
        deliveries = (
            db_session.query(SaleDelivery)
            .filter_by(sale_id=setup_sale.id, delivery_id=UUID(delivery_id))
            .all()
        )
        assert len(deliveries) == 1
