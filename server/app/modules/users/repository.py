from sqlalchemy.orm import Session
from app.modules.users.model import User, AuthProvider
from typing import Optional


class UserRepository:
    """Repository for user database operations"""

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        hashed_password: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        auth_provider: AuthProvider = AuthProvider.EMAIL,
        google_id: Optional[str] = None,
        profile_picture: Optional[str] = None,
    ) -> User:
        """Create a new user"""
        user_id = __import__("uuid").uuid4().hex
        user = User(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            username=username,
            full_name=full_name,
            auth_provider=auth_provider,
            google_id=google_id,
            profile_picture=profile_picture,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        return db.query(User).filter(User.google_id == google_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def update_user(db: Session, user: User, **kwargs) -> User:
        """Update user fields"""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Delete a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

    @staticmethod
    def user_exists(db: Session, email: str) -> bool:
        """Check if user exists by email"""
        return db.query(User).filter(User.email == email).first() is not None
