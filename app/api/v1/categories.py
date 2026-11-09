from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.db.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Kategorie vybavení"])


@router.get("/", response_model=List[CategoryResponse], summary="Seznam všech kategorií")
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Vrátí seznam všech evidovaných kategorií s ceníkovými sazbami."""
    service = CategoryService(db)
    return service.get_categories(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse, summary="Detail kategorie")
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Vrátí detail konkrétní kategorie."""
    service = CategoryService(db)
    return service.get_category_by_id(category_id)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Vytvoření nové kategorie (chráněno)")
def create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Vytvoří novou kategorii vybavení včetně ceníku (vyžaduje přihlášení)."""
    service = CategoryService(db)
    return service.create_category(cat_in)


@router.put("/{category_id}", response_model=CategoryResponse, summary="Úprava kategorie (chráněno)")
def update_category(
    category_id: int,
    cat_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upraví název, popis nebo ceny kategorie (vyžaduje přihlášení)."""
    service = CategoryService(db)
    return service.update_category(category_id, cat_in)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Smazání prázdné kategorie (chráněno)")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Smaže kategorii, pokud k ní není přiřazeno žádné vybavení (vyžaduje přihlášení)."""
    service = CategoryService(db)
    service.delete_category(category_id)
    return None
