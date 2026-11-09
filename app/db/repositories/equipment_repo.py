from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models.equipment import EquipmentItem, EquipmentStatus


class EquipmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int) -> Optional[EquipmentItem]:
        stmt = (
            select(EquipmentItem)
            .options(joinedload(EquipmentItem.category))
            .where(EquipmentItem.id == item_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_inventory_number(self, inv_num: str) -> Optional[EquipmentItem]:
        stmt = (
            select(EquipmentItem)
            .options(joinedload(EquipmentItem.category))
            .where(EquipmentItem.inventory_number == inv_num)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(
        self,
        category_id: Optional[int] = None,
        status: Optional[EquipmentStatus] = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentItem]:
        stmt = select(EquipmentItem).options(joinedload(EquipmentItem.category))
        
        if not include_deleted:
            stmt = stmt.where(EquipmentItem.is_deleted.is_(False))
        if category_id is not None:
            stmt = stmt.where(EquipmentItem.category_id == category_id)
        if status is not None:
            stmt = stmt.where(EquipmentItem.status == status)

        stmt = stmt.offset(skip).limit(limit).order_by(EquipmentItem.inventory_number)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, item: EquipmentItem) -> EquipmentItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return self.get_by_id(item.id) or item

    def update(self, item: EquipmentItem) -> EquipmentItem:
        self.db.commit()
        self.db.refresh(item)
        return self.get_by_id(item.id) or item

    def soft_delete(self, item: EquipmentItem) -> EquipmentItem:
        item.is_deleted = True
        self.db.commit()
        self.db.refresh(item)
        return item
