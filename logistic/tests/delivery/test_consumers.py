import copy
import datetime
import json
import uuid
from typing import List
from unittest import mock
from unittest.mock import MagicMock, patch

import faker
import pytest
from sqlalchemy.orm import Session

from delivery.consumers import (
    CreateDeliveryStopsConsumer,
    GetDeliveriesConsumer,
)
from delivery.models import Delivery, DeliveryAddress, DeliveryStop, Driver
from delivery.schemas import DeliverySaleStatus
from rpc_clients.schemas import ProductSchema

fake = faker.Faker()


@pytest.fixture
def payload_dict():
    return {
        "sales_id": str(uuid.UUID(int=0)),
        "order_number": 123,
        "address": {
            "id": str(uuid.UUID(int=0)),
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "12345",
            "country": "USA",
        },
        "sales_items": [],
    }


class TestGetProductsConsumer:

    def test_init(self):
        # Act
        consumer = CreateDeliveryStopsConsumer()

        # Assert
        assert consumer.queue == "logistic.send_pending_sales_to_delivery"

    @patch("delivery.consumers.create_delivery_stops_transaction")
    @patch("delivery.consumers.SessionLocal")
    def test_process_payload_success(
        self, mock_session_local, mock_create_transaction, payload_dict
    ):
        # Arrange
        consumer = CreateDeliveryStopsConsumer()
        consumer.connection = MagicMock()
        consumer.channel = MagicMock()

        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db
        mock_create_transaction.return_value = True

        # Act
        result = consumer.process_payload(payload_dict)

        # Assert
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()

        result_dict = json.loads(result)
        assert result_dict["sale_id"] == payload_dict["sales_id"]
        assert result_dict["status"] == DeliverySaleStatus.SUCCESS
        assert result_dict["message"] == "Delivery items created successfully"

    @patch("delivery.consumers.create_delivery_stops_transaction")
    @patch("delivery.consumers.SessionLocal")
    def test_process_payload_failure(
        self, mock_session_local, mock_create_transaction, payload_dict
    ):
        # Arrange
        consumer = CreateDeliveryStopsConsumer()
        consumer.connection = MagicMock()
        consumer.channel = MagicMock()
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_sale_payload = MagicMock()
        mock_sale_payload.sales_id = payload_dict["sales_id"]
        mock_create_transaction.return_value = False

        # Act
        payload_dict = copy.deepcopy(payload_dict)
        del payload_dict["sales_id"]
        result = consumer.process_payload(payload_dict)

        # Assert
        mock_session_local.assert_called_once()

        mock_create_transaction.assert_not_called()

        result_dict = json.loads(result)
        assert result_dict["sale_id"] is None
        assert result_dict["status"] == DeliverySaleStatus.ERROR
        assert "sales_id" in result_dict["message"]

    @patch("delivery.consumers.create_delivery_stops_transaction")
    @patch("delivery.consumers.SessionLocal")
    def test_process_payload_exception(
        self, mock_session_local, mock_create_transaction, payload_dict
    ):
        # Arrange
        consumer = CreateDeliveryStopsConsumer()
        consumer.connection = MagicMock()
        consumer.channel = MagicMock()
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_sale_payload = MagicMock()
        mock_sale_payload.sales_id = payload_dict["sales_id"]

        mock_create_transaction.side_effect = Exception("Test exception")

        # Act
        result = consumer.process_payload(payload_dict)

        # Assert
        mock_session_local.assert_called_once()

        mock_create_transaction.assert_called_once()
        mock_db.close.assert_called_once()

        result_dict = json.loads(result)
        assert result_dict["sale_id"] == payload_dict["sales_id"]
        assert result_dict["status"] == DeliverySaleStatus.ERROR
        assert result_dict["message"] == "Test exception"


def generate_fake_products(product_ids) -> List[ProductSchema]:
    """
    Generate fake products for testing.
    """
    return [
        ProductSchema(
            **{
                "id": id,
                "product_code": str(fake.random_int(min=1000, max=9999)),
                "name": fake.word(),
                "price": fake.random_number(digits=5),
                "images": [fake.image_url() for _ in range(3)],
                "manufacturer": {
                    "id": fake.uuid4(),
                    "manufacturer_name": fake.company(),
                },
            }
        )
        for id in product_ids
    ]


