import logging
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.models.user import User, UserRole
from app.db.models.category import Category
from app.db.models.equipment import EquipmentItem, EquipmentStatus
from app.core.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    logger.info("Inicializace tabulek v databázi...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # 1. Kontrola a vložení uživatelů
        if not db.query(User).filter_by(username="obsluha").first():
            logger.info("Vytváření uživatele 'obsluha'...")
            staff_user = User(
                username="obsluha",
                email="obsluha@horyavoda.cz",
                hashed_password=hash_password("Heslo123!"),
                role=UserRole.STAFF,
                is_active=True,
            )
            admin_user = User(
                username="admin",
                email="admin@horyavoda.cz",
                hashed_password=hash_password("Admin123!"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add_all([staff_user, admin_user])
            db.commit()

        # 2. Kontrola a vložení kategorií
        if db.query(Category).count() == 0:
            logger.info("Vytváření kategorií vybavení s ceníky...")
            cat_ski = Category(
                name="Sjezdové lyže",
                description="Carvingové sjezdové lyže různých délek a tuhostí.",
                halfday_price=250.0,
                daily_price=400.0,
                weekend_price=700.0,
            )
            cat_snb = Category(
                name="Snowboardy",
                description="Freestyle a all-mountain snowboardy.",
                halfday_price=230.0,
                daily_price=380.0,
                weekend_price=650.0,
            )
            cat_boots = Category(
                name="Lyžařské a snowboardové boty",
                description="Skeletové boty a boty na snowboard.",
                halfday_price=120.0,
                daily_price=180.0,
                weekend_price=300.0,
            )
            cat_boat = Category(
                name="Lodě a kanoe",
                description="Nafukovací dvoumístné kanoe a rafty na vodu.",
                halfday_price=300.0,
                daily_price=500.0,
                weekend_price=900.0,
            )
            db.add_all([cat_ski, cat_snb, cat_boots, cat_boat])
            db.commit()

            # 3. Vložení konkrétních fyzických kusů
            logger.info("Vytváření konkrétních inventárních kusů vybavení...")
            items = [
                # Dva stejné páry lyží jsou dva unikátní záznamy dle zadání!
                EquipmentItem(
                    inventory_number="SKI-001",
                    category_id=cat_ski.id,
                    size="170 cm",
                    purchase_year=2024,
                    condition_state="Výborný",
                    status=EquipmentStatus.AVAILABLE
                ),
                EquipmentItem(
                    inventory_number="SKI-002",
                    category_id=cat_ski.id,
                    size="170 cm",
                    purchase_year=2024,
                    condition_state="Výborný",
                    status=EquipmentStatus.AVAILABLE
                ),
                EquipmentItem(
                    inventory_number="SKI-003",
                    category_id=cat_ski.id,
                    size="165 cm",
                    purchase_year=2023,
                    condition_state="Běžné opotřebení",
                    status=EquipmentStatus.AVAILABLE
                ),
                EquipmentItem(
                    inventory_number="SKI-004",
                    category_id=cat_ski.id,
                    size="175 cm",
                    purchase_year=2022,
                    condition_state="Poškrábaná skluznice po servisu",
                    status=EquipmentStatus.IN_SERVICE  # Kus v servisu
                ),
                EquipmentItem(
                    inventory_number="SNB-001",
                    category_id=cat_snb.id,
                    size="156 cm",
                    purchase_year=2024,
                    condition_state="Jako nové",
                    status=EquipmentStatus.AVAILABLE
                ),
                EquipmentItem(
                    inventory_number="BOOT-001",
                    category_id=cat_boots.id,
                    size="42 EU",
                    purchase_year=2023,
                    condition_state="Dobrý stav",
                    status=EquipmentStatus.AVAILABLE
                ),
                EquipmentItem(
                    inventory_number="BOOT-002",
                    category_id=cat_boots.id,
                    size="44 EU",
                    purchase_year=2023,
                    condition_state="Dobrý stav",
                    status=EquipmentStatus.AVAILABLE
                ),
                EquipmentItem(
                    inventory_number="BOAT-001",
                    category_id=cat_boat.id,
                    size="Dvoumístná Pálava",
                    purchase_year=2023,
                    condition_state="Výborný stav bez záplat",
                    status=EquipmentStatus.AVAILABLE
                ),
            ]
            db.add_all(items)
            db.commit()

        logger.info("Seedování databáze bylo úspěšně dokončeno!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
