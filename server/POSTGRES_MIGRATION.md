# PostgreSQL Migration Guide

## 📋 Overview

Your project has been refactored to use **PostgreSQL** instead of SQLite.

### ✅ What Changed

- **Database Driver**: SQLite → PostgreSQL (psycopg2-binary)
- **Connection String**: `sqlite:///./test.db` → `postgresql://user:password@host:port/database`
- **Configuration**: Database pooling with connection verification enabled
- **Dependencies**: Added `psycopg2-binary` for PostgreSQL support

---

## 🚀 Setup PostgreSQL

### Option 1: Using Homebrew (macOS)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify installation
psql --version
```

### Option 2: Using Docker (Recommended)

```bash
# Create and run PostgreSQL container
docker run --name rag-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=rag_pipeline \
  -p 5432:5432 \
  -d postgres:15
```

### Option 3: Docker Compose

Create `docker-compose.yml` in your server directory:

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: rag_pipeline
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Then run:

```bash
docker-compose up -d
```

---

## ⚙️ Configuration

### 1. Update `.env` file

Replace the credentials with your PostgreSQL setup:

```bash
# Local PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_pipeline

# Remote PostgreSQL (example)
DATABASE_URL=postgresql://user:password@your-db-host.com:5432/rag_pipeline
```

### 2. Supported PostgreSQL Connection Formats

```bash
# Basic
postgresql://user:password@localhost:5432/database

# With default port (5432)
postgresql://user:password@localhost/database

# SSH tunnel
postgresql://user:password@localhost:5433/database  # Use port 5433 if tunneled

# AWS RDS
postgresql://user:password@your-instance.region.rds.amazonaws.com:5432/database
```

---

## 🗄️ Database Initialization

### 1. Create Database (if not auto-created)

```bash
# Using psql command line
psql -U postgres -h localhost

# Inside psql prompt:
CREATE DATABASE rag_pipeline;
```

### 2. Start Your Application

```bash
cd /Users/newapple/Documents/GitHub/rag-pipeline/server
source .venv/bin/activate
uvicorn main:app --reload
```

**That's it!** The app will automatically create all tables on startup.

### 3. Verify Tables Created

```bash
# Connect to database
psql -U postgres -h localhost -d rag_pipeline

# Inside psql, list tables:
\dt

# Should show:
#  public | users | table | postgres
```

---

## 🧪 Test Your Setup

Run the authentication test suite:

```bash
# From the server directory with venv activated
python << 'EOF'
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/users"

# Test signup
response = requests.post(f"{BASE_URL}/auth/signup", json={
    "email": "test@example.com",
    "password": "TestPass123",
    "username": "testuser",
    "full_name": "Test User"
})

print(f"Signup Status: {response.status_code}")
if response.status_code == 201:
    print("✅ PostgreSQL is working!")
    print(response.json())
else:
    print("❌ Error:", response.json())
EOF
```

---

## 🔧 Using TablePlus with PostgreSQL

### Connection Details

- **Type**: PostgreSQL
- **Host**: `localhost`
- **Port**: `5432`
- **User**: `postgres`
- **Password**: `password` (from your .env)
- **Database**: `rag_pipeline`

### Steps

1. Open TablePlus
2. Click "Create Connection"
3. Select PostgreSQL
4. Enter above details
5. Click "Connect"

---

## 🔄 Migration from SQLite to PostgreSQL

### Export SQLite Data

```bash
# Dump SQLite database
sqlite3 test.db ".dump" > sqlite_dump.sql
```

### Import to PostgreSQL

```bash
# Connect to PostgreSQL and import
psql -U postgres -h localhost -d rag_pipeline < sqlite_dump.sql
```

Or use SQLAlchemy migration tools:

```bash
# With Alembic (if migrations are set up)
alembic upgrade head
```

---

## 🐛 Troubleshooting

### Connection Refused

```
ERROR: could not connect to server: Connection refused
```

**Solution**: Ensure PostgreSQL is running

```bash
# Homebrew
brew services start postgresql@15

# Docker
docker start rag-postgres
```

### Authentication Failed

```
FATAL: password authentication failed for user "postgres"
```

**Solution**: Check .env DATABASE_URL credentials match PostgreSQL setup

### Database Does Not Exist

```
FATAL: database "rag_pipeline" does not exist
```

**Solution**: Create the database

```bash
psql -U postgres -h localhost -c "CREATE DATABASE rag_pipeline;"
```

### Permission Denied

```
ERROR: permission denied for schema public
```

**Solution**: Grant privileges

```bash
psql -U postgres -h localhost -d rag_pipeline \
  -c "GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;"
```

---

## 📊 Performance Tuning

Your `database.py` now includes:

- **Pool size**: 10 connections
- **Max overflow**: 20 additional connections under load
- **Pool pre-ping**: Verifies connections before use (prevents "connection lost" errors)

---

## 🔒 Security Notes

1. **Change PostgreSQL password**:

   ```bash
   psql -U postgres -h localhost
   ALTER USER postgres WITH PASSWORD 'new_secure_password';
   ```

2. **Use `.env` for sensitive data** ✅ Already set up

3. **Update SECRET_KEY in production**:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Restrict database access** in production:
   - Use AWS RDS with security groups
   - Enable SSL connections
   - Use strong passwords

---

## ✅ Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] `.env` file updated with correct credentials
- [ ] `psycopg2-binary` installed in venv
- [ ] App starts without errors: `uvicorn main:app --reload`
- [ ] Tables created in database (check with TablePlus or psql)
- [ ] Signup endpoint returns 201 status
- [ ] Login endpoint returns 200 status
- [ ] Profile endpoint returns user data when authenticated

---

## 🎯 Next Steps

1. **Update your production environment** with PostgreSQL credentials
2. **Test the full authentication flow** using the test suite
3. **Configure backups** (especially important for production)
4. **Set up database monitoring** (pgAdmin, AWS CloudWatch, etc.)

---

## 📚 Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/psycopg2/)
- [SQLAlchemy PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Docker PostgreSQL](https://hub.docker.com/_/postgres)
