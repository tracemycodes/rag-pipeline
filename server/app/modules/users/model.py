from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base
from datetime import datetime
import enum


class AuthProvider(str, enum.Enum):
    """Authentication provider enum"""
    EMAIL = "email"
    GOOGLE = "google"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    auth_provider = Column(SQLEnum(AuthProvider), default=AuthProvider.EMAIL)
    google_id = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Config:
        from_attributes = True
