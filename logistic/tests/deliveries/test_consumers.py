import json
import uuid
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from deliveries.consumers import GetProductsConsumer
from deliveries.schemas import DeliverySaleStatus


class TestGetProductsConsumer:

    def test_init(self):
        # Act
        consumer = GetProductsConsumer()

        # Assert
        assert consumer.queue == "logistic.send_pending_sales_to_delivery"

    @patch('deliveries.consumers.create_delivery_stops_transaction')
    @patch('deliveries.consumers.PayloadSaleSchema')
    @patch('deliveries.consumers.SessionLocal')
    def test_process_payload_success(
        self, mock_session_local, mock_payload_schema, mock_create_transaction
    ):
        # Arrange
        consumer = GetProductsConsumer()
        consumer.connection = MagicMock()
        consumer.channel = MagicMock()

        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        payload_dict = {"sales_id": str(uuid.UUID(int=0))}
        mock_sale_payload = MagicMock()
        mock_sale_payload.sales_id = payload_dict["sales_id"]
        mock_payload_schema.model_validate_json.return_value = (
            mock_sale_payload
        )

        mock_create_transaction.return_value = True

        # Act
        result = consumer.process_payload(json.dumps(payload_dict))

        # Assert
        mock_session_local.assert_called_once()
        mock_payload_schema.model_validate_json.assert_called_once_with(
            json.dumps(payload_dict)
        )
        mock_create_transaction.assert_called_once_with(
            mock_db, mock_sale_payload
        )
        mock_db.close.assert_called_once()

        result_dict = json.loads(result)
        assert result_dict["sale_id"] == payload_dict["sales_id"]
        assert result_dict["status"] == DeliverySaleStatus.SUCCESS
        assert result_dict["message"] == "Delivery items created successfully"

    @patch('deliveries.consumers.create_delivery_stops_transaction')
    @patch('deliveries.consumers.PayloadSaleSchema')
    @patch('deliveries.consumers.SessionLocal')
    def test_process_payload_failure(
        self, mock_session_local, mock_payload_schema, mock_create_transaction
    ):
        # Arrange
        consumer = GetProductsConsumer()
        consumer.connection = MagicMock()
        consumer.channel = MagicMock()
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        payload_dict = {"sales_id": str(uuid.UUID(int=0))}
        mock_sale_payload = MagicMock()
        mock_sale_payload.sales_id = payload_dict["sales_id"]
        mock_payload_schema.model_validate_json.return_value = (
            mock_sale_payload
        )

        mock_create_transaction.return_value = False

        # Act
        result = consumer.process_payload(json.dumps(payload_dict))

        # Assert
        mock_session_local.assert_called_once()
        mock_payload_schema.model_validate_json.assert_called_once_with(
            json.dumps(payload_dict)
        )
        mock_create_transaction.assert_called_once_with(
            mock_db, mock_sale_payload
        )
        mock_db.close.assert_called_once()

        result_dict = json.loads(result)
        assert result_dict["sale_id"] == payload_dict["sales_id"]
        assert result_dict["status"] == DeliverySaleStatus.ERROR
        assert result_dict["message"] == "Failed to create delivery items"

    @patch('deliveries.consumers.create_delivery_stops_transaction')
    @patch('deliveries.consumers.PayloadSaleSchema')
    @patch('deliveries.consumers.SessionLocal')
    def test_process_payload_exception(
        self, mock_session_local, mock_payload_schema, mock_create_transaction
    ):
        # Arrange
        consumer = GetProductsConsumer()
        consumer.connection = MagicMock()
        consumer.channel = MagicMock()
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        payload_dict = {"sales_id": str(uuid.UUID(int=0))}
        mock_sale_payload = MagicMock()
        mock_sale_payload.sales_id = payload_dict["sales_id"]
        mock_payload_schema.model_validate_json.return_value = (
            mock_sale_payload
        )

        mock_create_transaction.side_effect = Exception("Test exception")

        # Act
        result = consumer.process_payload(json.dumps(payload_dict))

        # Assert
        mock_session_local.assert_called_once()
        mock_payload_schema.model_validate_json.assert_called_once_with(
            json.dumps(payload_dict)
        )
        mock_create_transaction.assert_called_once_with(
            mock_db, mock_sale_payload
        )
        mock_db.close.assert_called_once()

        result_dict = json.loads(result)
        assert result_dict["sale_id"] == payload_dict["sales_id"]
        assert result_dict["status"] == DeliverySaleStatus.ERROR
        assert result_dict["message"] == "Test exception"
