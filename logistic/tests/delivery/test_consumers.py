import copy
import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from delivery.consumers import GetProductsConsumer
from delivery.schemas import DeliverySaleStatus
from sqlalchemy.orm import Session


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
        consumer = GetProductsConsumer()

        # Assert
        assert consumer.queue == "logistic.send_pending_sales_to_delivery"

    @patch("delivery.consumers.create_delivery_stops_transaction")
    @patch("delivery.consumers.SessionLocal")
    def test_process_payload_success(
        self, mock_session_local, mock_create_transaction, payload_dict
    ):
        # Arrange
        consumer = GetProductsConsumer()
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
        consumer = GetProductsConsumer()
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
        assert result_dict["sale_id"] == None
        assert result_dict["status"] == DeliverySaleStatus.ERROR
        assert "sales_id" in result_dict["message"]

    @patch("delivery.consumers.create_delivery_stops_transaction")
    @patch("delivery.consumers.SessionLocal")
    def test_process_payload_exception(
        self, mock_session_local, mock_create_transaction, payload_dict
    ):
        # Arrange
        consumer = GetProductsConsumer()
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
