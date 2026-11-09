from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_user_optional
from app.db.models.user import User
from app.db.models.equipment import EquipmentStatus
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentResponse, EquipmentReserveRequest
from app.services.equipment_service import EquipmentService

router = APIRouter(prefix="/equipment", tags=["Kusy vybavení"])


@router.get("/", response_model=List[EquipmentResponse], summary="Seznam vybavení s filtry")
def list_equipment(
    category_id: Optional[int] = Query(None, description="Filtrovat podle kategorie"),
    equipment_status: Optional[EquipmentStatus] = Query(None, alias="status", description="Filtrovat podle stavu (AVAILABLE, RENTED, IN_SERVICE, RESERVED)"),
    include_deleted: bool = Query(False, description="Zahrnout i vyřazené/smazané kusy"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Vrátí seznam evidovaných fyzických kusů vybavení.
    Umožňuje ranní rychlý přehled volného vybavení (status=AVAILABLE) a filtrování dle kategorií.
    Pokud uživatel není přihlášený personál, osobní údaje rezervací jsou z důvodu ochrany soukromí skryty.
    """
    service = EquipmentService(db)
    items = service.get_items(
        category_id=category_id,
        status_filter=equipment_status,
        include_deleted=include_deleted,
        skip=skip,
        limit=limit
    )

    if not current_user:
        # GDPR ochrana: Anonymním návštěvníkům nepředáváme data o rezervujících zákaznících
        masked = []
        for item in items:
            r = EquipmentResponse.model_validate(item)
            r.reservation_code = None
            r.reservation_customer = None
            r.reservation_note = None
            masked.append(r)
        return masked

    return items


@router.get("/{item_id}", response_model=EquipmentResponse, summary="Detail konkrétního kusu vybavení")
def get_equipment_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Vrátí detail konkrétního kusu včetně informací o kategorii."""
    service = EquipmentService(db)
    item = service.get_item_by_id(item_id)
    resp = EquipmentResponse.model_validate(item)
    if not current_user:
        resp.reservation_code = None
        resp.reservation_customer = None
        resp.reservation_note = None
    return resp


@router.post("/{item_id}/reserve", response_model=EquipmentResponse, summary="Vytvoření rezervace (veřejné pro zákazníky)")
def reserve_equipment_item(
    item_id: int,
    reserve_in: EquipmentReserveRequest,
    db: Session = Depends(get_db)
):
    """
    Umožňuje zákazníkovi zarezervovat volný kus.
    Kusu je přiřazen unikátní kód rezervace a status RESERVED.
    """
    service = EquipmentService(db)
    return service.reserve_item(
        item_id=item_id,
        customer_name=reserve_in.customer_name,
        customer_phone=reserve_in.customer_phone,
        start_date=reserve_in.start_date,
        rental_block=reserve_in.rental_block,
        note=reserve_in.note
    )


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED, summary="Zaevidování nového kusu vybavení (chráněno)")
def create_equipment_item(
    item_in: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Zaeviduje nový fyzický kus vybavení s unikátním inventárním číslem (vyžaduje přihlášení)."""
    service = EquipmentService(db)
    return service.create_item(item_in)


@router.put("/{item_id}", response_model=EquipmentResponse, summary="Úprava údajů a stavu kusu (chráněno)")
def update_equipment_item(
    item_id: int,
    item_in: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upraví stav opotřebení, provozní status (např. odeslání do servisu) nebo parametry kusu."""
    service = EquipmentService(db)
    return service.update_item(item_id, item_in)


@router.delete("/{item_id}", response_model=EquipmentResponse, summary="Vyřazení / soft-delete kusu vybavení (chráněno)")
def delete_equipment_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Provede bezpečné vyřazení kusu z aktivního fondu (soft-delete).
    Historie kusu v databázi zůstává zachována dle požadavku klienta na neměnnost historie.
    """
    service = EquipmentService(db)
    return service.soft_delete_item(item_id)
