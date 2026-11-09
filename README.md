# Půjčovna vybavení „Hory a voda“ (Varianta D)

Technická dokumentace a specifikace semestrálního projektu pro předmět **Pokročilé programování (PPRO)**, FIM UHK, zimní semestr 2026/2027.

---

## 1. Základní informace o projektu

- **Předmět:** Pokročilé programování (PPRO) – FIM UHK, ZS 2026/2027
- **Varianta zadání:** D – Půjčovna vybavení
- **Klient:** Martin Řehák, půjčovna *Hory a voda* (lyže, snowboardy, v létě lodě a vodácké vybavení)
- **Konzultace a role klienta:** `dominik.palla@uhk.cz`
- **Povinný milník:** Potvrzení volby zadání a návrhu datového modelu nejpozději na 4. cvičení.

---

## 2. Současný stav (AS-IS) a motivace klienta

Klient v současnosti provozuje evidenci manuálně:
- Záznamy v papírovém sešitě, inventární čísla psaná lihovkou na vybavení.
- Rezervace jsou přijímány telefonicky a zapisovány na papírové lístečky připíchnuté nad pultem.
- Sezóna je krátká a intenzivní, o víkendech se tvoří dlouhé fronty.
- **Kritický problém:** V sezóně dochází k overbookingu (jeden pár lyží je slíben dvěma lidem). V sobotním ranním shonu klient situaci hasí improvizací – zákazníkovi nabídne jiné vybavení a slevu, což snižuje zisk a profesionální reputaci půjčovny.

---

## 3. Společné povinné minimum semestrálního projektu

Projekt musí bezpodmínečně splňovat následující technická a architektonická kritéria:

1. **Architektura:** Tři vrstvy se striktně jednosměrnými závislostmi (Prezentační / API vrstva $\rightarrow$ Aplikační / Doménová logika $\rightarrow$ Datová / Perzistentní vrstva).
2. **Databáze & Migrace:** Relační databáze běžící v kontejneru (Docker) spravovaná verzovanými migracemi.
3. **Datový model:** Nejméně 5 doménových entit a alespoň jedna vazba $M:N$.
4. **Kontejnerizace:** Kompletní spuštění aplikace a její infrastruktury jediným příkazem:
   ```bash
   docker compose up
   ```
5. **Testy:** Sada automatizovaných testů ověřující doménová pravidla a klíčovou logiku aplikace.
6. **Data a bezpečnost:** Striktně syntetická data. Žádná reálná osobní data, žádné komerční stáže/projekty, žádná citlivá hesla či tajné klíče v repozitáři.
7. **Technická dokumentace:** Udržovaný přehled architektury, datového modelu, rozhodnutí a postupů.

---

## 4. Požadavky klienta (Co klient chce)

1. **Evidence konkrétních kusů vybavení:**
   - Každý kus má své unikátní inventární číslo, kategorii, velikost (např. délka lyží 170 cm), rok pořízení a stav opotřebení.
   - Evidence je striktně po fyzických kusech: dva identické páry lyží téhož výrobce a délky představují dva samostatné záznamy v databázi.
2. **Kategorie vybavení:**
   - Typické kategorie: lyže, snowboardy, boty, hole, lodě, vesty, helmy apod.
   - Sazby a výpočty cen vycházejí z přiřazené kategorie.
3. **Evidence zákazníků:**
   - Jméno, příjmení, telefonní číslo, číslo průkazu totožnosti (OP / pas), stav/výše kauce.
4. **Správa výpůjček:**
   - Jedna výpůjčka může obsahovat více kusů vybavení (např. komplet lyže + boty + hůlky + helma).
   - Má definovaný časový interval (`datum_od`, `datum_do`).
   - Tentýž fyzický kus je v čase půjčován opakovaně různým zákazníkům.
5. **Rezervace dopředu:**
   - Možnost zaevidovat rezervaci s předstihem (např. telefonát v úterý na víkendovou výpůjčku od soboty).
   - Časový slot vyzvednutí: v den začátku výpůjčky je rezervace garantována s ranním blokem do 10:00 (s 30minutovou ochrannou lhůtou do 10:30).
