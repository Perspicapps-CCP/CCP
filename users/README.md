## 🔐 User Login API

### `POST /api/v1/users/login`

Authenticate a user using their username and password. Available for all roles: `STAFF`, `SELLER`, and `CLIENT`.

---

### 📥 Request Body

```json
{
  "username": "string",
  "password": "string"
}
```

| Field    | Type   | Required | Description     |
| -------- | ------ | -------- | --------------- |
| username | string | ✅       | User's username |
| password | string | ✅       | User's password |

---

### 📤 Response (200 OK)

```json
{
  "access_token": "jwt_token_here",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "johndoe",
    "email": "john@example.com",
    "role": "SELLER"
  }
}
```

| Field        | Type   | Description                         |
| ------------ | ------ | ----------------------------------- |
| access_token | string | JWT token for authenticated use     |
| user         | object | Basic user information              |
| user.id      | UUID   | Unique identifier (UUID format)     |
| user.role    | string | One of: `STAFF`, `SELLER`, `CLIENT` |

---

### ❌ Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Invalid credentials"
}
```

## 👤 Get User Profile API

### `GET /api/v1/users/profile`

Retrieve the authenticated user's profile information.

---

### 🔐 Authentication

Requires Bearer Token (JWT) in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### 📤 Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john@example.com",
  "role": "CLIENT"
}
```

| Field    | Type   | Description                         |
| -------- | ------ | ----------------------------------- |
| id       | UUID   | User's unique identifier            |
| username | string | User's username                     |
| email    | string | User's email address                |
| role     | string | One of: `STAFF`, `SELLER`, `CLIENT` |

---

### ❌ Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Invalid or expired token.."
}
```

## ➕ Create Seller API

### `POST /api/v1/users/sellers`

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

| Field          | Type   | Required | Description                               |
| -------------- | ------ | -------- | ----------------------------------------- |
| full_name      | string | ✅       | Seller’s full name                        |
| email          | string | ✅       | Seller’s email address                    |
| id_type        | string | ✅       | Type of ID (e.g. `CC`, `CE`, `NIT`, etc.) |
| identification | string | ✅       | ID number                                 |
| phone          | string | ✅       | Phone number (e.g. with country code)     |
| username       | string | ✅       | Username for login                        |

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

| Field | Type   | Description                           |
| ----- | ------ | ------------------------------------- |
| id    | UUID   | Unique ID of the newly created seller |
| role  | string | Always set to `SELLER`                |

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

### `GET /api/v1/users/sellers`

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

| Field          | Type   | Description                         |
| -------------- | ------ | ----------------------------------- |
| id             | UUID   | Unique identifier of the seller     |
| full_name      | string | Seller’s full name                  |
| email          | string | Email address                       |
| username       | string | Username                            |
| phone          | string | Phone number                        |
| id_type        | string | Type of ID (e.g. `CC`, `CE`, `NIT`) |
| identification | string | Document/ID number                  |

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

## 👤 Client Sign Up API

### `POST /api/v1/users/clients/`

Create a new client using the provided personal, contact, and address information.

---

### 🔐 Authentication

❌ No authentication required.

---

### 📥 Request Body

```json
{
  "full_name": "Cosme Fulanito",
  "email": "cosme@ccp.com.co",
  "id_type": "CC",
  "identification": "101000000000",
  "phone": "+57 3000000000",
  "username": "cosmef",
  "address": {
    "id": "de305d54-75b4-431b-adb2-eb6b9e546014",
    "line": "Cra. 7 #123-45",
    "neighborhood": "Chapinero",
    "city": "Bogotá",
    "state": "Cundinamarca",
    "country": "Colombia",
    "latitude": 4.6482837,
    "longitude": -74.247894
  },
  "password": "P@ssw0rd!"
}
```

| Field          | Type   | Required                                                 | Description                               |
| -------------- | ------ | -------------------------------------------------------- | ----------------------------------------- |
| full_name      | string | ✅                                                       | Client’s full name                        |
| email          | string | ✅                                                       | Client’s email address                    |
| id_type        | string | ✅                                                       | Type of ID (e.g. `CC`, `CE`, `NIT`, etc.) |
| identification | string | ✅                                                       | ID number                                 |
| phone          | string | ✅                                                       | Phone number (e.g. with country code)     |
| username       | string | ✅                                                       | Username for login                        |
| address        | object | ✅                                                       | Address details (see fields below)        |
| password       | string | ✅ Password (at least 8 characters, 1 special character) |

#### 🔹 Address Object

| Field        | Type   | Required | Description               |
| ------------ | ------ | -------- | ------------------------- |
| id           | UUID   | ✅       | Unique ID for the address |
| line         | string | ✅       | Street address            |
| neighborhood | string | ✅       | Neighborhood name         |
| city         | string | ✅       | City name                 |
| state        | string | ✅       | State or department       |
| country      | string | ✅       | Country name              |
| latitude     | float  | ✅       | Latitude coordinate       |
| longitude    | float  | ✅       | Longitude coordinate      |

---

### 📤 Response (201 Created)

```json
{
  "id": "83f3e840-4c9e-4c21-babc-c5aa2cb3af19",
  "full_name": "Cosme Fulanito",
  "email": "cosme@ccp.com.co",
  "id_type": "CC",
  "identification": "101000000000",
  "phone": "+57 3000000000",
  "username": "cosmef",
  "role": "CLIENT",
  "address": {
    "id": "de305d54-75b4-431b-adb2-eb6b9e546014",
    "line": "Cra. 7 #123-45",
    "neighborhood": "Chapinero",
    "city": "Bogotá",
    "state": "Cundinamarca",
    "country": "Colombia",
    "latitude": 4.6482837,
    "longitude": -74.247894
  },
  "password": "P@ssw0rd!"
}
```

| Field   | Type   | Description                                 |
| ------- | ------ | ------------------------------------------- |
| id      | UUID   | Unique ID of the newly created client       |
| role    | string | Always set to `CLIENT`                      |
| address | object | Address of the client (see structure above) |
