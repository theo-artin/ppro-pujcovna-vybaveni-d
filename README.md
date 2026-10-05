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
6. **Částečné vrácení vybavení:**
   - Podpora vrácení jednotlivých kusů z jedné výpůjčky v různých časech (např. lyže vráceny v poledne, boty až večer).
7. **Servis a údržba:**
   - Přepnutí kusu do stavu servisování. Po tuto dobu nesmí být kus nabízen ani k výpůjčce, ani k rezervaci.
   - Přehled vybavení v servisu včetně informace, jak dlouho v něm je.
8. **Ceník a tarifikace:**
   - Výpočet ceny podle kategorie a počtu dní.
   - Zvláštní pravidlo pro víkend: počítá se jako 2 dny, ale zákazník si vybavení vyzvedává již v pátek odpoledne.
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

| # | Otevřený bod | Podstata problému |
|---|---|---|
| **1** | **Konkrétní kus vs. typová kapacita** | Zákazník v telefonu poptává „lyže 170 cm“, nikoliv inventární číslo #412. Rozhodnutí: Bude rezervace držet virtuální kapacitu v rámci (kategorie + parametry) a konkrétní kus se přiřadí až při fyzickém výdeji, nebo se konkrétní kus fixuje hned při rezervaci? |
| **2** | **Expirace nevyzvednuté rezervace** | Rezervace má platnost např. do soboty 10:00. Co se stane v 10:05? Uvolní systém kus automaticky pro frontu v prodejně, nebo se vyžaduje manuální zásah/storno obsluhou? |
| **3** | **Záznam poškození vybavení** | Jak přesně evidovat vzniklou škodu při vrácení? Má být škoda navázána na inventární kus (změna opotřebení/servis), na výpůjčku/zákazníka (dlužná částka, stržení z kauce)? |
| **4** | **Částečné vrácení a penalizace** | Má výpůjčka celkový stav otevřeno/uzavřeno, nebo má každá zapůjčená položka vlastní životní cyklus? Jak se počítá penále při částečném zpoždění jedné položky? |
| **5** | **Změna ceníku během sezóny** | Jak technicky zajistit, aby úprava ceníku neovlivnila již uzavřené minulé výpůjčky a existující rezervace (historické snapshoty cen vs. platnost ceníku s časovým intervalem)? |

---

## 8. Sekce: Rozhodnutí (Architecture & Business Decisions Log)

Tato sekce průběžně eviduje veškerá odsouhlasená rozhodnutí k otevřeným bodům i technické architektuře projektu. Každý záznam obsahuje datum, kontext, zvolené řešení a jeho zdůvodnění.

### Záznamy rozhodnutí

*Zatím žádná rozhodnutí nebyla formalizována. Níže jsou uvedeny výchozí návrhy k projednání:*

- **ADR-001: Strategie rezervací (Návrh k projednání)**
  - *Stav:* K diskusi
  - *Kontext:* Zákazník poptává typ a velikost, obsluha potřebuje jednoduchost a nesmí dojít k přerezervování.
  - *Doporučený návrh:* Dvoufázový model – rezervace alokuje konkrétní fyzický kus (či garantuje slot konkrétního kusu), aby bylo technicky triviální garantovat zákaz časového překryvu, s možností obsluhy při výdeji kus operativně zaměnit za ekvivalent stejné kategorie/velikosti.

- **ADR-002: Expirace rezervací (Návrh k projednání)**
  - *Stav:* K diskusi
  - *Kontext:* V sobotu stojí fronta a blokované nevyzvednuté rezervace připravují půjčovnu o tržby.
  - *Doporučený návrh:* Rezervace má čas expirace (např. sjednaný čas + tolerance 30 min). Po uplynutí systém označí rezervaci jako `EXPIROVÁNO` a nabídne obsluze rychlé uvolnění do volného fondu jedním kliknutím (nebo automatickým cron jobem).

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

---

## 9. Technický zásobník a spuštění

- **Backend / Databáze / Frontend:** Bude upřesněno po dohodě s uživatelem.
- **Kontejnerizace:** Docker & Docker Compose (`docker compose up`).
- **Migrace:** Verzované schéma relační databáze.
