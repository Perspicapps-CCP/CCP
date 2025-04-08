
## 📋 Create Sales Plan

### `POST /api/v1/sales/plans`

Create a new sales plan for a product and assign it to one or more sellers.

---

### 🔐 Authentication

Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### 📥 Request Body

```json
{
  "product_id": "ae3f541e-b3b5-4cb6-a018-02f58bbd0c2e",
  "goal": 1000,
  "start_date": "2025-03-01",
  "end_date": "2025-03-31",
  "seller_ids": [
    "3f9c962a-6b71-41d2-a9e0-b98c0c245e4a",
    "95f25a3f-8e3e-4fa4-804a-3dd7b640a6a3"
  ]
}
```

| Field        | Type     | Required | Description                                    |
|--------------|----------|----------|------------------------------------------------|
| product_id   | UUID     | ✅       | ID of the product                              |
| goal         | integer  | ✅       | Sales goal for the plan                        |
| start_date   | string   | ✅       | Start date (format: `YYYY-MM-DD`)             |
| end_date     | string   | ✅       | End date (format: `YYYY-MM-DD`)               |
| seller_ids   | UUID[]   | ✅       | Array of seller UUIDs assigned to this plan   |

---

### 📤 Response (201 Created)

```json
{
  "id": "faec7f5d-308e-4d5b-9dbb-564f72c04f4a",
  "product": {
        "id": "0c5c90ab-95e4-4a7b-aad3-6d3ee80cf469",
        "images": [
            "http://example.com/img4.jpg"
        ],
        "product_code": "p001",
        "name": "MProduct1",
        "price": "5000.00"
  },
  "goal": 1000,
  "start_date": "2025-03-01",
  "end_date": "2025-03-31",
  "sellers": [
    {
      "id": "3f9c962a-6b71-41d2-a9e0-b98c0c245e4a",
      "full_name": "Wilson Ventas Quevedo",
      "email": "wilveque@ccp.com.co",
      "username": "wilveque",
      "phone": "+57 2325248847",
      "id_type": "CC",
      "identification": "101448745887"
    },
    {
      "id": "95f25a3f-8e3e-4fa4-804a-3dd7b640a6a3",
      "full_name": "Cosme Fulanito",
      "email": "cosme@ccp.com.co",
      "username": "cosmef",
      "phone": "+57 3000000000",
      "id_type": "CC",
      "identification": "101000000000"
    }
  ]
}
```

| Field         | Type   | Description                            |
|---------------|--------|----------------------------------------|
| id            | UUID   | Unique ID of the created plan          |
| sellers       | array  | List of seller objects (full structure)|

---

### ❌ Error Responses

#### 400 Bad Request

```json
{
  "detail": "End date must be after start date"
}
```

#### 422

## 📄 List All Sales Plans API

### `GET /api/v1/sales/plans`

Retrieve all sales plans in the system. Each plan includes its assigned sellers and metadata.

> ⚠️ This endpoint is **not paginated** — it returns the full list.

---

### 🔐 Authentication

Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### 📤 Response (200 OK)

```json
[
  {
    "id": "faec7f5d-308e-4d5b-9dbb-564f72c04f4a",
    "product": {
        "id": "0c5c90ab-95e4-4a7b-aad3-6d3ee80cf469",
        "images": [
            "http://example.com/img4.jpg"
        ],
        "product_code": "p001",
        "name": "MProduct1",
        "price": "5000.00"
    },
    "goal": 1000,
    "start_date": "2025-03-01",
    "end_date": "2025-03-31",
    "sellers": [
      {
        "id": "3f9c962a-6b71-41d2-a9e0-b98c0c245e4a",
        "full_name": "Wilson Ventas Quevedo",
        "email": "wilveque@ccp.com.co",
        "username": "wilveque",
        "phone": "+57 2325248847",
        "id_type": "CC",
        "identification": "101448745887"
      },
      {
        "id": "95f25a3f-8e3e-4fa4-804a-3dd7b640a6a3",
        "full_name": "Cosme Fulanito",
        "email": "cosme@ccp.com.co",
        "username": "cosmef",
        "phone": "+57 3000000000",
        "id_type": "CC",
        "identification": "101000000000"
      }
    ]
  },
  {
    "id": "67f4531e-df2a-45ff-bc1f-3640dc0bcb01",
    "product": {
        "id": "0c5c90ab-95e4-4a7b-aad3-6d3ee80cf469",
        "images": [
            "http://example.com/img4.jpg"
        ],
        "product_code": "p001",
        "name": "MProduct1",
        "price": "5000.00"
    },
    "goal": 500,
    "start_date": "2025-04-01",
    "end_date": "2025-04-30",
    "sellers": [
      {
        "id": "1a7f962a-9d44-43f2-8eaf-d5c5a45f3c1d",
        "full_name": "Johanna Sepulveda",
        "email": "johanna@ccp.com.co",
        "username": "jsepulveda",
        "phone": "+57 3112233445",
        "id_type": "CC",
        "identification": "101998877665"
      }
    ]
  }
]
```

