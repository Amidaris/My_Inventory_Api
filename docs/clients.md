# Auth API – Documentation (POC)

## Endpoints

### 1. Create new client
```bash
POST /clients
```

- Body: application/json
```json
 {
  "name": "string",
  "email": "string|null",
  "phone": "string|null",
  "address": "string",
  "nip": "string",
  "accountNumber": "string|null"
}
```

- Response: 201 Created
```json
{ 
"id": 1, 
"name": "ABC Sp. z o.o.", 
"email": null, 
"phone": null, 
"address": "ul. Testowa 1", 
"nip": "1234567890", 
"accountNumber": "12345678901234567890123456", 
"active": true 
}
```
Notes:
- nip must be valid and unique for the authenticated user (different users can have the same NIP)
- requires JWT authentication


### 2. Get cliens list (with paggination)
```bash
GET /clients?limit=20&offset=0
```
- Header: Authorization: Bearer <access_token>

- Response: 200 OK
```json
{
  "total": 3,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "name": "ACME",
      "nip": "1234567890",
      "active": true
    }
  ]
}
```
Notes:
- returns only active clients
- sorted by name ascending
- requires JWT authentication

### 3. Edit client
```bash

```

### 4. Soft delete client
```bash
DeletE /clients/{id}
```

- Header: Authorization: Bearer <access_token>

- Response: 204 No Content

- Notes:

client must belong to the authenticated user

invalid token → 401

deleting someone else’s client → 403

deleting already inactive client → 403

client not found → 404