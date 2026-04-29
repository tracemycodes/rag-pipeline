from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.users.dependencies import get_current_user
from app.modules.users.schemas import (
    SignupEmailRequest,
    LoginEmailRequest,
    GoogleAuthRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
    ErrorResponse,
)
from app.modules.users.handlers import AuthHandler, UserHandler
from app.modules.users.model import User

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# Authentication Endpoints
@router.post(
    "/auth/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
    summary="Sign up with email and password",
)
def signup(request: SignupEmailRequest, db: Session = Depends(get_db)):
    """
    Create a new user account with email and password.
    
    - **email**: User's email address (must be unique)
    - **password**: Password (minimum 8 characters)
    - **full_name**: Optional full name
    """
    return AuthHandler.signup_email(request, db)


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
    summary="Login with email and password",
)
def login(request: LoginEmailRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email and password.
    
    Returns JWT access token on successful login.
    """
    return AuthHandler.login_email(request, db)


@router.post(
    "/auth/google",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Authenticate with Google OAuth",
)
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with Google OAuth ID token.
    
    - **id_token**: Google ID token from frontend authentication
    
    Creates new user account if it doesn't exist.
    """
    return AuthHandler.google_auth(request, db)


# User Profile Endpoints
@router.get(
    "/profile",
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get current user profile",
)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.put(
    "/profile",
    response_model=UserResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Update user profile",
)
def update_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile information.
    
    - **full_name**: Optional new full name
    - **username**: Optional new username (must be unique)
    - **profile_picture**: Optional new profile picture URL
    
    Requires valid JWT token in Authorization header.
    """
    return UserHandler.update_profile(current_user.id, request, db)


@router.post(
    "/password/change",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Change user password",
)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change the current user's password.
    
    - **old_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    
    Requires valid JWT token in Authorization header.
    """
    return UserHandler.change_password(current_user.id, request, db)