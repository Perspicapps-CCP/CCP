## ➕ Create Seller API

### `POST /api/v1/sales/sellers`

Create a new seller using the provided personal and contact information.

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
  "full_name": "Wilson Ventas Quevedo",
  "email": "wilveque@ccp.com.co",
  "id_type": "CC",
  "identification": "101448745887",
  "phone": "+57 2325248847",
  "username": "wilveque"
}
```

| Field           | Type   | Required | Description                                |
|------------------|--------|----------|--------------------------------------------|
| full_name        | string | ✅       | Seller’s full name                         |
| email            | string | ✅       | Seller’s email address                     |
| id_type          | string | ✅       | Type of ID (e.g. `CC`, `CE`, `NIT`, etc.)  |
| identification   | string | ✅       | ID number                                  |
| phone            | string | ✅       | Phone number (e.g. with country code)      |
| username         | string | ✅       | Username for login                         |

---

### 📤 Response (201 Created)

```json
{
  "id": "3f9c962a-6b71-41d2-a9e0-b98c0c245e4a",
  "full_name": "Wilson Ventas Quevedo",
  "email": "wilveque@ccp.com.co",
  "id_type": "CC",
  "identification": "101448745887",
  "phone": "+57 2325248847",
  "username": "wilveque",
  "role": "SELLER"
}
```

| Field     | Type   | Description                              |
|-----------|--------|------------------------------------------|
| id        | UUID   | Unique ID of the newly created seller    |
| role      | string | Always set to `SELLER`                   |

---

### ❌ Error Responses

#### 400 Bad Request (Business Validation Error)

```json
{
  "detail": "Username already exists"
}
```

---

#### 422 Unprocessable Entity (Pydantic Validation Error)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    },
    {
      "loc": ["body", "full_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

#### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

## 📄 List All Sellers API

### `GET /api/v1/sales/sellers`

Retrieve a list of all sellers in the system.

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
    "full_name": "Ana María López",
    "email": "amlopez@ccp.com.co",
    "username": "amlopez",
    "phone": "+57 3225584123",
    "id_type": "CC",
    "identification": "101012345678"
  }
]
```

| Field           | Type   | Description                            |
|------------------|--------|----------------------------------------|
| id               | UUID   | Unique identifier of the seller        |
| full_name        | string | Seller’s full name                     |
| email            | string | Email address                          |
| username         | string | Username                               |
| phone            | string | Phone number                           |
| id_type          | string | Type of ID (e.g. `CC`, `CE`, `NIT`)    |
| identification   | string | Document/ID number                     |

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
  "product_id": "ae3f541e-b3b5-4cb6-a018-02f58bbd0c2e",
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
    "product_id": "ae3f541e-b3b5-4cb6-a018-02f58bbd0c2e",
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
    "product_id": "f61cc002-6d5d-4d10-a511-9c83d3b8c76e",
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
| product_id    | UUID     | Associated product                      |
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