| Field         | Type     | Description                             |
|---------------|----------|-----------------------------------------|
| id            | UUID     | Unique ID of the sales plan             |
| product       | object   | Associated product                      |
| goal          | integer  | Sales target                            |
| start_date    | string   | Start date (YYYY-MM-DD)                 |
| end_date      | string   | End date (YYYY-MM-DD)                   |
| sellers       | array    | List of seller objects (full structure) |

---

### ❌ Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action"
}
```

## 📄 List Seller Sales API

### `GET /api/v1/sales/sales/`

Retrieve all sales records made by sellers. Each record includes order and seller details.

> ⚠️ This endpoint is **not paginated** — it returns the full list of sales.

---

### 🔐 Authentication

Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### 📤 Response (200 OK)

```json
[
  {
    "order": {
      "id": "eec0aa19-d22f-4c5f-a27e-0f32fa8a6ac2",
      "number": "3155185411"
    },
    "city": "Bogota",
    "date": "2025-04-01",
    "value": 120000,
    "seller": {
      "id": "3f9c962a-6b71-41d2-a9e0-b98c0c245e4a",
      "full_name": "Wilson Ventas Quevedo",
      "email": "wilveque@ccp.com.co",
      "username": "wilveque",
      "phone": "+57 2325248847",
      "id_type": "CC",
      "identification": "101448745887"
    }
  }
]
```

---

### 🔍 Field Reference

| Field       | Type   | Description                             |
|-------------|--------|-----------------------------------------|
| order       | object | Contains `id` (UUID) and `number` (string) |
| city        | string | City where the sale occurred            |
| date        | string | Date of the sale (`YYYY-MM-DD`)         |
| value       | number | Sale amount in local currency           |
| seller      | object | Full seller profile (same structure used in seller endpoints) |

---

### ❌ Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

```json
{
  "detail": "You do not have permission to view sales"
}
```

## 📤 Export Sales API

### `GET /api/v1/sales/sales/export/`

Export seller sales as a CSV file using optional filters like seller and date range.

---

### 🔐 Authentication

Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### 📥 Query Parameters

| Param        | Type   | Required | Description                                  |
|--------------|--------|----------|----------------------------------------------|
| seller_id    | UUID   | ❌       | Filter sales by specific seller              |
| start_date   | string | ❌       | Filter from this date (`YYYY-MM-DD`)         |
| end_date     | string | ❌       | Filter until this date (`YYYY-MM-DD`)        |

**Example request:**

```
GET /api/v1/sales/sales/export/?seller_id=3f9c962a-6b71-41d2-a9e0-b98c0c245e4a&start_date=2025-04-01&end_date=2025-04-30
```

---

### 📤 Response (200 OK)

**Content-Type:** `text/csv`
**Content-Disposition:** `attachment; filename="sales_export.csv"`

Returns a downloadable `.csv` file with sales data.

**Example CSV Format:**

```
order_id,order_number,date,city,seller_name,seller_phone,value
eec0aa19-d22f-4c5f-a27e-0f32fa8a6ac2,3155185411,2025-04-01,Bogota,Wilson Ventas Quevedo,+57 2325248847,120000
...
```

---

### ❌ Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid date range: end_date must be after start_date"
}
```

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

```json
{
  "detail": "You do not have permission to export sales"
}
```

## 📍 List Routes API

### `GET /api/v1/sales/routes/`

Retrieve all sales routes. Each route includes multiple client stops with full client and address info.

---

### 🔐 Authentication

Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### 📥 Query Parameters (Optional)

