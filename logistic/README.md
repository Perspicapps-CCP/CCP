# FastAPI Logistic Project

This project is a FastAPI application for managing Logistic. It includes endpoints for creating, retrieving, deliveries and routes

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


## Running Tests

To run the tests, use the following command:

```sh
pytest --cov=. -v -s --cov-fail-under=80
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

# Logistic endpoints

## Create Delivery Route
### `POST /logistic/delivery`
Creates a new delivery route for orders from a specific warehouse on a given date.
---
🔐 Authentication
Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```
---
📥 Request Body

```json
{
  "delivery_date": "2025-04-10",
  "warehouse_id": "e7a3b2c1-5d9f-48e6-b0a7-c2d1f3e4a5b6"
}
```

|Field	|Type	|Required|	Description|
|-|-|-|-|
|delivery_date	|string	|✅	|Date for the delivery (format: YYYY-MM-DD)|
|warehouse_id	|UUID	|✅	|ID of the warehouse for pickup|

📤 Response (201 Created)

```json
{
    "shipping_number": "GU-20250410-001",
    "licence_plate": "XYZ-123",
    "diver_name": "Carlos Ramírez",
    "warehouse": {
      "warehouse_id": "e7a3b2c1-5d9f-48e6-b0a7-c2d1f3e4a5b6",
      "warehouse_name": "Bodega Principal Bogotá"
    },
    "delivery_status": "scheduled"
}
```
|Field	|Type	|	Description|
|-|-|-|
|shipping_number	|string	|Unique tracking number for the delivery route|
|licence_plate	|string	|License plate of the delivery vehicle|
|diver_name	|string	|Name of the delivery driver|
|warehouse	|object	|Information about the pickup warehouse|
|delivery_status	|string	|Current status of the delivery route|
|orders	|array	|List of orders included in this delivery route|

❌ Error Responses

400 Bad Request
```json
{
  "detail": "Invalid date format - use YYYY-MM-DD"
}
```
404 Not Found
```json
{
  "detail": "Warehouse with ID e7a3b2c1-5d9f-48e6-b0a7-c2d1f3e4a5b6 not found"
}
```
422 Unprocessable Entity
```json
{
  "detail": "No pending orders for this warehouse on the specified date"
}
```
401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action"
}
```

## Get Deliveries
### `GET /logistic/delivery/{shipping_number}`

Retrieves detailed information about a specific delivery route by its shipping number.
---
🔐 Authentication
Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```
---

📥 Request Parameters

```query string
  shipping_number: "GU-20250410-001"
```

| Parameter | Type | Required | Description |
|-|-|-|-|
| shipping_number | string | ✅ | Unique tracking number for the delivery route |


📤 Response (200 OK)

```json
[{
    "shipping_number": "GU-20250410-001",
    "licence_plate": "XYZ-123",
    "diver_name": "Carlos Ramírez",
    "warehouse": {
      "warehouse_id": "e7a3b2c1-5d9f-48e6-b0a7-c2d1f3e4a5b6",
      "warehouse_name": "Bodega Principal Bogotá"
    },
    "delivery_status": "scheduled",
    "orders": [{
        "order_number": "ORD-2025-0412",
        "order_address": "Calle 123 #45-67, Bogotá",
        "customer_phone_number": "+57 3001234567",
        "product_id": "0c5c90ab-95e4-4a7b-aad3-6d3ee80cf469",
        "product_code": "P001",
        "product_name": "Laptop Empresarial X500",
        "quantity": 1,
        "images":["https://example.com/images/laptop1.jpg", "https://example.com/images/laptop1.jpg"]
    }]
}]
```

|Field	|Type	|	Description|
|-|-|-|
|shipping_number	|string	|Unique tracking number for the delivery route|
|licence_plate	|string	|License plate of the delivery vehicle|
|diver_name	|string	|Name of the delivery driver|
|warehouse	|object	|Information about the pickup warehouse|
|delivery_status	|string	|Current status of the delivery route|
|orders	|array	|List of orders included in this delivery route|

❌ Error Responses

404 Not Found
```json
{
  "detail": "Delivery with shipping number GU-20250410-001 not found"
}
```
401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action"
}
```

## Get Delivery Route
### `GET /logistic/route/{shipping_number}`

Retrieves geographic routing information for a specific delivery, including delivery points with coordinates.

---
🔐 Authentication
Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```
---

📥 Request Parameters

```query string
  shipping_number: "GU-20250410-001"
```

| Parameter | Type | Required | Description |
|-|-|-|-|
| shipping_number | string | ✅ | Unique tracking number for the delivery route |

📤 Response (200 OK)

```json
[{
   "shipping_number": "GU-20250410-001",
   "order_number": "ORD-2025-0412",
   "order_address": "Calle 123 #45-67, Bogotá",
   "order_customer_name": "Ramon Valdez",
   "customer_phone_number": "+57 3001234567",
   "latitude":"4.645707804636481",
   "longitude":"-74.10965904880698",
}]
```

❌ Error Responses

404 Not Found
```json
{
  "detail": "Delivery with shipping number GU-20250410-001 not found"
}
```
401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```
403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action"
}
```