6. **Částečné vrácení vybavení:**
   - Podpora vrácení jednotlivých kusů z jedné výpůjčky v různých časech (např. lyže vráceny v poledne, boty až večer).
7. **Servis a údržba:**
   - Přepnutí kusu do stavu servisování. Po tuto dobu nesmí být kus nabízen ani k výpůjčce, ani k rezervaci.
   - Přehled vybavení v servisu včetně informace, jak dlouho v něm je.
8. **Ceník a tarifikace (Časové bloky výpůjček):**
   - Výpočet ceny podle kategorie vybavení a zvoleného časového bloku:
     - **Půldenní bloky (Half-day):**
       - *Dopolední slot:* 08:00 – 13:00 (vhodné pro ranní lyžování či krátký sjezd řeky).
       - *Odpolední slot:* 13:00 – 18:00.
     - **Celodenní blok (Full-day):** 1 kalendářní den (např. 08:00 – 18:00 nebo 24 hodin).
     - **Vícedenní bloky (Multi-day):** $N$ kalendářních dní (např. týdenní rodinná dovolená).
     - **Víkendový blok (Weekend package):** Zvýhodněný balíček od pátku 14:00 do neděle 18:00 (případně vrácení v pondělí do 09:00), tarifikovaný přesně jako 2 celé dny.
9. **Přehledy a reporting:**
   - Aktuální stav: co je právě půjčené venku.
   - Prodlení: co mělo být vráceno a dosud není.
   - Využitost: statistika četnosti výpůjček jednotlivých kusů pro rozhodování o vyřazení a dokoupení nového inventáře.

---

## 5. Obchodní pravidla (Na čem klient trvá)

Tato pravidla musí být **vynucena aplikací a datovou integritou**, nikoliv spoléháním na lidskou obsluhu:
- **Žádné kolize termínů:** Jeden fyzický kus nesmí být v žádném případě přiřazen ke dvěma výpůjčkám nebo rezervacím, jejichž časové intervaly se překrývají.
- **Nedostupnost kusu v servisu:** Kus nacházející se v servisu nelze zapůjčit ani rezervovat.
- **Penále za pozdní vrácení:** Za každý započatý den zpoždění oproti sjednanému termínu vrácení se automaticky kalkuluje penále.
- **Neměnnost historie:** Historie výpůjček u jednotlivých kusů se nikdy fyzicky nemaže. Slouží k posuzování reklamací, amortizaci a obměně vybavení.

---

## 6. Přání a náměty (Co klient prohodil mimochodem)

Doplňkové body ke zvážení v ergonomii a UI:
- *Ranní přehledovka:* Zobrazení na jedné přehledné obrazovce pro sobotní ranní špičku („co máme zrovna volné k okamžitému půjčení“).
- *Kauce:* Klient vybírá kauci v hotovosti a preferuje jednoduchou evidenci bez složitého účetního zatížení.
- *Ruční operativní sleva:* Možnost obsluhy udělit individuální slevu na výpůjčku.
- *Tisk smlouvy:* Možnost vygenerovat/vytisknout jednoduchou smlouvu o výpůjčce nebo předávací protokol.

---

## 7. Otevřené body (Kde se návrh láme)

Body, které klient nemá dořešené a které vyžadují jednoznačné architektonické a procesní rozhodnutí vývojového týmu:

