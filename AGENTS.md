# AGENTS.md – Pravidla a metodika práce agenta

Tento dokument slouží jako lokální instrukční sada a pravidla chování pro AI asistenta (Antigravity / agenty) při práci na tomto projektu.

---

## 1. Stručný přehled projektu

Projekt realizuje aplikaci pro **Půjčovnu vybavení „Hory a voda“** (Zadání varianty D) v rámci předmětu **Pokročilé programování (PPRO)** na FIM UHK (ZS 2026/2027).

> [!NOTE]
> Veškeré detailní zadání, doménová pravidla klienta, otevřené body, stav projektu a průběžný protokol rozhodnutí se nacházejí v [README.md](README.md).
> **Informace z README.md se zde neduplikují.**

---

## 2. Metodika a procesní pravidla práce

Při veškerých úpravách a postupu na projektu se agent řídí následujícími závaznými pravidly:

### 2.1 Git operace a schvalování commitů
- **Žádné svévolné commity:** Agent nesmí provést `git commit` automaticky bez předchozího dotazu a schválení uživatelem.
- **Formát žádosti o commit:** Před commitem agent uživateli přehledně sdělí:
  1. Které soubory budou do commitu zahrnuty (`git add`).
  2. Návrh zprávy commitu (v souladu s [Conventional Commits](https://www.conventionalcommits.org/), např. `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`).
- **Čekání na potvrzení:** Agent provede commit až po výslovném potvrzení uživatelem.
- **Git Push:** Operace `git push` na vzdálený repozitář (GitHub) se provádí pouze na přímou žádost uživatele.

### 2.2 Průběžné informování a transparentnost
- Agent uživatele v každém kroku stručně a jasně informuje o tom:
  - co právě dokončil,
  - v jakém stavu se kód a workspace nachází,
  - jaký je doporučený bezprostředně následující krok.
- Pokud vznikne více možností řešení, agent nabídne varianty s doporučením a vyžádá si preferenci uživatele.

### 2.3 Protokolování rozhodnutí (Decisions Log)
- Při jakékoli dohodě s uživatelem týkající se:
  - vyřešení některého z otevřených bodů klienta (viz sekce 7 v `README.md`),
  - volby technologického stacku (jazyk, framework, DB, migrační nástroj, frontend),
  - návrhu datového modelu a klíčových vazeb,
  je agent povinen provést zápis do sekce **8. Rozhodnutí** v [README.md](README.md).

### 2.4 Technické mantinely projektu
- **Třívrstvá architektura:** Důsledně oddělené vrstvy s jednosměrným tokem závislostí.
- **Docker & Docker Compose:** Aplikace i relační databáze musí být plně a bezchybně spustitelné příkazem `docker compose up`.
- **Migrace:** Veškeré změny databázového schématu musí být řízeny verzovanými migracemi.
- **Kvalita a bezpečnost:** Automatizované testy doménových pravidel, striktně syntetická testovací data, zákaz commitování credentials a tajných klíčů.
