from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.db.models.equipment import EquipmentStatus
from app.schemas.category import CategoryResponse


class EquipmentBase(BaseModel):
    inventory_number: str = Field(..., min_length=1, max_length=50, description="Unikátní inventární číslo")
    category_id: int = Field(..., description="ID kategorie vybavení")
    size: str = Field(..., min_length=1, max_length=30, description="Velikost/délka např. 170 cm")
    purchase_year: int = Field(..., ge=1990, le=2100)
    condition_state: str = Field("Výborný", max_length=100)
    status: EquipmentStatus = EquipmentStatus.AVAILABLE
    reservation_code: Optional[str] = Field(None, max_length=50, description="Kód rezervace např. REZ-2026-1042")
    reservation_customer: Optional[str] = Field(None, max_length=150, description="Jméno a telefon zákazníka")
    reservation_note: Optional[str] = Field(None, max_length=200, description="Termín a tarif rezervace")


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    inventory_number: Optional[str] = Field(None, min_length=1, max_length=50)
    category_id: Optional[int] = None
    size: Optional[str] = Field(None, min_length=1, max_length=30)
    purchase_year: Optional[int] = Field(None, ge=1990, le=2100)
    condition_state: Optional[str] = Field(None, max_length=100)
    status: Optional[EquipmentStatus] = None
    reservation_code: Optional[str] = None
    reservation_customer: Optional[str] = None
    reservation_note: Optional[str] = None


class EquipmentResponse(EquipmentBase):
    id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


class EquipmentReserveRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100, description="Jméno a příjmení zákazníka")
    customer_phone: str = Field(..., min_length=5, max_length=30, description="Telefonní kontakt zákazníka")
    start_date: str = Field(..., description="Datum začátku výpůjčky (YYYY-MM-DD)")
    rental_block: str = Field("FULLDAY", description="Zvolený tarif např. FULLDAY, WEEKEND")
    note: Optional[str] = Field(None, max_length=200, description="Doplňující poznámka zákazníka")
