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
  "delivery_status": "scheduled",
  "order": [
    {
      "order_number": "ORD-2025-0412",
      "order_address": "Calle 123 #45-67, Bogotá",
      "customer_phone_number": "+57 3001234567",
      "product": [
        {
          "product_id": "0c5c90ab-95e4-4a7b-aad3-6d3ee80cf469",
          "product_code": "P001",
          "product_name": "Laptop Empresarial X500",
          "quantity": 1,
          "images": [
            "https://example.com/images/laptop1.jpg",
            "https://example.com/images/laptop1_alt.jpg"
          ]
        },
        {
          "product_id": "71ba32ed-9a1c-42d3-8c89-3f1e4e5d6c7b",
          "product_code": "P002",
          "product_name": "Monitor UltraWide 34\"",
          "quantity": 2,
          "images": [
            "https://example.com/images/monitor.jpg"
          ]
        }
      ]
    },
    {
      "order_number": "ORD-2025-0415",
      "order_address": "Carrera 78 #23-45, Bogotá",
      "customer_phone_number": "+57 3109876543",
      "product": [
        {
          "product_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
          "product_code": "P003",
          "product_name": "Teclado Mecánico RGB",
          "quantity": 3,
          "images": [
            "https://example.com/images/keyboard.jpg"
          ]
        }
      ]
    }
  ]
}
```
|Field	|Type	|	Description|
|-|-|-|
|shipping_number	|string	|Unique tracking number for the delivery route|
|licence_plate	|string	|License plate of the delivery vehicle|
|diver_name	|string	|Name of the delivery driver|
|warehouse	|object	|Information about the pickup warehouse|
|delivery_status	|string	|Current status of the delivery route|
|order	|array	|List of orders included in this delivery route|

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