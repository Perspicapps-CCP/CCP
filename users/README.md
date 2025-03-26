## 🔐 User Login API

### `POST /api/v1/users/login`

Authenticate a user using their username and password. Available for all roles: `STAFF`, `SELLER`, and `BUYER`.

---

### 📥 Request Body

```json
{
  "username": "string",
  "password": "string"
}
```

| Field     | Type   | Required | Description         |
|-----------|--------|----------|---------------------|
| username  | string | ✅       | User's username     |
| password  | string | ✅       | User's password     |

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

| Field         | Type   | Description                              |
|---------------|--------|------------------------------------------|
| access_token  | string | JWT token for authenticated use          |
| user          | object | Basic user information                   |
| user.id       | UUID   | Unique identifier (UUID format)          |
| user.role     | string | One of: `STAFF`, `SELLER`, `BUYER`       |

---

### ❌ Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Invalid credentials"
}
```

#### 403 Forbidden

```json
{
  "detail": "User role is not allowed"
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
  "role": "BUYER"
}
```

| Field     | Type   | Description                          |
|-----------|--------|--------------------------------------|
| id        | UUID   | User's unique identifier             |
| username  | string | User's username                      |
| email     | string | User's email address                 |
| role      | string | One of: `STAFF`, `SELLER`, `BUYER`   |

---

### ❌ Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden

```json
{
  "detail": "Invalid or expired token."
}
```
