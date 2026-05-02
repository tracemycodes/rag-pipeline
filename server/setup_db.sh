#!/bin/bash
# Database setup script

cd /Users/newapple/Documents/GitHub/rag-pipeline/server

# Activate virtual environment
source .venv/bin/activate

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
fi

# Initialize database by running the app startup
python << 'EOF'
from app.database import Base, engine
from app.modules.users.model import User

# Create all tables
Base.metadata.create_all(bind=engine)
print("✓ Database tables created successfully")

# Verify connection
try:
    with engine.connect() as conn:
        result = conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        print("✓ Database connection verified")
except Exception as e:
    print(f"✗ Database connection error: {e}")

# List all tables
inspector = __import__('sqlalchemy').inspect(engine)
tables = inspector.get_table_names()
print(f"✓ Tables in database: {tables}")
EOF

echo ""
echo "Database setup complete!"
echo "You can now start the server with: uvicorn main:app --reload"
