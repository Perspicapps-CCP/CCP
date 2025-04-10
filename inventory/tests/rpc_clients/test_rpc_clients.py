import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from faker import Faker

from rpc_clients.schemas import ProductSchema
from rpc_clients.suppliers_client import SuppliersClient

fake = Faker()


class TestSuppliersClient:

    @pytest.fixture
    def mock_call_broker(self):
        """
        Fixture to mock the call_broker method.
        """
        return MagicMock()

    @pytest.fixture
    def suppliers_client(self, mock_call_broker) -> SuppliersClient:
        """
        Fixture to create a SuppliersClient instance with a mocked call_broker.
        """
        with patch('pika.BlockingConnection') as mock_connection:
            mock_channel = MagicMock()
            mock_connection.return_value.channel.return_value = mock_channel
            client = SuppliersClient()
            client.call_broker = mock_call_broker
            return client

    def test_get_products_calls_broker_with_correct_routing_key(
        self, suppliers_client: SuppliersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_products calls call_broker with the correct
          routing key and payload.
        """
        product_ids = [uuid4(), uuid4()]
        suppliers_client.get_products(product_ids)

        # Assert call_broker was called with the
        #  correct routing key and payload
        mock_call_broker.assert_called_once_with(
            "suppliers.get_products",
            {"product_ids": [str(product_id) for product_id in product_ids]},
        )

    def test_get_products_returns_correct_data(
        self, suppliers_client: SuppliersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_products returns the correct data when
          call_broker is mocked.
        """
        product_ids = [uuid4(), uuid4()]
        products_response = [
            {
                "id": str(product_ids[0]),
                "product_code": str(fake.random_int(min=1000, max=9999)),
                "name": fake.word(),
                "price": fake.random_number(digits=5),
                "images": [fake.image_url() for _ in range(3)],
            },
            {
                "id": str(product_ids[1]),
                "product_code": str(fake.random_int(min=1000, max=9999)),
                "name": fake.word(),
                "price": fake.random_number(digits=5),
                "images": [fake.image_url() for _ in range(3)],
            },
        ]
        mock_response = {"products": products_response}
        mock_call_broker.return_value = mock_response

        result = suppliers_client.get_products(product_ids)

        # Assert the result is a list of ProductSchema objects
        assert len(result) == 2
        for index, product in enumerate(result):
            assert isinstance(product, ProductSchema)
            response_product = products_response[index]
            assert str(product.id) == response_product['id']
            assert product.product_code == response_product['product_code']
            assert product.name == response_product['name']
            assert product.price == response_product['price']
            assert product.images == response_product['images']

    def test_get_product_calls_get_products(
        self, suppliers_client: SuppliersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_product calls get_products and
          returns the correct product.
        """
        product_id = uuid4()
        product_reponse = {
            "id": str(product_id),
            "product_code": str(fake.random_int(min=1000, max=9999)),
            "name": fake.word(),
            "price": fake.random_number(digits=5),
            "images": [fake.image_url() for _ in range(3)],
        }
        mock_response = {"products": [product_reponse]}
        mock_call_broker.return_value = mock_response

        result = suppliers_client.get_products([product_id])

        # Assert the result is a ProductSchema object
        assert isinstance(result[0], ProductSchema)
        assert result[0].id == product_id
        assert result[0].product_code == product_reponse['product_code']
        assert result[0].name == product_reponse['name']
        assert result[0].price == product_reponse['price']

    def test_get_product_raises_value_error_if_product_not_found(
        self, suppliers_client: SuppliersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_product raises a ValueError if the product is not found.
        """
        product_id = uuid4()
        mock_call_broker.return_value = {
            "products": []
        }  # Simulate no products found

        result = suppliers_client.get_products([product_id])
        assert len(result) == 0
