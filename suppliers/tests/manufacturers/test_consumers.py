import json
import uuid
from typing import List
from unittest import mock

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from manufacturers.consumers import (
    GetProductsByCodeConsumer,
    GetProductsConsumer,
)
from manufacturers.models import (
    IdentificationType,
    Manufacturer,
    ManufacturerProduct,
)

fake = Faker()


@pytest.fixture
def manufacturer(db_session: Session) -> Manufacturer:
    manufacturer = Manufacturer(
        id=uuid.uuid4(),
        identification_type=fake.random_element(IdentificationType),
        identification_number=fake.random_int(),
        name=fake.company(),
        address=fake.address(),
        contact_phone=fake.phone_number(),
        email=fake.email(),
        created_at=fake.date_time(),
        updated_at=fake.date_time(),
    )
    db_session.add(manufacturer)
    db_session.commit()
    return manufacturer


@pytest.fixture
def products_in_db(
    db_session: Session, manufacturer: Manufacturer
) -> List[ManufacturerProduct]:
    """
    Fixture to create products in the database for testing.
    """

    products = [
        ManufacturerProduct(
            id=uuid.uuid4(),
            manufacturer_id=manufacturer.id,
            code=fake.ean(),
            name=fake.word(),
            price=fake.random_number(digits=5),
            created_at=fake.date_time(),
            updated_at=fake.date_time(),
        )
        for _ in range(3)
    ]
    db_session.add_all(products)
    db_session.commit()
    return list(
        db_session.query(ManufacturerProduct)
        .order_by(ManufacturerProduct.updated_at.desc())
        .all()
    )


class TestGetProductsConsumer:
    """
    Test suite for the GetProductsConsumer class.
    """

    def test_invalid_payload(self):
        """
        Test GetProductsConsumer with an invalid payload.
        """
        consumer = GetProductsConsumer()
        invalid_payload = {"invalid_key": "invalid_value"}

        response = consumer.process_payload(invalid_payload)

        assert "error" in response
        assert isinstance(
            response["error"], list
        )  # Validation errors are returned as a list
        assert response["error"][0]["loc"] == ("product_ids",)
        assert response["error"][0]["msg"] == "Field required"

    def test_valid_payload(
        self, db_session: Session, products_in_db: List[ManufacturerProduct]
    ):
        """
        Test GetProductsConsumer with a valid payload and verify the data.
        """
        consumer = GetProductsConsumer()
        select_products = products_in_db[:2]  # Select first two products

        # Prepare a valid payload with product IDs
        product_ids = [str(product.id) for product in select_products]
        valid_payload = {"product_ids": product_ids}

        with mock.patch("manufacturers.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            products_data = consumer.process_payload(valid_payload)
            products_data = json.loads(products_data)

        assert "products" in products_data
        products_data = products_data["products"]

        assert len(products_data) == len(select_products)
        for product, product_data in zip(select_products, products_data):
            assert str(product.id) == product_data["id"]
            assert product.code == product_data["product_code"]
            assert product.name == product_data["name"]
            assert str(product.price) == product_data["price"]

    def test_list_missing_products(self, db_session: Session):
        """
        Test GetProductsConsumer with a valid payload and verify the data.
        """
        consumer = GetProductsConsumer()
        valid_payload = {
            "product_ids": [
                str(uuid.uuid4()),
                str(uuid.uuid4()),
                str(uuid.uuid4()),
            ]
        }
        with mock.patch("manufacturers.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            products_data = consumer.process_payload(valid_payload)
            products_data = json.loads(products_data)

        assert "products" in products_data
        assert len(products_data["products"]) == 0

    @pytest.mark.usefixtures("products_in_db")
    def test_empty_products(self, db_session: Session):
        """
        Test GetProductsConsumer with an empty list of product IDs.
        """
        consumer = GetProductsConsumer()
        valid_payload = {"product_ids": []}

        with mock.patch("manufacturers.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            # Parse the JSON response
            products_data = consumer.process_payload(valid_payload)
            products_data = json.loads(products_data)

        assert "products" in products_data
        assert len(products_data["products"]) == 0


class TestGetProductsByCodeConsumer:
    """
    Test suite for the GetProductsByCodeConsumer class.
    """

    def test_invalid_payload(self):
        """
        Test GetProductsByCodeConsumer with an invalid payload.
        """
        consumer = GetProductsByCodeConsumer()
        invalid_payload = {"invalid_key": "invalid_value"}

        response = consumer.process_payload(invalid_payload)

        assert "error" in response
        assert isinstance(response["error"], list)
        assert response["error"][0]["loc"] == ("product_codes",)
        assert response["error"][0]["msg"] == "Field required"

    def test_valid_payload(
        self, db_session: Session, products_in_db: List[ManufacturerProduct]
    ):
        """
        Test GetProductsByCodeConsumer with
          a valid payload and verify the data.
        """
        consumer = GetProductsByCodeConsumer()
        select_products = products_in_db[:2]  # Select first two products

        # Prepare a valid payload with product codes
        product_codes = [product.code for product in select_products]
        valid_payload = {"product_codes": product_codes}

        with mock.patch("manufacturers.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            products_data = consumer.process_payload(valid_payload)
            products_data = json.loads(products_data)

        assert "products" in products_data
        products_data = products_data["products"]

        assert len(products_data) == len(select_products)
        for product, product_data in zip(select_products, products_data):
            assert product.code == product_data["product_code"]
            assert product.name == product_data["name"]
            assert str(product.price) == product_data["price"]

    def test_list_missing_products(self, db_session: Session):
        """
        Test GetProductsByCodeConsumer with codes that do not exist.
        """
        consumer = GetProductsByCodeConsumer()
        valid_payload = {
            "product_codes": [
                "NONEXISTENT1",
                "NONEXISTENT2",
                "NONEXISTENT3",
            ]
        }
        with mock.patch("manufacturers.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            products_data = consumer.process_payload(valid_payload)
            products_data = json.loads(products_data)

        assert "products" in products_data
        assert len(products_data["products"]) == 0

    @pytest.mark.usefixtures("products_in_db")
    def test_empty_products(self, db_session: Session):
        """
        Test GetProductsByCodeConsumer with an empty list of product codes.
        """
        consumer = GetProductsByCodeConsumer()
        valid_payload = {"product_codes": []}

        with mock.patch("manufacturers.consumers.SessionLocal") as get_session:
            get_session.return_value = db_session
            products_data = consumer.process_payload(valid_payload)
            products_data = products_data

        assert "error" in products_data
