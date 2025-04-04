from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from faker import Faker

from rpc_clients.schemas import ProductSchema, SellerSchema
from rpc_clients.suppliers_client import SuppliersClient
from rpc_clients.users_client import UsersClient

fake = Faker()


@pytest.mark.skip_mock_suppliers
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

        result = suppliers_client.get_product(product_id)

        # Assert the result is a ProductSchema object
        assert isinstance(result, ProductSchema)
        assert result.id == product_id
        assert result.product_code == product_reponse['product_code']
        assert result.name == product_reponse['name']
        assert result.price == product_reponse['price']

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

        with pytest.raises(ValueError, match="Product not found."):
            suppliers_client.get_product(product_id)


@pytest.mark.skip_mock_users
class TestUsersClient:
    @pytest.fixture
    def mock_call_broker(self):
        """
        Fixture to mock the call_broker method.
        """
        return MagicMock()

    @pytest.fixture
    def users_client(self, mock_call_broker) -> UsersClient:
        """
        Fixture to create a UsersClient instance with a mocked call_broker.
        """
        client = UsersClient()
        client.call_broker = mock_call_broker
        return client

    def test_get_sellers_calls_broker_with_correct_routing_key(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_sellers calls call_broker with the
          correct routing key and payload.
        """
        seller_ids = [uuid4(), uuid4()]
        users_client.get_sellers(seller_ids)

        # Assert call_broker was called with the
        #  correct routing key and payload
        mock_call_broker.assert_called_once_with(
            "users.get_sellers",
            {"seller_ids": [str(seller_id) for seller_id in seller_ids]},
        )

    def test_get_sellers_returns_correct_data(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_sellers returns the correct
          data when call_broker is mocked.
        """
        seller_ids = [uuid4(), uuid4()]
        sellers_response = [
            {
                "id": str(seller_ids[0]),
                "full_name": fake.name(),
                "email": fake.email(),
                "username": fake.user_name(),
                "phone": fake.phone_number(),
                "id_type": fake.random_element(elements=("ID", "Passport")),
                "identification": str(
                    fake.random_int(min=100000, max=999999)
                ),
                "created_at": fake.date_time().isoformat(),
                "updated_at": fake.date_time().isoformat(),
            },
            {
                "id": str(seller_ids[1]),
                "full_name": fake.name(),
                "email": fake.email(),
                "username": fake.user_name(),
                "phone": fake.phone_number(),
                "id_type": fake.random_element(elements=("ID", "Passport")),
                "identification": str(
                    fake.random_int(min=100000, max=999999)
                ),
                "created_at": fake.date_time().isoformat(),
                "updated_at": fake.date_time().isoformat(),
            },
        ]
        mock_response = {"sellers": sellers_response}
        mock_call_broker.return_value = mock_response

        result = users_client.get_sellers(seller_ids)

        # Assert the result is a list of SellerSchema objects
        assert len(result) == 2
        for index, seller in enumerate(result):
            assert isinstance(seller, SellerSchema)
            response_seller = sellers_response[index]
            assert str(seller.id) == response_seller["id"]
            assert seller.full_name == response_seller["full_name"]
            assert seller.email == response_seller["email"]
            assert seller.username == response_seller["username"]
            assert seller.phone == response_seller["phone"]
            assert seller.id_type == response_seller["id_type"]
            assert seller.identification == response_seller["identification"]

    def test_get_sellers_returns_empty_list_if_no_sellers_found(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_sellers returns an empty list if no sellers are found.
        """
        seller_ids = [uuid4(), uuid4()]
        mock_call_broker.return_value = {
            "sellers": []
        }  # Simulate no sellers found

        result = users_client.get_sellers(seller_ids)

        # Assert the result is an empty list
        assert result == []
