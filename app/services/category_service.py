from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.category import Category
from app.db.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def get_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.repo.get_all(skip=skip, limit=limit)

    def get_category_by_id(self, category_id: int) -> Category:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kategorie s ID {category_id} nebyla nalezena."
            )
        return category

    def create_category(self, cat_in: CategoryCreate) -> Category:
        if self.repo.get_by_name(cat_in.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kategorie s názvem '{cat_in.name}' již existuje."
            )
        
        category = Category(
            name=cat_in.name,
            description=cat_in.description,
            halfday_price=cat_in.halfday_price,
            daily_price=cat_in.daily_price,
            weekend_price=cat_in.weekend_price,
        )
        return self.repo.create(category)

    def update_category(self, category_id: int, cat_in: CategoryUpdate) -> Category:
        category = self.get_category_by_id(category_id)
        
        if cat_in.name is not None and cat_in.name != category.name:
            existing = self.repo.get_by_name(cat_in.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kategorie s názvem '{cat_in.name}' již existuje."
                )
            category.name = cat_in.name

        if cat_in.description is not None:
            category.description = cat_in.description
        if cat_in.halfday_price is not None:
            category.halfday_price = cat_in.halfday_price
        if cat_in.daily_price is not None:
            category.daily_price = cat_in.daily_price
        if cat_in.weekend_price is not None:
            category.weekend_price = cat_in.weekend_price

        return self.repo.update(category)

    def delete_category(self, category_id: int) -> None:
        category = self.get_category_by_id(category_id)
        if category.equipment_items and len(category.equipment_items) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nelze smazat kategorii, ke které je přiřazeno vybavení. Nejprve přeřaďte nebo odeberte vybavení."
            )
        self.repo.delete(category)
