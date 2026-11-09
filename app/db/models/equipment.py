from datetime import datetime, timezone
import enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.category import Category


class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"        # Volné k půjčení
    RENTED = "RENTED"              # Půjčeno zákazníkovi
    RESERVED = "RESERVED"          # Rezervováno
    IN_SERVICE = "IN_SERVICE"      # V servisu / údržbě (dle zadání nelze půjčit ani rezervovat)
    RETIRED = "RETIRED"            # Vyřazeno z provozu


class EquipmentItem(Base):
    __tablename__ = "equipment_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    inventory_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    size: Mapped[str] = mapped_column(String(30), nullable=False)  # např. '170 cm', '43 EU'
    purchase_year: Mapped[int] = mapped_column(Integer, nullable=False)
    condition_state: Mapped[str] = mapped_column(String(100), default="Výborný", nullable=False)
    
    status: Mapped[EquipmentStatus] = mapped_column(
        Enum(EquipmentStatus),
        default=EquipmentStatus.AVAILABLE,
        nullable=False,
        index=True
    )
    
    # Rezervační údaje pro kontrolu při vyzvednutí
    reservation_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default=None, index=True)
    reservation_customer: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, default=None)
    reservation_note: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, default=None)

    # Soft delete dle požadavku klienta: historie se nemaže
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    category: Mapped["Category"] = relationship("Category", back_populates="equipment_items")