| # | Otevřený bod | Podstata problému | Stav řešení |
|---|---|---|---|
| **1** | **Konkrétní kus vs. typová kapacita** | Zákazník v telefonu poptává „lyže 170 cm“, nikoliv inventární číslo #412. Rozhodnutí: Bude rezervace držet virtuální kapacitu v rámci (kategorie + parametry) a konkrétní kus se přiřadí až při fyzickém výdeji, nebo se konkrétní kus fixuje hned při rezervaci? | K diskusi (ADR-001) |
| **2** | **Expirace nevyzvednuté rezervace** | Rezervace má platnost např. do soboty 10:00. Co se stane v 10:05? Uvolní systém kus automaticky pro frontu v prodejně, nebo se vyžaduje manuální zásah/storno obsluhou? | **Vyřešeno (ADR-002)**: Do 10:00 + 30 min tolerance; v 10:30 auto-uvolnění |
| **3** | **Záznam poškození vybavení** | Jak přesně evidovat vzniklou škodu při vrácení? Má být škoda navázána na inventární kus (změna opotřebení/servis), na výpůjčku/zákazníka (dlužná částka, stržení z kauce)? | K diskusi (ADR-003) |
| **4** | **Částečné vrácení a penalizace** | Má výpůjčka celkový stav otevřeno/uzavřeno, nebo má každá zapůjčená položka vlastní životní cyklus? Jak se počítá penále při částečném zpoždění jedné položky? | K diskusi (ADR-004) |
| **5** | **Změna ceníku během sezóny** | Jak technicky zajistit, aby úprava ceníku neovlivnila již uzavřené minulé výpůjčky a existující rezervace (historické snapshoty cen vs. platnost ceníku s časovým intervalem)? | K diskusi (ADR-005) |

---

## 8. Sekce: Rozhodnutí (Architecture & Business Decisions Log)

Tato sekce průběžně eviduje veškerá odsouhlasená rozhodnutí k otevřeným bodům i technické architektuře projektu. Každý záznam obsahuje datum, kontext, zvolené řešení a jeho zdůvodnění.

### Záznamy rozhodnutí

- **ADR-001: Strategie rezervací (Návrh k projednání)**
  - *Stav:* K diskusi
  - *Kontext:* Zákazník poptává typ a velikost, obsluha potřebuje jednoduchost a nesmí dojít k přerezervování.
  - *Doporučený návrh:* Dvoufázový model – rezervace alokuje konkrétní fyzický kus (či garantuje slot konkrétního kusu), aby bylo technicky triviální garantovat zákaz časového překryvu, s možností obsluhy při výdeji kus operativně zaměnit za ekvivalent stejné kategorie/velikosti.

- **ADR-002: Expirace a držení rezervace v den výdeje**
  - *Stav:* **Schváleno** (2026-10-05)
  - *Kontext:* V sobotu ráno stojí před prodejnou fronta a blokované nevyzvednuté rezervace připravují půjčovnu o tržby i spokojené zákazníky.
  - *Rozhodnutí:* Rezervace je v den začátku výpůjčky garantována s ranním oknem do 10:00 s 30minutovou ochrannou tolerancí (do 10:30). Pokud se zákazník do 10:30 nedostaví ani nepožádá o posun, rezervace je automaticky přepnuta do stavu `EXPIRED` a rezervované vybavení je uvolněno pro zákazníky ve frontě.

- **ADR-003: Evidence poškození a vazba na kauci (Návrh k projednání)**
  - *Stav:* K diskusi
  - *Kontext:* Kus může být poškozen, opotřeben nebo ztracen.
  - *Doporučený návrh:* Záznam o vrácení obsahuje hodnocení stavu každé položky. Při poškození vzniká servisní incident navázaný na daný kus i danou výpůjčku s vyčíslenou částkou škody (započteno proti kauci).

- **ADR-004: Životní cyklus položek výpůjčky a penále (Návrh k projednání)**
  - *Stav:* K diskusi
  - *Kontext:* Částečné vrácení (např. lyže vráceny včas, boty o den později).
  - *Doporučený návrh:* Výpůjčka se skládá z položek (`RentalItem`). Každá položka má vlastní čas vrácení a stav. Penále za pozdní vrácení se počítá na úrovni konkrétního nevráceného kusu za každý započatý den prodlení.

- **ADR-005: Verzování cen a integrita účtování (Návrh k projednání)**
  - *Stav:* K diskusi
  - *Kontext:* Změna ceníku nesmí přepsat cenu běžící nebo minulé výpůjčky.
  - *Doporučený návrh:* Při vytvoření výpůjčky/rezervace se ukládá neměnný snapshot sjednané jednotkové ceny do záznamu položky (`unit_price_at_rental`). Změna globálního ceníku ovlivní pouze nově vytvářené rezervace.

