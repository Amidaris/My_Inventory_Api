# Auth API – Documentation (POC)

## Endpoints

### 1. Health check
```bash
GET /health
```

- Response:
```json
{ "status": "ok" }
```

### 2. Register (New user)
```bash
POST /auth/register
```

- Body: application/json

  { 
    "username": "string", 
    "email": "string", 
    "password": "string", 
    "confirm_password": "string" 
  }

- Response: 201 Created
```json
{
  "id": 1, 
  "email": "user@example.com", 
  "role": "user"
}
```

- Notes:

- email must be a valid email format

- password must have at least 8 characters

- password and confirm_password must match

- username and email must be unique


### 3. Login
```bash
POST /auth/login
```

- Body: application/x-www-form-urlencoded

    - username: string

    - password: string

- Response:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

- Notes:

    Access token expires in 15 minutes (ACCESS_TOKEN_EXPIRE_MINUTES)
    
    Passwords are hashed using bcrypt

### 4. Refresh token
```bash
POST /auth/refresh
```

- Body: application/json
```json
{
  "refresh_token": "<jwt>"
}
```

- Response:
```json
{
  "access_token": "<new_jwt>",
  "token_type": "bearer"
}
```
- Notes:

    Refresh token expires in 7 days (REFRESH_TOKEN_EXPIRE_DAYS)

    Stateless – server does not store tokens

### 5. Protected endpoint
```bash
GET /protected
```

- Header: Authorization: Bearer <access_token>

- Response:
```json
{
  "id": 1,
  "username": "user",
  "email": "user@example.com",
  "full_name": "User",
  "role": "user",
  "disabled": false
}
```
- Notes:

    Invalid token → 401

    Disabled user → 403