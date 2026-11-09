from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.core.security import create_access_token
from app.db.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autentizace"])


@router.post("/login", response_model=Token, summary="Přihlášení uživatele (OAuth2 kompatibilní)")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Přihlášení obsluhy půjčovny. Vrací JWT bearer token.
    Funguje také přímo s tlačítkem 'Authorize' v horní části Swagger /docs.
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nesprávné uživatelské jméno nebo heslo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uživatelský účet je deaktivován."
        )

    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse, summary="Informace o aktuálně přihlášeném uživateli")
def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Vrátí profil přihlášeného uživatele (obsluhy / administrátora)."""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Registrace nového uživatele")
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Založí nový uživatelský účet obsluhy."""
    auth_service = AuthService(db)
    return auth_service.create_user(user_in)
