def test_create_and_get_category(client, auth_headers):
    # 1. Vytvoření kategorie
    cat_payload = {
        "name": "Běžky",
        "description": "Běžecké lyže klasika i skate",
        "halfday_price": 150.0,
        "daily_price": 250.0,
        "weekend_price": 450.0,
    }
    create_resp = client.post("/api/v1/categories/", json=cat_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created_cat = create_resp.json()
    assert created_cat["name"] == "Běžky"
    assert created_cat["weekend_price"] == 450.0

    # 2. Načtení detailu kategorie
    cat_id = created_cat["id"]
    get_resp = client.get(f"/api/v1/categories/{cat_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Běžky"


def test_create_equipment_and_prevent_duplicate_inventory_number(client, auth_headers):
    # Nejprve vytvoříme kategorii
    cat_resp = client.post(
        "/api/v1/categories/",
        json={
            "name": "Snowboardy test",
            "halfday_price": 200.0,
            "daily_price": 300.0,
            "weekend_price": 500.0,
        },
        headers=auth_headers
    )
    assert cat_resp.status_code == 201
    cat_id = cat_resp.json()["id"]

    # 1. Vložení prvního kusu
    item_payload = {
        "inventory_number": "SNB-999",
        "category_id": cat_id,
        "size": "158 cm",
        "purchase_year": 2024,
        "condition_state": "Nové",
        "status": "AVAILABLE"
    }
    item_resp = client.post("/api/v1/equipment/", json=item_payload, headers=auth_headers)
    assert item_resp.status_code == 201
    item_id = item_resp.json()["id"]

    # 2. Pokus o vložení druhého kusu se STEJNÝM inventárním číslem -> musí selhat (400 Bad Request)
    duplicate_resp = client.post("/api/v1/equipment/", json=item_payload, headers=auth_headers)
    assert duplicate_resp.status_code == 400
    assert "již existuje" in duplicate_resp.json()["detail"]

    # 3. Soft-delete kusu
    del_resp = client.delete(f"/api/v1/equipment/{item_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["is_deleted"] is True
    assert del_resp.json()["status"] == "RETIRED"

    # 4. Kus již není ve výchozím seznamu
    list_resp = client.get("/api/v1/equipment/")
    assert not any(i["id"] == item_id for i in list_resp.json())


def test_unauthenticated_cannot_create_equipment(client):
    # Nepřihlášený uživatel nesmí mít právo vytvářet inventář
    resp = client.post(
        "/api/v1/equipment/",
        json={
            "inventory_number": "HACK-001",
            "category_id": 1,
            "size": "170 cm",
            "purchase_year": 2024,
            "condition_state": "Neznámý",
            "status": "AVAILABLE"
        }
    )
    assert resp.status_code == 401


def test_update_equipment_condition_state(client, auth_headers):
    # 1. Vytvoření kusu s výchozím stavem
    cat_resp = client.post(
        "/api/v1/categories/",
        json={
            "name": "Lyže sjezdové test",
            "halfday_price": 250.0,
            "daily_price": 400.0,
            "weekend_price": 700.0,
        },
        headers=auth_headers
    )
    cat_id = cat_resp.json()["id"]

    item_resp = client.post(
        "/api/v1/equipment/",
        json={
            "inventory_number": "SKI-COND-01",
            "category_id": cat_id,
            "size": "165 cm",
            "purchase_year": 2024,
            "condition_state": "Výborný",
            "status": "AVAILABLE"
        },
        headers=auth_headers
    )
    assert item_resp.status_code == 201
    item_id = item_resp.json()["id"]
    assert item_resp.json()["condition_state"] == "Výborný"

    # 2. Změna stavu opotřebení přihlášenou obsluhou / adminem
    update_resp = client.put(
        f"/api/v1/equipment/{item_id}",
        json={
            "condition_state": "Poškrábaná skluznice – vyžaduje servis",
            "status": "IN_SERVICE"
        },
        headers=auth_headers
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["condition_state"] == "Poškrábaná skluznice – vyžaduje servis"
    assert updated_data["status"] == "IN_SERVICE"


def test_public_reservation_and_gdpr_masking(client, auth_headers):
    # 1. Vytvoření kategorie a kusu
    cat_resp = client.post(
        "/api/v1/categories/",
        json={"name": "Pádla test", "halfday_price": 50.0, "daily_price": 90.0, "weekend_price": 160.0},
        headers=auth_headers
    )
    cat_id = cat_resp.json()["id"]

    item_resp = client.post(
        "/api/v1/equipment/",
        json={
            "inventory_number": "PAD-GDPR-01",
            "category_id": cat_id,
            "size": "210 cm",
            "purchase_year": 2024,
            "condition_state": "Nové",
            "status": "AVAILABLE"
        },
        headers=auth_headers
    )
    item_id = item_resp.json()["id"]

    # 2. Nepřihlášený zákazník si zarezervuje kus
    reserve_resp = client.post(
        f"/api/v1/equipment/{item_id}/reserve",
        json={
            "customer_name": "Jan Novák",
            "customer_phone": "+420 777 888 999",
            "rental_block": "FULLDAY",
            "start_date": "2026-12-01",
            "note": "Vyzvedne v 9:00"
        }
    )
    assert reserve_resp.status_code == 200
    res_data = reserve_resp.json()
    assert res_data["status"] == "RESERVED"
    assert res_data["reservation_code"].startswith("REZ-")
    assert "Jan Novák" in res_data["reservation_customer"]

    # 3. Nepřihlášený uživatel (GET bez tokenu) vidí status RESERVED, ale osobní údaje jsou ZAMASKIVÁNY (None)
    public_get = client.get(f"/api/v1/equipment/{item_id}")
    assert public_get.status_code == 200
    pub_data = public_get.json()
    assert pub_data["status"] == "RESERVED"
    assert pub_data["reservation_code"] is None
    assert pub_data["reservation_customer"] is None
    assert pub_data["reservation_note"] is None

    # Stejně tak v hromadném seznamu
    public_list = client.get("/api/v1/equipment/")
    pub_item = next(i for i in public_list.json() if i["id"] == item_id)
    assert pub_item["status"] == "RESERVED"
    assert pub_item["reservation_code"] is None
    assert pub_item["reservation_customer"] is None

    # 4. Přihlášený personál (GET s auth_headers) vidí kompletní rezervační data
    auth_get = client.get(f"/api/v1/equipment/{item_id}", headers=auth_headers)
    assert auth_get.status_code == 200
    auth_data = auth_get.json()
    assert auth_data["reservation_code"] == res_data["reservation_code"]
    assert "Jan Novák" in auth_data["reservation_customer"]
    assert "+420 777 888 999" in auth_data["reservation_customer"]

    # 5. Nelze znovu rezervovat již rezervovaný kus
    conflict_resp = client.post(
        f"/api/v1/equipment/{item_id}/reserve",
        json={
            "customer_name": "Petr Druhý",
            "customer_phone": "+420 606 111 222",
            "rental_block": "FULLDAY",
            "start_date": "2026-12-01"
        }
    )
    assert conflict_resp.status_code == 400


