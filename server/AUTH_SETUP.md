# User Authentication System Documentation

## Overview

This authentication system provides a complete JWT-based authentication flow with support for:

- Email/Password signup and login
- Google OAuth 2.0 authentication
- User profile management
- Password change functionality

## Architecture

The user module follows a clean architecture pattern:

```
users/
├── model.py         # SQLAlchemy ORM models
├── schemas.py       # Pydantic request/response schemas
├── service.py       # Business logic (JWT, password hashing, OAuth verification)
├── repository.py    # Database operations
├── handlers.py      # API request handlers
├── routes.py        # API route definitions
└── dependencies.py  # FastAPI dependencies (JWT validation)
```

## Setup Instructions

### 1. Install Dependencies

Update your virtual environment with the new dependencies:

```bash
pip install -r requirements.txt
# or
poetry install  # if using pyproject.toml
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

**Important settings:**

- `SECRET_KEY`: Use a strong random string (generate with `openssl rand -hex 32`)
- `DATABASE_URL`: Configure your database connection
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: Get from Google Cloud Console

### 3. Database Setup

The database tables are automatically created on app startup. If you need to reset:

```bash
python -c "from server.app.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

## API Endpoints

### Authentication

#### Signup (Email/Password)

```
POST /api/v1/users/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "john_doe",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "auth_provider": "email",
    "created_at": "2024-06-01T10:00:00",
    "updated_at": "2024-06-01T10:00:00"
  }
}
```

#### Login (Email/Password)

```
POST /api/v1/users/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {...}
}
```

#### Google OAuth

```
POST /api/v1/users/auth/google
Content-Type: application/json

{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ..."
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {...}
}
```

### User Profile

#### Get Profile

```
GET /api/v1/users/profile
Authorization: Bearer {access_token}

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "profile_picture": null,
  "is_active": true,
  "is_verified": false,
  "auth_provider": "email",
  "created_at": "2024-06-01T10:00:00",
  "updated_at": "2024-06-01T10:00:00"
}
```

#### Update Profile

```
PUT /api/v1/users/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "John Updated",
  "username": "john_updated",
  "profile_picture": "https://example.com/pic.jpg"
}

Response: 200 OK
{...updated user...}
```

#### Change Password

```
POST /api/v1/users/password/change
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "securepassword123",
  "new_password": "newsecurepassword123"
}

Response: 200 OK
{
  "message": "Password updated successfully"
}
```

## Security Considerations

1. **JWT Token**:
   - Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30)
   - Always use HTTPS in production
   - Keep `SECRET_KEY` secure and rotate regularly

2. **Password Security**:
   - Passwords are hashed using bcrypt
   - Minimum 8 characters required
   - Implement rate limiting on login attempts

3. **Google OAuth**:
   - Verify `id_token` server-side (already implemented)
   - Use HTTPS redirect URIs
   - Never expose client secrets in frontend code

4. **Database**:
   - Use strong database credentials
   - Enable SSL for database connections in production
   - Regular backups

## User Model Fields

| Field           | Type          | Description                          |
| --------------- | ------------- | ------------------------------------ |
| id              | String (UUID) | Unique user identifier               |
| email           | String        | User's email (unique)                |
| username        | String        | Username (unique)                    |
| full_name       | String        | User's full name                     |
| hashed_password | String        | Bcrypt hashed password               |
| profile_picture | String        | URL to profile picture               |
| is_active       | Boolean       | Account active status                |
| is_verified     | Boolean       | Email verification status            |
| auth_provider   | Enum          | Authentication method (email/google) |
| google_id       | String        | Google unique ID (for OAuth)         |
| created_at      | DateTime      | Account creation timestamp           |
| updated_at      | DateTime      | Last update timestamp                |

## Frontend Integration

### Using JWT Token

```javascript
// Store token from login/signup response
localStorage.setItem("access_token", response.access_token);

// Send with requests
fetch("/api/v1/users/profile", {
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
  },
});
```

### Google OAuth (Frontend)

```javascript
// After Google sign-in
const id_token = googleUser.getAuthResponse().id_token;

fetch("/api/v1/users/auth/google", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ id_token }),
});
```

## Extending the System

### Add Email Verification

1. Create migration to add `email_verification_token` field
2. Send verification email on signup
3. Add `/auth/verify-email` endpoint

### Add Refresh Tokens

1. Store refresh tokens in database
2. Create `/auth/refresh` endpoint
3. Implement token refresh flow

### Add Two-Factor Authentication (2FA)

1. Add `mfa_enabled` and `mfa_secret` to User model
2. Implement TOTP using `pyotp` library
3. Add `/auth/2fa/setup` and `/auth/2fa/verify` endpoints

### Add Rate Limiting

1. Use `slowapi` library
2. Apply limits to login/signup endpoints
3. Implement account lockout after N failed attempts

## Troubleshooting

### "Invalid Google Token"

- Verify `GOOGLE_CLIENT_ID` is correct
- Check token hasn't expired
- Ensure frontend sends correct id_token

### "Email already registered"

- User already has account with this email
- Suggest password reset or Google auth if email was used with different method

### "Invalid JWT Token"

- Token expired (request new token via login)
- Token was tampered with
- `SECRET_KEY` changed (invalidates all existing tokens)

## Production Checklist

- [ ] Set strong `SECRET_KEY` using cryptographically secure random value
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Implement rate limiting
- [ ] Add email verification
- [ ] Add CORS restrictions (don't use allow_origins=["*"])
- [ ] Implement password reset flow
- [ ] Add audit logging for security events
- [ ] Regular security audits
- [ ] Keep dependencies updated
