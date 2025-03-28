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

    sh```
    docker run -d --name memcached -p 11211:11211 memcached
    ```

2. Run the FastAPI application:

    ```sh
    uvicorn main:app --reload
    ```

    The application will be available at `http://127.0.0.1:8000`.

## Endpoints

### Health Check

- **GET** `/ventas/health`
  - Response: `"pong"`

### Purchases

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

## Running Tests

To run the tests, use the following command:

```sh
    uvicorn main:app  --port 8000
```



pytest --cov=. -v -s --cov-fail-under=70


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
