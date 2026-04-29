from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.modules.users.model import AuthProvider


class SignupEmailRequest(BaseModel):
    """Schema for email/password signup"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class LoginEmailRequest(BaseModel):
    """Schema for email/password login"""
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """Schema for Google OAuth"""
    id_token: str


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """Schema for user profile response"""
    id: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    profile_picture: Optional[str]
    is_active: bool
    is_verified: bool
    auth_provider: AuthProvider
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    username: Optional[str] = None
    profile_picture: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Schema for changing password"""
    old_password: str
    new_password: str = Field(..., min_length=8)


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