- **ADR-006: Granularita časových bloků výpůjček a ceníku**
  - *Stav:* **Schváleno** (2026-10-05)
  - *Kontext:* Klient potřebuje pokrýt krátkodobé i vícedenní výpůjčky a zohlednit specifický víkendový režim.
  - *Rozhodnutí:* Systém podporuje 4 typy výpůjčních bloků:
    1. *Půldenní blok:* Dopoledne (08:00 – 13:00) a Odpoledne (13:00 – 18:00).
    2. *Celodenní blok:* Standardní 1 kalendářní den.
    3. *Vícedenní blok:* $N$ celých kalendářních dní.
    4. *Víkendový balíček:* Od pátku 14:00 do neděle 18:00 (vrácení pondělí do 09:00), zpoplatněný cenou 2 dnů.

- **ADR-007: Volba technologického stacku (Python & FastAPI)**
  - *Stav:* **Schváleno** (2026-10-05)
  - *Kontext:* Výběr jazyka, backendového frameworku, ORM a databáze pro realizaci třívrstvé architektury, jednoduché demo verze i finální aplikace.
  - *Rozhodnutí:*
    - **Jazyk & Runtime:** Python 3.12+ (v prostředí je k dispozici Python 3.14).
    - **Backend Framework:** FastAPI (vysoký výkon, asynchronní podpora, automatická OpenAPI/Swagger dokumentace, validace dat přes Pydantic v2).
    - **ORM & Databázový přístup:** SQLAlchemy 2.0 (moderní typed declarative mapping) s asynchronním i synchronním ovladačem.
    - **Databáze:** PostgreSQL v Dockeru (pro lokální rychlý vývoj demo verze lze paralelně podporovat SQLite/PostgreSQL).
    - **Migrace schématu:** Alembic (verzované migrace splňující povinné minimum).
    - **Autentizace:** Bezpečný hash hesel (bcrypt / argon2), OAuth2 password flow s JWT tokeny (případně session cookie pro webové rozhraní).
    - **Kontejnerizace:** Docker & Docker Compose (`docker compose up`).
    - **Testování:** Pytest + HTTPX TestClient pro testy byznys pravidel a endpointů.

- **ADR-008: Firemní identita a designový systém webového rozhraní**
  - *Stav:* **Schváleno** (2026-10-19)
  - *Kontext:* Požadavek na ucelenou corporate identity, odstranění vodorovného přetékání tabulky inventáře při 100% zoomu, doplnění fotek/loga půjčovny do horní třetiny a použití plného názvu půjčovny.
  - *Rozhodnutí:*
    - **Oficiální název:** „Půjčovna sportovního vybavení Hory & Voda“, zkráceně „Půjčovna Hory & Voda“.
    - **Layout & responzivita:** Zvětšení šířky hlavního pruhu na `1560px` a kompaktní strukturování tabulky vybavení, aby se na standardních monitorech při 100% zoomu nezobrazoval horizontální posuvník.
    - **Hero sekce:** Začlenění reprezentativní hero sekce s fotkou interiéru půjčovny a horského zázemí a oficiálním emblémem značky v horní třetině hlavní stránky.
    - **Vizuální styl:** Striktní Light mode, žádné AI „pill“ ovály, prémiový minimalistický styl (inspirace Squarespace/Adobe), barvy Alpine Amber (`#d97706`), Glacier Blue (`#0284c7`), Slate Ink (`#1c1917`). Kompletní dokumentace v `docs/corporate_identity.md`.

- **ADR-009: Ochrana osobních údajů zákazníků (GDPR) a oddělení zákaznického / personálního pohledu**
  - *Stav:* **Schváleno** (2026-11-02)
  - *Kontext:* Nepřihlášení uživatelé jsou zákazníci webu. Zákazník nesmí vidět osobní údaje (jména, telefonní čísla, poznámky ani rezervační kódy) jiných zákazníků ani seznam čekajících rezervací. Zákazníkovi stačí vědět, že daný kus je ve stavu „Rezervováno“.
  - *Rozhodnutí:*
    - **Backendové maskování (Data Masking):** Veřejné endpointy `GET /api/v1/equipment/` a `GET /api/v1/equipment/{id}` kontrolují přítomnost a roli uživatele. Pro anonymní návštěvníky se hodnoty `reservation_code`, `reservation_customer` a `reservation_note` vrací striktně jako `null`.
    - **Veřejná rezervace bez nutnosti přihlášení:** Zákazníci mohou vytvořit rezervaci přes koncový bod `POST /api/v1/equipment/{item_id}/reserve`.
    - **Oddělení UI zobrazení:** Karta aktivních rezervací (`#card-active-reservations`) na rezervační záložce i detaily zákazníka u kusu v tabulce inventáře jsou pro nepřihlášené uživatele zcela skryté. Zpřístupní se výhradně personálu s rolí `STAFF` nebo `ADMIN`.

