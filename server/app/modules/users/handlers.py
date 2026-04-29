from fastapi import HTTPException, status
from datetime import timedelta
from sqlalchemy.orm import Session
from app.modules.users.schemas import (
    SignupEmailRequest,
    LoginEmailRequest,
    GoogleAuthRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
)
from app.modules.users.service import AuthService
from app.modules.users.repository import UserRepository
from app.modules.users.model import AuthProvider
from app.config import settings


class AuthHandler:
    """Handler for authentication endpoints"""

    @staticmethod
    def signup_email(request: SignupEmailRequest, db: Session) -> TokenResponse:
        """Handle email/password signup"""
        
        # Check if email already exists
        if UserRepository.user_exists(db, request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password and create user
        hashed_password = AuthService.hash_password(request.password)
        user = UserRepository.create_user(
            db,
            email=request.email,
            hashed_password=hashed_password,
            full_name=request.full_name,
            auth_provider=AuthProvider.EMAIL,
        )

        # Generate token
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        return AuthService.create_user_response(user, access_token)

    @staticmethod
    def login_email(request: LoginEmailRequest, db: Session) -> TokenResponse:
        """Handle email/password login"""
        # Get user by email
        user = UserRepository.get_user_by_email(db, request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if user has password (might be OAuth user)
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses OAuth authentication",
            )

        # Verify password
        if not AuthService.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        # Generate token
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        return AuthService.create_user_response(user, access_token)

    @staticmethod
    def google_auth(request: GoogleAuthRequest, db: Session) -> TokenResponse:
        """Handle Google OAuth authentication"""
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured",
            )

        # Verify Google token
        idinfo = AuthService.verify_google_token(request.id_token)
        if not idinfo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
            )

        google_id = idinfo.get("sub")
        email = idinfo.get("email")

        # Check if user exists by Google ID
        user = UserRepository.get_user_by_google_id(db, google_id)
        if user:
            # Existing user, just log them in
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated",
                )
        else:
            # Check if email is already registered
            existing_user = UserRepository.get_user_by_email(db, email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered with different auth method",
                )

            # Create new user
            user = UserRepository.create_user(
                db,
                email=email,
                username=idinfo.get("email").split("@")[0],
                full_name=idinfo.get("name"),
                profile_picture=idinfo.get("picture"),
                auth_provider=AuthProvider.GOOGLE,
                google_id=google_id,
            )

        # Generate token
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        return AuthService.create_user_response(user, access_token)


class UserHandler:
    """Handler for user endpoints"""

    @staticmethod
    def get_profile(user_id: str, db: Session) -> UserResponse:
        """Get user profile"""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    def update_profile(
        user_id: str, request: UserUpdateRequest, db: Session
    ) -> UserResponse:
        """Update user profile"""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if username is already taken
        if request.username and request.username != user.username:
            if UserRepository.get_user_by_username(db, request.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

        # Update user
        user = UserRepository.update_user(
            db,
            user,
            full_name=request.full_name,
            username=request.username,
            profile_picture=request.profile_picture,
        )
        return user

    @staticmethod
    def change_password(
        user_id: str, request: ChangePasswordRequest, db: Session
    ) -> dict:
        """Change user password"""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses OAuth authentication",
            )

        # Verify old password
        if not AuthService.verify_password(request.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
            )

        # Update password
        new_hashed_password = AuthService.hash_password(request.new_password)
        UserRepository.update_user(db, user, hashed_password=new_hashed_password)

        return {"message": "Password updated successfully"}
