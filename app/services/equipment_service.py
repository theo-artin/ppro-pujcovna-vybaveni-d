from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.equipment import EquipmentItem, EquipmentStatus
from app.db.repositories.equipment_repo import EquipmentRepository
from app.db.repositories.category_repo import CategoryRepository
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate


class EquipmentService:
    def __init__(self, db: Session):
        self.repo = EquipmentRepository(db)
        self.category_repo = CategoryRepository(db)

    def get_items(
        self,
        category_id: Optional[int] = None,
        status_filter: Optional[EquipmentStatus] = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentItem]:
        return self.repo.get_all(
            category_id=category_id,
            status=status_filter,
            include_deleted=include_deleted,
            skip=skip,
            limit=limit
        )

    def get_item_by_id(self, item_id: int) -> EquipmentItem:
        item = self.repo.get_by_id(item_id)
        if not item or item.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kus vybavení s ID {item_id} nebyl nalezen."
            )
        return item

    def create_item(self, item_in: EquipmentCreate) -> EquipmentItem:
        # 1. Kontrola existence kategorie
        category = self.category_repo.get_by_id(item_in.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kategorie s ID {item_in.category_id} neexistuje."
            )

        # 2. Kontrola unikátnosti inventárního čísla
        existing = self.repo.get_by_inventory_number(item_in.inventory_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kus s inventárním číslem '{item_in.inventory_number}' již existuje."
            )

        db_item = EquipmentItem(
            inventory_number=item_in.inventory_number,
            category_id=item_in.category_id,
            size=item_in.size,
            purchase_year=item_in.purchase_year,
            condition_state=item_in.condition_state,
            status=item_in.status,
            reservation_code=item_in.reservation_code,
            reservation_customer=item_in.reservation_customer,
            reservation_note=item_in.reservation_note,
        )
        return self.repo.create(db_item)

    def update_item(self, item_id: int, item_in: EquipmentUpdate) -> EquipmentItem:
        item = self.get_item_by_id(item_id)

        if item_in.inventory_number is not None and item_in.inventory_number != item.inventory_number:
            existing = self.repo.get_by_inventory_number(item_in.inventory_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kus s inventárním číslem '{item_in.inventory_number}' již existuje."
                )
            item.inventory_number = item_in.inventory_number

        if item_in.category_id is not None and item_in.category_id != item.category_id:
            category = self.category_repo.get_by_id(item_in.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kategorie s ID {item_in.category_id} neexistuje."
                )
            item.category_id = item_in.category_id

        if item_in.size is not None:
            item.size = item_in.size
        if item_in.purchase_year is not None:
            item.purchase_year = item_in.purchase_year
        if item_in.condition_state is not None:
            item.condition_state = item_in.condition_state

        if "reservation_code" in item_in.model_fields_set:
            item.reservation_code = item_in.reservation_code
        if "reservation_customer" in item_in.model_fields_set:
            item.reservation_customer = item_in.reservation_customer
        if "reservation_note" in item_in.model_fields_set:
            item.reservation_note = item_in.reservation_note

        if item_in.status is not None:
            item.status = item_in.status
            # Pokud se stav vrací na AVAILABLE (uvolnění kusu ze servisu / vrácení / zrušení rezervace),
            # a nebyla explicitně předána nová rezervace, vyčistíme rezervační údaje
            if item.status == EquipmentStatus.AVAILABLE and "reservation_code" not in item_in.model_fields_set:
                item.reservation_code = None
                item.reservation_customer = None
                item.reservation_note = None

        return self.repo.update(item)

    def soft_delete_item(self, item_id: int) -> EquipmentItem:
        item = self.get_item_by_id(item_id)
        if item.status == EquipmentStatus.RENTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nelze vyřadit kus, který je právě zapůjčen zákazníkovi."
            )
        item.status = EquipmentStatus.RETIRED
        return self.repo.soft_delete(item)

    def reserve_item(
        self,
        item_id: int,
        customer_name: str,
        customer_phone: str,
        start_date: str,
        rental_block: str,
        note: Optional[str] = None
    ) -> EquipmentItem:
        item = self.get_item_by_id(item_id)
        if item.status != EquipmentStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kus '{item.inventory_number}' není volný k rezervaci (aktuální status: {item.status.value})."
            )

        import random, datetime
        year = datetime.datetime.now().year
        rand_num = random.randint(1000, 9999)
        code = f"REZ-{year}-{rand_num}"

        block_desc = f"{start_date} · {rental_block}"
        if note and note.strip():
            block_desc += f" ({note.strip()})"

        item.status = EquipmentStatus.RESERVED
        item.reservation_code = code
        item.reservation_customer = f"{customer_name.strip()} ({customer_phone.strip()})"
        item.reservation_note = block_desc

        return self.repo.update(item)
