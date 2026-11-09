from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    halfday_price: float = Field(..., ge=0, description="Cena za půlden (Kč)")
    daily_price: float = Field(..., ge=0, description="Cena za 1 kalendářní den (Kč)")
    weekend_price: float = Field(..., ge=0, description="Cena za víkendový balíček (Kč)")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    halfday_price: Optional[float] = Field(None, ge=0)
    daily_price: Optional[float] = Field(None, ge=0)
    weekend_price: Optional[float] = Field(None, ge=0)


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
