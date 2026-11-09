from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_password, hash_password
from app.db.models.user import User
from app.db.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, user_in: UserCreate) -> User:
        if self.repo.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uživatelské jméno '{user_in.username}' je již obsazené."
            )
        if self.repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"E-mail '{user_in.email}' je již registrován."
            )

        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            role=user_in.role,
            is_active=user_in.is_active,
        )
        return self.repo.create(db_user)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.repo.get_by_username(username)
