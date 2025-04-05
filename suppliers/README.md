# FastAPI Sales Project

This project is a FastAPI application for managing sales and purchases. It includes endpoints for creating, retrieving, updating, and deleting purchases, as well as managing user information.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. Install dependencies using `pipenv`:

    ```sh
    pipenv install
    ```

3. Activate the virtual environment:

    ```sh
    pipenv shell
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory of the project and add the following environment variables:

    ```env
    DB_USER=
    DB_PASSWORD=
    DB_HOST=
    DB_PORT=
    DB_NAME=
    ```

## Running the Application

1. Start the Memcached server using Docker:

    ```sh
    docker run -d --name memcached -p 11211:11211 memcached
    ```

2. Run the FastAPI application:

    ```sh
    uvicorn main:app --port 8000 --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

## Endpoints

### 1. Health Check

- **GET** `/ventas/health`
  - Response: `"pong"`

### 2. Purchases

- **POST** [purchases](/ventas/compras/)
  - Request Body:
    ```json
    {
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "address_id": "123e4567-e89b-12d3-a456-426614174001",
      "items": [
        {
          "product_id": "123e4567-e89b-12d3-a456-426614174002",
          "quantity": 2
        },
        {
          "product_id": "123e4567-e89b-12d3-a456-426614174003",
          "quantity": 1
        }
      ]
    }
    ```
  - Response: `PurchaseResponse`

- **GET** `/ventas/compras/{purchase_id}`
  - Response: `PurchaseResponse`

- **GET** [purchases](/ventas/compras/)
  - Query Parameters: `skip`, `limit`
  - Response: `List[PurchaseResponse]`

- **DELETE** `/ventas/compras/{purchase_id}`
  - Response: `DeleteResponse`


### 3. Add product pictures

- **POST** `/suppliers/manufacturers/{manufacturer_id}/products/image/`
  - Form Data:
    - `product_id`: ID of the product to add an image to
    - `product_image`: Collection of image files to upload
  - Response: `ImageUploadResponse`
    ```json
    {
      "operation_id": ID of the upload operation,
      "product_id": ID of the product to which images were uploaded,
      "processed_records": number of images processed,
      "successful_records": number of images successfully uploaded,
      "failed_records": number of images that failed to upload,
      "created_at": date and time when the image upload was performed, in ISO format
    }
    ```
  - Status Codes:
    - `201`: Images successfully uploaded
    - `400`: Invalid request (missing product_id or image files)
    - `404`: Manufacturer or product not found
    - `415`: Unsupported media type


## Running Tests

To run the tests, use the following command:

```sh
pytest --cov=. -v -s --cov-fail-under=70
```

Pre commit

```
pre-commit install

<!-- manually -->
pre-commit run --all-files

```

Run black
```
<!-- All files -->
black .
<!-- Single file -->
black path_to_file
```