class TestGetDeliveriesConsumer:

    @pytest.fixture(autouse=True)
    def mock_rabbitmq_client(self, request):
        """
        Mock the RabbitMQ client (pika) to avoid actual RabbitMQ calls.
        """
        if request.node.get_closest_marker("skip_mock_rabbitmq"):
            yield  # Skip the fixture
            return

        # Mock the pika connection and channel
        mock_connection = mock.MagicMock()
        mock_channel = mock.MagicMock()

        # Mock pika.BlockingConnection to return the mock connection
        with mock.patch(
            "pika.BlockingConnection", return_value=mock_connection
        ):
            # Mock the connection.channel() to return the mock channel
            mock_connection.channel.return_value = mock_channel
            yield mock_channel

    @pytest.fixture
    def consumer(self) -> GetDeliveriesConsumer:
        """
        Fixture to create a mock consumer instance.
        """
        consumer = GetDeliveriesConsumer()
        consumer.connection = MagicMock()
        consumer.channel = MagicMock()
        return consumer

    @pytest.fixture(autouse=True)
    def mock_suppliers_rpc_client(self, request):
        """
        Mock the SuppliersClient to avoid actual RPC calls.
        """
        if request.node.get_closest_marker("skip_mock_suppliers"):
            yield  # Skip the fixture
            return

        def get_products(_self, product_ids):
            if product_ids is None:
                product_ids = [uuid.uuid4() for _ in range(5)]
            return generate_fake_products(product_ids)

        with mock.patch(
            "rpc_clients.suppliers_client.SuppliersClient.get_products",
            side_effect=get_products,
            autospec=True,
        ):
            yield

    @pytest.fixture(autouse=True)
    def setup_method(self, db_session: Session):
        """
        Setup method to create a mock database session.
        """

        with (
            patch("delivery.consumers.SessionLocal") as get_session,
            patch(
                "delivery.consumers.InventoryClient"
            ) as mock_inventory_client,
        ):
            get_session.return_value = db_session
            mock_warehouse = MagicMock()
            mock_warehouse.warehouse_id = 1
            mock_warehouse.latitude = 0.0
            mock_warehouse.longitude = 0.0
            mock_inventory_client.return_value.get_warehouses.return_value = [
                mock_warehouse
            ]
            yield get_session

    @pytest.fixture
    def deliveries_in_db(self, db_session: Session) -> List[Delivery]:
        address = DeliveryAddress(
            id=fake.uuid4(cast_to=None),
            street=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            postal_code=fake.postcode(),
            country=fake.country(),
            latitude=fake.latitude(),
            longitude=fake.longitude(),
        )
        db_session.add(address)
        db_session.commit()

        driver = Driver(
            id=fake.uuid4(cast_to=None),
            name=fake.name(),
            license_plate=fake.license_plate(),
            phone_number=fake.phone_number(),
        )
        db_session.add(driver)
        db_session.commit()

        deliveries = []
        date = datetime.datetime.now()
        for i in range(3):
            deliveries.append(
                Delivery(
                    id=fake.uuid4(cast_to=None),
                    warehouse_id=fake.uuid4(cast_to=None),
                    driver_id=driver.id,
                    status="CREATED",
                    delivery_date=date + datetime.timedelta(days=i + 1),
                )
            )
        db_session.add_all(deliveries)
        db_session.commit()

        for delivery in deliveries:
            stops = [
                DeliveryStop(
                    id=fake.uuid4(cast_to=None),
                    sales_id=fake.uuid4(cast_to=None),
                    order_number=fake.random_int(min=1, max=1000),
                    address_id=address.id,
                    order_stop=i,
                    delivery_id=delivery.id,
                )
                for i in range(3)
            ]
            db_session.add_all(stops)
            db_session.commit()
        return db_session.query(Delivery).all()

    def test_invalid_payload(self, consumer: GetDeliveriesConsumer):
        """
        Test GetSellersConsumer with an invalid payload.
        """
        invalid_payload = {"invalid_key": "invalid_value"}

        response = consumer.process_payload(invalid_payload)

        assert "error" in response
        assert isinstance(
            response["error"], list
        )  # Validation errors are returned as a list
        assert response["error"][0]["loc"] == ("deliveries_ids",)
        assert response["error"][0]["msg"] == "Field required"

    def test_valid_payload(
        self,
        db_session: Session,
        deliveries_in_db: list[Delivery],
        consumer: GetDeliveriesConsumer,
    ):
        """
        Test GetSellersConsumer with a valid payload and verify the data.
        """
        select_deliveries = deliveries_in_db[:2]  # Select first two deliveries

        # Prepare a valid payload with deliveries IDs
        deliveries_ids = [str(delivery.id) for delivery in select_deliveries]
        valid_payload = {"deliveries_ids": deliveries_ids}

        # Parse the JSON response
        sellers_data = consumer.process_payload(valid_payload)
        sellers_data = json.loads(sellers_data)

        assert "deliveries" in sellers_data
        sellers_data = sellers_data["deliveries"]

        assert len(sellers_data) == len(select_deliveries)