| Param        | Type   | Description                                             |
|--------------|--------|---------------------------------------------------------|
| client_id    | UUID   | Filter routes that include this client                  |
| address      | string | Filter by address line or reference (partial match)     |
| start_date   | string | Filter from date (`YYYY-MM-DD`)                         |
| end_date     | string | Filter to date (`YYYY-MM-DD`)                           |

---

### 📤 Response (200 OK)

```json
[
  {
    "id": "f8e9a492-9bd1-40c6-9a6a-fc4f56eaeaf1",
    "date": "2025-02-20",
    "stops": [
      {
        "client": {
          "id": "3f9c962a-6b71-41d2-a9e0-b98c0c245e4a",
          "full_name": "Cosme Fulanito",
          "email": "cosme@ccp.com.co",
          "username": "cosmef",
          "phone": "+57 3000000000",
          "id_type": "CC",
          "identification": "101000000000",
          "role": "BUYER"
        },
        "address": {
          "line": "Av Siempre Viva 123",
          "neighborhood": "Centro",
          "city": "Bogota",
          "state": "Cundinamarca",
          "country": "Colombia",
          "latitude": 4.7110,
          "longitude": -74.0721
        }
      }
    ]
  },
  {
    "id": "2d59c857-2d2b-4a4b-9b16-2a4377d11e3a",
    "date": "2025-02-21",
    "stops": [
      {
        "client": {
          "id": "0e86f3d2-1b8a-4a25-a2c6-7842d1ec421f",
          "full_name": "Jumbo Market",
          "email": "jumbo@market.co",
          "username": "jumbo",
          "phone": "+57 3201234567",
          "id_type": "NIT",
          "identification": "900123456",
          "role": "BUYER"
        },
        "address": {
          "line": "Cra 50 #42-10",
          "neighborhood": "Chapinero",
          "city": "Bogota",
          "state": "Cundinamarca",
          "country": "Colombia",
          "latitude": 4.6584,
          "longitude": -74.0935
        }
      }
    ]
  }
]
```

---

### ❌ Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

#### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["query", "start_date"],
      "msg": "Invalid date format",
      "type": "value_error.date"
    }
  ]
}
```

## 🔎 Get Route Detail API

### `GET /api/v1/sales/routes/{route_id}`

Retrieve the full detail of a specific route, including all client stops.

---

### 🔐 Authentication

Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### 📥 Path Parameter

| Param     | Type | Required | Description           |
|-----------|------|----------|-----------------------|
| route_id  | UUID | ✅       | Unique ID of the route |

---

### 📤 Response (200 OK)

```json
{
  "id": "f8e9a492-9bd1-40c6-9a6a-fc4f56eaeaf1",
  "date": "2025-02-20",
  "stops": [
    {
      "client": {
        "id": "3f9c962a-6b71-41d2-a9e0-b98c0c245e4a",
        "full_name": "Cosme Fulanito",
        "email": "cosme@ccp.com.co",
        "username": "cosmef",
        "phone": "+57 3000000000",
        "id_type": "CC",
        "identification": "101000000000",
        "role": "BUYER"
      },
      "address": {
        "line": "Av Siempre Viva 123",
        "neighborhood": "Centro",
        "city": "Bogota",
        "state": "Cundinamarca",
        "country": "Colombia",
        "latitude": 4.7110,
        "longitude": -74.0721
      }
    },
    {
      "client": {
        "id": "0e86f3d2-1b8a-4a25-a2c6-7842d1ec421f",
        "full_name": "Jumbo Market",
        "email": "jumbo@market.co",
        "username": "jumbo",
        "phone": "+57 3201234567",
        "id_type": "NIT",
        "identification": "900123456",
        "role": "BUYER"
      },
      "address": {
        "line": "Cra 50 #42-10",
        "neighborhood": "Chapinero",
        "city": "Bogota",
        "state": "Cundinamarca",
        "country": "Colombia",
        "latitude": 4.6584,
        "longitude": -74.0935
      }
    }
  ]
}
```

---

### 📦 Stops Array

Each item in `stops` contains:

| Field   | Type   | Description                          |
|---------|--------|--------------------------------------|
| client  | object | Buyer user object                    |
| address | object | Full structured address              |

---

### ❌ Error Responses

#### 404 Not Found

```json
{
  "detail": "Route not found"
}
```

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden

```json
{
  "detail": "You do not have access to this route"
}
```
