from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from faker import Faker

from rpc_clients.schemas import ProductSchema, UserAuthSchema, UserSchema
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
            assert str(product.id) == response_product["id"]
            assert product.product_code == response_product["product_code"]
            assert product.name == response_product["name"]
            assert product.price == response_product["price"]
            assert product.images == response_product["images"]

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
        assert result.product_code == product_reponse["product_code"]
        assert result.name == product_reponse["name"]
        assert result.price == product_reponse["price"]

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

    def test_get_all_products_calls_broker_with_correct_routing_key(
        self, suppliers_client: SuppliersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_all_products calls call_broker with the
          correct routing key and payload.
        """
        suppliers_client.get_all_products()

        # Assert call_broker was called with the
        #  correct routing key and payload
        mock_call_broker.assert_called_once_with(
            "suppliers.get_products",
            {"product_ids": None},
        )


@pytest.mark.skip_mock_users
class UsersClientMixin:
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


class TestUsersClientGetSellers(UsersClientMixin):

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
                "address": None,
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
                "address": {
                    "id": "6e5eb867-db5c-437f-9137-fba893c03068",
                    "line": "Calle 26 #13-15",
                    "neighborhood": "Santa Fe",
                    "city": "Bogota",
                    "state": "Cundinamarca",
                    "country": "Colombia",
                    "latitude": 4.6097,
                    "longitude": -74.0817,
                },
            },
        ]
        mock_response = {"sellers": sellers_response}
        mock_call_broker.return_value = mock_response

        result = users_client.get_sellers(seller_ids)

        # Assert the result is a list of UserSchema objects
        assert len(result) == 2
        for index, seller in enumerate(result):
            assert isinstance(seller, UserSchema)
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

    def test_get_all_sellers_calls_broker_with_correct_routing_key(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_all_sellers calls call_broker with the
          correct routing key and payload.
        """
        users_client.get_all_sellers()

        # Assert call_broker was called with the
        #  correct routing key and payload
        mock_call_broker.assert_called_once_with(
            "users.get_sellers",
            {"seller_ids": None},
        )


class TestUsersClientGetClients(UsersClientMixin):
    def test_get_clients_calls_broker_with_correct_routing_key(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_clients calls call_broker with the
          correct routing key and payload.
        """
        client_ids = [uuid4(), uuid4()]
        users_client.get_clients(client_ids)

        # Assert call_broker was called with the
        #  correct routing key and payload
        mock_call_broker.assert_called_once_with(
            "users.get_clients",
            {"client_ids": [str(client_id) for client_id in client_ids]},
        )

    def test_get_clients_returns_correct_data(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_clients returns the correct
          data when call_broker is mocked.
        """
        client_ids = [uuid4(), uuid4()]
        clients_response = [
            {
                "id": str(client_ids[0]),
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
                "address": None,
            },
            {
                "id": str(client_ids[1]),
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
                "address": {
                    "id": "6e5eb867-db5c-437f-9137-fba893c03068",
                    "line": "Calle 26 #13-15",
                    "neighborhood": "Santa Fe",
                    "city": "Bogota",
                    "state": "Cundinamarca",
                    "country": "Colombia",
                    "latitude": 4.6097,
                    "longitude": -74.0817,
                },
            },
        ]
        mock_response = {"clients": clients_response}
        mock_call_broker.return_value = mock_response

        result = users_client.get_clients(client_ids)

        # Assert the result is a list of UserSchema objects
        assert len(result) == 2
        for index, client in enumerate(result):
            assert isinstance(client, UserSchema)
            response_client = clients_response[index]
            assert str(client.id) == response_client["id"]
            assert client.full_name == response_client["full_name"]
            assert client.email == response_client["email"]
            assert client.username == response_client["username"]
            assert client.phone == response_client["phone"]
            assert client.id_type == response_client["id_type"]
            assert client.identification == response_client["identification"]

    def test_get_clients_returns_empty_list_if_no_clients_found(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_clients returns an empty list if no clients are found.
        """
        client_ids = [uuid4(), uuid4()]
        mock_call_broker.return_value = {
            "clients": []
        }  # Simulate no clients found

        result = users_client.get_clients(client_ids)

        # Assert the result is an empty list
        assert result == []

    def test_get_all_clients_calls_broker_with_correct_routing_key(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that get_all_clients calls call_broker with the
          correct routing key and payload.
        """
        users_client.get_all_clients()

        # Assert call_broker was called with the
        #  correct routing key and payload
        mock_call_broker.assert_called_once_with(
            "users.get_clients",
            {"client_ids": None},
        )


class TestUsersClientAuthUser(UsersClientMixin):
    def test_auth_user_calls_broker_with_correct_routing_key(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that auth_user calls call_broker with the
          correct routing key and payload.
        """
        bearer_token = "test_token"
        mock_call_broker.return_value = {"user": None}
        users_client.auth_user(bearer_token)

        # Assert call_broker was called with the
        #  correct routing key and payload
        mock_call_broker.assert_called_once_with(
            "users.auth_user", {"bearer_token": bearer_token}
        )

    def test_auth_user_returns_correct_data(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that auth_user returns the correct data when
          call_broker is mocked.
        """
        bearer_token = "test_token"
        user_response = {
            "id": str(uuid4()),
            "full_name": fake.name(),
            "email": fake.email(),
            "username": fake.user_name(),
            "phone": fake.phone_number(),
            "id_type": fake.random_element(elements=("ID", "Passport")),
            "identification": str(fake.random_int(min=100000, max=999999)),
            "created_at": fake.date_time().isoformat(),
            "updated_at": fake.date_time().isoformat(),
            "address": None,
            "is_active": True,
            "is_seller": True,
            "is_client": False,
        }
        mock_response = {"user": user_response}
        mock_call_broker.return_value = mock_response

        result = users_client.auth_user(bearer_token)

        # Assert the result is a UserSchema object
        assert isinstance(result, UserAuthSchema)
        assert str(result.id) == user_response["id"]
        assert result.full_name == user_response["full_name"]
        assert result.email == user_response["email"]
        assert result.username == user_response["username"]
        assert result.phone == user_response["phone"]
        assert result.id_type == user_response["id_type"]
        assert result.identification == user_response["identification"]
        assert result.is_active == user_response["is_active"]
        assert result.is_seller == user_response["is_seller"]
        assert result.is_client == user_response["is_client"]

    def test_auth_user_returns_none_if_user_not_found(
        self, users_client: UsersClient, mock_call_broker: MagicMock
    ):
        """
        Test that auth_user returns None if the user is not found.
        """
        bearer_token = "test_token"
        mock_call_broker.return_value = {"user": None}
        result = users_client.auth_user(bearer_token)
        # Assert the result is None
        assert result is None
