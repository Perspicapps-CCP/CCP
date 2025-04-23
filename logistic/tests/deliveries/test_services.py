import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from uuid import UUID, uuid4
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from deliveries import models, schemas

from deliveries.services import (
    get_orders_pending_to_delivery,
    get_driver_available,
    create_driver,
    create_delivery_items,
    create_order_delivery,
    update_delivery_items,
    update_driver_on_delivery,
    create_delivery_transaction,
)


class TestServices(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.sample_uuid = uuid4()
        self.current_date = datetime.now()

    def test_get_pending_delivery_orders(self):
        # Mock setup
        warehouse1_id = uuid4()
        warehouse2_id = uuid4()
        sale1_id = uuid4()
        sale2_id = uuid4()
        sale3_id = uuid4()
        
        mock_items = [
            MagicMock(sales_id=sale1_id, warehouse_id=warehouse1_id),
            MagicMock(sales_id=sale2_id, warehouse_id=warehouse1_id),
            MagicMock(sales_id=sale3_id, warehouse_id=warehouse2_id),
        ]
        
        self.db.query.return_value.distinct.return_value.filter.return_value.all.return_value = mock_items
        
        # Execute
        result = get_orders_pending_to_delivery(self.db)
        
        # Assert
        expected = {
            warehouse1_id: [sale1_id, sale2_id],
            warehouse2_id: [sale3_id]
        }
        self.assertEqual(result, expected)
        self.db.query.assert_called_once()

    def test_get_driver_available(self):
        # Mock setup
        mock_driver = MagicMock()
        self.db.query.return_value.outerjoin.return_value.filter.return_value.first.return_value = mock_driver
        
        # Execute
        result = get_driver_available(self.db, self.current_date)
        
        # Assert
        self.assertEqual(result, mock_driver)
        self.db.query.assert_called_once_with(models.Driver)

    def test_create_driver(self):
        # Mock setup
        driver_data = schemas.DriverCreateSchema(
            driver_name="John Doe",
            license_plate="ABC123",
            phone_number="1234567890"
        )
        
        # Execute
        result = create_driver(self.db, driver_data)
        
        # Assert
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
        self.assertEqual(result.name, "John Doe")
        self.assertEqual(result.license_plate, "ABC123")
        self.assertEqual(result.phone_number, "1234567890")

    def test_create_delivery_items_success(self):
        # Mock setup
        sale_id = uuid4()
        address_id = uuid4()
        order_number = 123
        
        sale_data = schemas.PayloadSaleSchema(
            sales_id=sale_id,
            order_number=order_number,
            address_id=address_id,
            sales_items=[
                MagicMock(product_id=uuid4(), warehouse_id=uuid4()),
                MagicMock(product_id=uuid4(), warehouse_id=uuid4())
            ]
        )
        
        # Execute
        result = create_delivery_items(self.db, sale_data)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(self.db.add.call_count, 2)
        self.db.commit.assert_called_once()

    @patch('deliveries.services.print')
    def test_create_delivery_items_integrity_error_unique_violation(self, mock_print):
        # Mock setup
        sale_data = schemas.PayloadSaleSchema(
            sales_id=uuid4(),
            order_number="ORD-123",
            address_id=uuid4(),
            sales_items=[MagicMock(product_id=uuid4(), warehouse_id=uuid4())]
        )
        
        # Set up a unique violation error
        unique_violation = UniqueViolation()
        unique_violation.diag = MagicMock()
        unique_violation.diag.message_detail = "Key already exists"
        integrity_error = IntegrityError("statement", "params", unique_violation)
        
        self.db.commit.side_effect = integrity_error
        
        # Execute
        result = create_delivery_items(self.db, sale_data)
        
        # Assert
        self.assertTrue(result)
        self.db.rollback.assert_called_once()
        mock_print.assert_called_once()

    @patch('deliveries.services.print')
    def test_create_delivery_items_other_integrity_error(self, mock_print):
        # Mock setup
        sale_data = schemas.PayloadSaleSchema(
            sales_id=uuid4(),
            order_number="ORD-123",
            address_id=uuid4(),
            sales_items=[MagicMock(product_id=uuid4(), warehouse_id=uuid4())]
        )
        
        integrity_error = IntegrityError("statement", "params", Exception("Other integrity error"))
        self.db.commit.side_effect = integrity_error
        
        # Execute
        result = create_delivery_items(self.db, sale_data)
        
        # Assert
        self.assertFalse(result)
        self.db.rollback.assert_called_once()
        mock_print.assert_called_once()

    @patch('deliveries.services.print')
    def test_create_delivery_items_general_exception(self, mock_print):
        # Mock setup
        sale_data = schemas.PayloadSaleSchema(
            sales_id=uuid4(),
            order_number="ORD-123",
            address_id=uuid4(),
            sales_items=[MagicMock(product_id=uuid4(), warehouse_id=uuid4())]
        )
        
        self.db.commit.side_effect = Exception("General error")
        
        # Execute
        result = create_delivery_items(self.db, sale_data)
        
        # Assert
        self.assertFalse(result)
        self.db.rollback.assert_called_once()
        mock_print.assert_called_once()

    def test_add_delivery(self):
        # Mock setup
        warehouse_id = uuid4()
        mock_delivery = MagicMock()
        self.db.flush.return_value = None
        self.db.refresh.return_value = None
        
        # Execute
        with patch('deliveries.services.models.Delivery', return_value=mock_delivery):
            result = create_order_delivery(self.db, warehouse_id)
        
        # Assert
        self.assertEqual(result, mock_delivery)
        self.db.add.assert_called_once_with(mock_delivery)
        self.db.flush.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_delivery)

    @patch('deliveries.services.update')
    def test_update_delivery_items(self, mock_update):
        # Mock setup
        delivery_id = uuid4()
        warehouse_id = uuid4()
        sales_orders = [uuid4(), uuid4()]
        
        mock_result = MagicMock()
        mock_result.rowcount = 2
        self.db.execute.return_value = mock_result
        
        # Execute
        result = update_delivery_items(self.db, delivery_id, sales_orders, warehouse_id)
        
        # Assert
        self.assertEqual(result, 2)
        self.db.execute.assert_called_once()

    @patch('deliveries.services.update')
    def test_update_driver_on_delivery_success(self, mock_update):
        # Mock setup
        delivery_id = uuid4()
        driver_id = uuid4()
        delivery_date = self.current_date
        
        mock_result = MagicMock()
        mock_result.rowcount = 1
        self.db.execute.return_value = mock_result
        
        # Execute
        result = update_driver_on_delivery(self.db, delivery_id, driver_id, delivery_date)
        
        # Assert
        self.assertTrue(result)
        self.db.commit.assert_called_once()

    @patch('deliveries.services.update')
    def test_update_driver_on_delivery_no_rows_affected(self, mock_update):
        # Mock setup
        mock_result = MagicMock()
        mock_result.rowcount = 0
        self.db.execute.return_value = mock_result
        
        # Execute
        result = update_driver_on_delivery(self.db, uuid4(), uuid4(), self.current_date)
        
        # Assert
        self.assertFalse(result)
        self.db.rollback.assert_called_once()
        self.db.commit.assert_not_called()

    @patch('deliveries.services.print')
    @patch('deliveries.services.update')
    def test_update_driver_on_delivery_exception(self, mock_update, mock_print):
        # Mock setup
        self.db.execute.side_effect = Exception("Database error")
        
        # Execute
        result = update_driver_on_delivery(self.db, uuid4(), uuid4(), self.current_date)
        
        # Assert
        self.assertFalse(result)
        self.db.rollback.assert_called_once()
        mock_print.assert_called_once()

    @patch('deliveries.services.get_pending_delivery_orders')
    def test_create_delivery_transaction_no_pending_orders(self, mock_get_pending):
        # Mock setup
        mock_get_pending.return_value = {}
        
        # Execute
        result = create_delivery_transaction(self.db)
        
        # Assert
        self.assertIsNone(result)

    @patch('deliveries.services.update_delivery_items')
    @patch('deliveries.services.add_delivery')
    @patch('deliveries.services.get_pending_delivery_orders')
    def test_create_delivery_transaction_success(self, mock_get_pending, mock_add, mock_update_items):
        # Mock setup
        warehouse_id = uuid4()
        sales_orders = [uuid4(), uuid4()]
        
        mock_get_pending.return_value = {warehouse_id: sales_orders}
        
        mock_delivery = MagicMock()
        mock_delivery.id = uuid4()
        mock_add.return_value = mock_delivery
        
        mock_update_items.return_value = 2
        
        # Execute
        result = create_delivery_transaction(self.db)
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_delivery)
        self.db.commit.assert_called_once()

    @patch('deliveries.services.update_delivery_items')
    @patch('deliveries.services.add_delivery')
    @patch('deliveries.services.get_pending_delivery_orders')
    def test_create_delivery_transaction_multi_chunk(self, mock_get_pending, mock_add, mock_update_items):
        # Mock setup
        warehouse_id = uuid4()
        # Create 15 sales_orders to be split into two chunks (10 + 5)
        sales_orders = [uuid4() for _ in range(15)]
        
        mock_get_pending.return_value = {warehouse_id: sales_orders}
        
        mock_delivery1 = MagicMock()
        mock_delivery2 = MagicMock()
        mock_add.side_effect = [mock_delivery1, mock_delivery2]
        
        mock_update_items.return_value = 10  # Both updates succeed
        
        # Execute
        result = create_delivery_transaction(self.db)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_add.call_count, 2)
        self.assertEqual(mock_update_items.call_count, 2)
        self.db.commit.assert_called_once()

    @patch('deliveries.services.update_delivery_items')
    @patch('deliveries.services.add_delivery')
    @patch('deliveries.services.get_pending_delivery_orders')
    def test_create_delivery_transaction_update_fails(self, mock_get_pending, mock_add, mock_update_items):
        # Mock setup
        warehouse_id = uuid4()
        sales_orders = [uuid4(), uuid4()]
        
        mock_get_pending.return_value = {warehouse_id: sales_orders}
        
        mock_delivery = MagicMock()
        mock_delivery.id = uuid4()
        mock_add.return_value = mock_delivery
        
        # Update returns 0 rows affected
        mock_update_items.return_value = 0
        
        # Execute
        result = create_delivery_transaction(self.db)
        
        # Assert
        self.assertIsNone(result)
        self.db.rollback.assert_called_once()
        self.db.commit.assert_not_called()

    @patch('deliveries.services.print')
    @patch('deliveries.services.get_pending_delivery_orders')
    def test_create_delivery_transaction_exception(self, mock_get_pending, mock_print):
        # Mock setup
        mock_get_pending.side_effect = Exception("Database error")
        
        # Execute
        result = create_delivery_transaction(self.db)
        
        # Assert
        self.assertIsNone(result)
        self.db.rollback.assert_called_once()
        mock_print.assert_called_once()


if __name__ == "__main__":
    unittest.main()