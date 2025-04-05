import io
import uuid
import pytest
from unittest.mock import MagicMock
from faker import Faker
from fastapi.testclient import TestClient

from manufacturers.models import Manufacturer, ManufacturerProduct

fake = Faker()
fake.seed_instance(0)


def mock_manufacturer() -> Manufacturer:
    return Manufacturer(
        name=fake.name(),
        identification_type="CC",
        identification_number=str(fake.random_number(digits=10)),
        address=fake.address(),
        contact_phone=str(fake.random_number(digits=10)),
        email=fake.email(),
    )


def mock_product(manufacturer: Manufacturer) -> ManufacturerProduct:
    return ManufacturerProduct(
        manufacturer_id=manufacturer.id,
        code=fake.word(),
        name=fake.word(),
        price=fake.random_number(digits=5),
    )


@pytest.fixture
def mock_image() -> io.BytesIO:
    """
    Create a mock image file for testing.
    """
    return io.BytesIO(b"fake image content")


@pytest.fixture
def mock_large_image() -> io.BytesIO:
    """
    Create a mock large image file for testing.
    """
    return io.BytesIO(b"x" * (10 * 1024 * 1024))  # 10MB image


def test_upload_images_success(
    client: TestClient,
    mock_image: io.BytesIO,
    mock_storage_bucket: MagicMock,
    db_session,
) -> None:
    dummy_manufacturer = mock_manufacturer()
    db_session.add(dummy_manufacturer)
    db_session.flush()
    db_session.refresh(dummy_manufacturer)

    dummy_product = mock_product(dummy_manufacturer)
    db_session.add(dummy_product)
    db_session.commit()
    db_session.refresh(dummy_product)

    response = client.post(
        f"/suppliers/manufacturers/{dummy_manufacturer.id}/products/image/",
        data={"product_id": str(dummy_product.id)},
        files={"product_image": ("test_image.jpg", mock_image, "image/jpeg")},
    )

    assert response.status_code == 201
    assert response.json()["processed_records"] == 1
    assert response.json()["successful_records"] == 1
    assert response.json()["failed_records"] == 0
    mock_storage_bucket.blob.assert_called_once()


def test_upload_images_success_multiple_images_uploaded(
    client: TestClient,
    mock_image: io.BytesIO,
    mock_storage_bucket: MagicMock,
    db_session,
) -> None:
    dummy_manufacturer = mock_manufacturer()
    db_session.add(dummy_manufacturer)
    db_session.flush()
    db_session.refresh(dummy_manufacturer)

    dummy_product = mock_product(dummy_manufacturer)
    db_session.add(dummy_product)
    db_session.commit()
    db_session.refresh(dummy_product)

    response = client.post(
        f"/suppliers/manufacturers/{dummy_manufacturer.id}/products/image",
        data={"product_id": str(dummy_product.id)},
        files=[
            ("product_image", ("image1.jpg", mock_image, "image/jpeg")),
            ("product_image", ("image2.jpg", mock_image, "image/jpeg")),
            ("product_image", ("image3.jpg", mock_image, "image/jpeg")),
        ],
    )

    assert response.status_code == 201
    assert response.json()["processed_records"] == 3
    assert response.json()["successful_records"] == 3
    assert response.json()["failed_records"] == 0
    mock_storage_bucket.blob.assert_called()


def test_upload_image_failed_manufacturer_not_found(
    client: TestClient, mock_image: io.BytesIO
) -> None:
    non_existent_id = str(uuid.uuid4())

    response = client.post(
        f"/suppliers/manufacturers/{non_existent_id}/products/image",
        data={"product_id": str(uuid.uuid4())},
        files={"product_image": ("test_image.jpg", mock_image, "image/jpeg")},
    )

    assert response.status_code == 404
    assert "Manufacturer not found" in response.json()["detail"]


def test_upload_image_failed_product_not_found(
    client: TestClient,
    mock_image: io.BytesIO,
    db_session,
) -> None:
    dummy_manufacturer = mock_manufacturer()
    db_session.add(dummy_manufacturer)
    db_session.flush()
    db_session.refresh(dummy_manufacturer)

    non_existent_product_id = str(uuid.uuid4())

    response = client.post(
        f"/suppliers/manufacturers/{dummy_manufacturer.id}/products/image",
        data={"product_id": non_existent_product_id},
        files={"product_image": ("test_image.jpg", mock_image, "image/jpeg")},
    )

    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]


def test_upload_image_failed_file_too_large(
    client: TestClient,
    mock_large_image: io.BytesIO,
    db_session,
) -> None:
    dummy_manufacturer = mock_manufacturer()
    db_session.add(dummy_manufacturer)
    db_session.flush()
    db_session.refresh(dummy_manufacturer)

    dummy_product = mock_product(dummy_manufacturer)
    db_session.add(dummy_product)
    db_session.commit()
    db_session.refresh(dummy_product)

    response = client.post(
        f"/suppliers/manufacturers/{dummy_manufacturer.id}/products/image",
        data={"product_id": str(dummy_product.id)},
        files={
            "product_image": (
                "large_image.jpg",
                mock_large_image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["processed_records"] == 1
    assert response.json()["successful_records"] == 0
    assert response.json()["failed_records"] == 1


def test_upload_image_failed_upload_error(
    client: TestClient,
    mock_image: io.BytesIO,
    mock_storage_bucket,
    db_session,
) -> None:
    dummy_manufacturer = mock_manufacturer()
    db_session.add(dummy_manufacturer)
    db_session.flush()
    db_session.refresh(dummy_manufacturer)

    dummy_product = mock_product(dummy_manufacturer)
    db_session.add(dummy_product)
    db_session.commit()
    db_session.refresh(dummy_product)

    mock_blob = MagicMock()
    mock_blob.upload_from_file.side_effect = Exception("Storage upload error")
    mock_storage_bucket.blob.return_value = mock_blob

    response = client.post(
        f"/suppliers/manufacturers/{dummy_manufacturer.id}/products/image",
        data={"product_id": str(dummy_product.id)},
        files={"product_image": ("test_image.jpg", mock_image, "image/jpeg")},
    )

    assert response.status_code == 201
    assert response.json()["processed_records"] == 1
    assert response.json()["successful_records"] == 0
    assert response.json()["failed_records"] == 1

    mock_storage_bucket.blob.assert_called_once()
    mock_blob.upload_from_file.assert_called_once()