- **ADR-010: Responzivní mobilní zobrazení pro telefony a rozbalovací navigace**
  - *Stav:* **Schváleno** (2026-11-09)
  - *Kontext:* Požadavek na bezchybné zobrazení na smartphonech, aniž by došlo k jakémukoli narušení desktopového layoutu pro PC (široký kontejner 1560 px pro tabulku). Původní vodorovný posuvník (slider) byl na mobilu méně zřetelný jako výběr stránek.
  - *Rozhodnutí:*
    - Implementována dvouúrovňová mobilní navigace (`@media (max-width: 768px)` a `≤ 480px`): v horním řádku je logo a tlačítko přihlášení, pod ním plnohodnotné rozbalovací menu (drop-down menu) pro přepínání hlavních stránek (*Ranní přehled*, *Rezervace*, *Ceníky a kategorie*).
    - Drop-down menu jasně zobrazuje aktuálně zvolenou sekci i rozbalitelný seznam možností s popisy a ikonami, čímž eliminuje nutnost posouvání záložek do stran.
    - Adaptivní přizpůsobení vyhledávacího pole, přepínačů filtrů a modálních dialogů pro dotyková zařízení.

---

## 9. Projektová dokumentace

Veškerá technická a semestrální dokumentace je připravena v adresáři [`docs/`](docs):

- 📄 **Oficiální PDF dokumentace:** [docs/PPRO-dokumentace-Hory-a-voda.pdf](docs/PPRO-dokumentace-Hory-a-voda.pdf)
- 📝 **Vyplněná semestrální šablona (DOCX):** [docs/PPRO-dokumentace-Hory-a-voda.docx](docs/PPRO-dokumentace-Hory-a-voda.docx)
- 📖 **Systémová technická dokumentace (Markdown):** [docs/system_documentation.md](docs/system_documentation.md)
- 🎨 **Firemní identita a designový manuál:** [docs/corporate_identity.md](docs/corporate_identity.md)

---

## 10. Technický zásobník a spuštění

- **Backend:** Python 3.14, FastAPI, Pydantic v2, Uvicorn
- **ORM & Migrace:** SQLAlchemy 2.0, Alembic
- **Databáze:** PostgreSQL 16 (případně SQLite pro rychlé offline testování bez Docker daemona)
- **Kontejnerizace:** Dockerfile, Docker Compose (`docker compose up`)
- **Testy & QA:** Pytest, HTTPX, Ruff / Black

### 9.1 Rychlé lokální spuštění demo verze

1. **Aktivace virtuálního prostředí a instalace závislostí:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Aplikace databázových migrací a naplnění syntetickými daty:**
   ```bash
   alembic upgrade head
   python -m app.seed
   ```

3. **Spuštění vývojového serveru:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - Interaktivní Swagger dokumentace: **`http://localhost:8000/docs`**
   - OpenAPI specifikace: `http://localhost:8000/openapi.json`

4. **Spuštění automatizovaných testů:**
   ```bash
   pytest -v
   ```

### 9.2 Spuštění přes Docker Compose

```bash
docker compose up --build
```
Aplikace automaticky spustí PostgreSQL kontejner, vyčká na jeho healthcheck, aplikuje Alembic migrace, vloží počáteční data a spustí FastAPI na portu `8000`.

### 9.3 Testovací demo účty (syntetická data)

| Uživatelské jméno | Heslo | Role | Popis |
|---|---|---|---|
| `obsluha` | `Heslo123!` | `STAFF` | Běžný personál půjčovny pro ranní odbavování |
| `admin` | `Admin123!` | `ADMIN` | Administrátor se správou personálu a ceníků |


