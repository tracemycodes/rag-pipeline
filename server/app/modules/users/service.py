from datetime import datetime, timedelta
from typing import Optional
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt
from google.auth.transport import requests
from google.oauth2 import id_token
from app.config import settings
from app.modules.users.model import User, AuthProvider
from sqlalchemy.orm import Session


# Password hashing context - using argon2 for better security and no 72-byte limit
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using argon2"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash using argon2"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def verify_google_token(id_token_str: str) -> Optional[dict]:
        """Verify Google ID token and return user info"""
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str, requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            return idinfo
        except Exception as e:
            print(f"Error verifying Google token: {e}")
            return None

    @staticmethod
    def generate_user_id() -> str:
        """Generate a unique user ID"""
        return str(uuid.uuid4())

    @staticmethod
    def create_user_response(user: User, access_token: str) -> dict:
        """Create token response with user data"""
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "profile_picture": user.profile_picture,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "auth_provider": user.auth_provider,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            },
        }
