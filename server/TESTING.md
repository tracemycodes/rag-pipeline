# API Testing Guide

This guide shows how to test the authentication API endpoints.

## Quick Start

### 1. Start the Server

```bash
cd server
source .venv/bin/activate
uvicorn main:app --reload
```

Server will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs
Alternative docs: http://localhost:8000/redoc

### 2. Test Endpoints

## Using cURL

### Signup with Email/Password

```bash
curl -X POST "http://localhost:8000/api/v1/users/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "username": "testuser",
    "full_name": "Test User"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "abc123...",
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "profile_picture": null,
    "is_active": true,
    "is_verified": false,
    "auth_provider": "email",
    "created_at": "2024-06-01T10:00:00",
    "updated_at": "2024-06-01T10:00:00"
  }
}
```

### Login with Email/Password

```bash
curl -X POST "http://localhost:8000/api/v1/users/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Get User Profile

```bash
# Replace TOKEN with the access_token from signup/login
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN"
```

### Update User Profile

```bash
curl -X PUT "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "username": "newusername",
    "profile_picture": "https://example.com/picture.jpg"
  }'
```

### Change Password

```bash
curl -X POST "http://localhost:8000/api/v1/users/password/change" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "testpassword123",
    "new_password": "newpassword456"
  }'
```

## Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/users"

# Signup
signup_data = {
    "email": "test@example.com",
    "password": "testpassword123",
    "username": "testuser",
    "full_name": "Test User"
}

response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
result = response.json()
access_token = result["access_token"]
print(f"Token: {access_token}")

# Get profile
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/profile", headers=headers)
profile = response.json()
print(f"Profile: {json.dumps(profile, indent=2)}")

# Update profile
update_data = {
    "full_name": "Updated Name",
    "username": "newusername"
}
response = requests.put(f"{BASE_URL}/profile", json=update_data, headers=headers)
print(f"Update response: {response.json()}")
```

## Using Postman

1. **Create a new request collection**

2. **Signup Endpoint:**
   - Method: POST
   - URL: `{{base_url}}/api/v1/users/auth/signup`
   - Body (raw JSON):

   ```json
   {
     "email": "test@example.com",
     "password": "testpassword123",
     "username": "testuser",
     "full_name": "Test User"
   }
   ```

   - In Tests tab, add:

   ```javascript
   var jsonData = pm.response.json();
   pm.environment.set("access_token", jsonData.access_token);
   ```

3. **Get Profile:**
   - Method: GET
   - URL: `{{base_url}}/api/v1/users/profile`
   - Headers tab, add: `Authorization: Bearer {{access_token}}`

## Test Scenarios

### Scenario 1: Complete Auth Flow

```bash
# 1. Signup
curl -X POST "http://localhost:8000/api/v1/users/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepass123",
    "username": "newuser",
    "full_name": "New User"
  }' | jq '.access_token' > token.txt

TOKEN=$(cat token.txt | tr -d '"')

# 2. Get profile
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN"

# 3. Update profile
curl -X PUT "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Updated User"}'

# 4. Change password
curl -X POST "http://localhost:8000/api/v1/users/password/change" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "securepass123",
    "new_password": "newsecurepass456"
  }'

# 5. Login with new password
curl -X POST "http://localhost:8000/api/v1/users/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "newsecurepass456"
  }'
```

### Scenario 2: Error Handling

```bash
# Test: Duplicate email
curl -X POST "http://localhost:8000/api/v1/users/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "pass123",
    "username": "another_user"
  }'
# Expected: 400 Bad Request - "Email already registered"

# Test: Weak password
curl -X POST "http://localhost:8000/api/v1/users/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "123",
    "username": "testuser2"
  }'
# Expected: 422 Validation Error

# Test: Invalid login
curl -X POST "http://localhost:8000/api/v1/users/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "wrongpassword"
  }'
# Expected: 401 Unauthorized - "Invalid email or password"

# Test: Invalid token
curl -X GET "http://localhost:8000/api/v1/users/profile" \
  -H "Authorization: Bearer invalid_token"
# Expected: 401 Unauthorized - "Invalid authentication credentials"
```

## Expected Status Codes

| Operation       | Success | Error         |
| --------------- | ------- | ------------- |
| Signup          | 201     | 400, 422      |
| Login           | 200     | 401, 400      |
| Get Profile     | 200     | 401, 404      |
| Update Profile  | 200     | 400, 401, 404 |
| Change Password | 200     | 400, 401, 404 |
| Google Auth     | 200     | 400, 401, 500 |

## Debugging

### Enable Debug Logging

Add to your code before running the app:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### Check Token Contents

```python
from jose import jwt
import json

token = "your_token_here"
SECRET_KEY = "your-secret-key"

try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print(json.dumps(payload, indent=2))
except Exception as e:
    print(f"Error: {e}")
```

### Database Inspection

```python
from sqlalchemy import create_engine, inspect
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# List all tables
print(inspector.get_table_names())

# List users
from app.database import SessionLocal
from app.modules.users.model import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f"{user.id}: {user.email} ({user.username})")
```

## Common Issues

### 1. "Email already registered"

- User already exists with that email
- Solution: Use a different email or reset the database

### 2. "Invalid Google token"

- Google Client ID not configured correctly
- Token expired (Google tokens expire)
- Solution: Check .env and regenerate token

### 3. "JWT token expired"

- Token was created more than 30 minutes ago (default)
- Solution: Login again to get new token

### 4. "User account is deactivated"

- User's is_active field is False
- Solution: Manually set is_active=True in database

### 5. CORS errors in frontend

- Frontend and backend on different origins
- Solution: Already enabled in main.py, or restrict origins for production
