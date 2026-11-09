#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript pro automatické a přesné vyplnění šablony dokumentace PPRO
do formátu DOCX a následnou konverzi do PDF.
"""

import os
import subprocess
import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def set_cell_text(cell, text, bold=False, italic=False, size_pt=10, color_rgb=(0x1c, 0x19, 0x17)):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)
    return p

def main():
    template_path = "docs/PPRO-dokumentace-sablona-v1.docx"
    doc = docx.Document(template_path)

    # 1. TABULKA 0 – Metadata projektu
    t0 = doc.tables[0]
    t0_data = [
        ("Název projektu", "Půjčovna sportovního vybavení „Hory a voda“"),
        ("Zvolené zadání", "D – Půjčovna vybavení"),
        ("Jméno a příjmení", "Theo Indruch"),
        ("Repozitář na GitHubu", "https://github.com/theo-artin/ppro-pujcovna-vybaveni-d.git"),
        ("Datum poslední úpravy", "2. 11. 2026")
    ]
    for r_idx, (k, v) in enumerate(t0_data):
        row = t0.rows[r_idx]
        set_cell_text(row.cells[0], k, bold=True, size_pt=10)
        set_cell_text(row.cells[1], v, bold=False, size_pt=10)

    # 2. ÚPRAVA ODSTAVCŮ V SEKCÍCH
    # Smažeme šedý text kurzivou (P[3])
    doc.paragraphs[3].text = ""

    # Sekce 1: Popis řešení (nahradíme nápovědu P[5] a využijeme prázdné odstavce)
    desc_p1 = (
        "Aplikace představuje komplexní informační systém pro půjčovnu sportovního vybavení „Hory a voda s.r.o.“, "
        "která nabízí celoroční sortiment pro zimní i letní outdoorové sporty (lyže, snowboardy, skialpy, boty, "
        "kánoe, packrafty, rafty, pádla, vesty a helmy). Systém řeší kritický problém klienta, kterým byla dosavadní "
        "manuální evidence v papírových sešitech a telefonické rezervace na lístečcích. V sobotních ranních špičkách "
        "docházelo k overbookingu (jeden pár lyží slíben dvěma zákazníkům), vzniku dlouhých front a chybám při "
        "odbavování. Nový systém garantuje přesnou evidenci konkrétních fyzických kusů inventáře, zamezuje kolizím termínů "
        "a chrání provozní marži půjčovny."
    )
    desc_p2 = (
        "Systém slouží třem skupinám uživatelů: (1) pultovému personálu (role STAFF) pro ranní přehled inventáře, rychlé "
        "vydávání a vracení vybavení a evidenci servisu; (2) vedoucímu provozu (role ADMIN) pro kompletní správu ceníků, "
        "kategorií a uživatelských účtů; (3) koncovým zákazníkům (veřejnost) pro prohlížení ceníků, ověření okamžité dostupnosti "
        "a vytvoření online rezervace."
    )
    desc_p3 = (
        "Architektura je postavena jako třívrstvá se striktně jednosměrnými závislostmi: "
        "1. Prezentační vrstva: Klientská Single Page Application (HTML5, Modern CSS editorial design bez externích frameworků, "
        "Vanilla JS) komunikující přes asynchronní REST API. "
        "2. Aplikační a doménová vrstva: Python 3.14 a FastAPI s typovou validací přes Pydantic v2 schémata, službami pro "
        "byznys pravidla (EquipmentService, CategoryService) a bezpečnostními JWT filtry. "
        "3. Datová a perzistentní vrstva: SQLAlchemy 2.0 ORM s plnou transakční integritou ACID, verzované databázové "
        "migrace Alembic a relační databáze PostgreSQL 16 (v Docker kontejneru) s možností lokálního SQLite běhu pro CI testy."
    )
    desc_p4 = (
        "Bezpečnost a GDPR: Systém striktně chrání osobní údaje zákazníků. Pro nepřihlášené návštěvníky dochází na backendu "
        "k dynamickému maskování rezervačních kódů, jmen a kontaktů na hodnotu null. Veřejný zákazník vidí pouze štítek "
        "„Rezervováno“. Karta čekajících rezervací je přístupná výhradně personálu. Při osobním odběru zákazník sdělí kód "
        "rezervace, personál ověří shodu v systému a jedním kliknutím kus převede do stavu půjčeno (RENTED)."
    )
    desc_p5 = (
        "Uživatelské rozhraní a responzivita: Web je navržen v prémiovém světlém editorial stylu (Light mode) "
        "inspirovaném Squarespace a Adobe. Pro stolní počítače nabízí velkorysý kontejner (1560 px), ve kterém se kompletní "
        "inventární tabulka zobrazí bez vodorovného posunu. Pro mobilní telefony je implementována adaptivní dvouúrovňová "
        "hlavička s plynulým horizontálním touch-posuvem navigačních záložek, takže horní menu nikdy neuteče z obrazovky mobilu."
    )

    doc.paragraphs[5].text = desc_p1
    doc.paragraphs[6].text = desc_p2
    doc.paragraphs[7].text = desc_p3
    doc.paragraphs[8].text = desc_p4
    doc.paragraphs[9].text = desc_p5
    doc.paragraphs[10].text = ""
    doc.paragraphs[11].text = ""

    # Sekce 2: Rozhodnutí – promažeme nápovědu P[13]
    doc.paragraphs[13].text = ""

    # TABULKA 1 – Rozhodnutí (Table 1)
    t1 = doc.tables[1]
    # Smažeme stávající řádky kromě hlavičky
    while len(t1.rows) > 1:
        tr = t1.rows[-1]._tr
        tr.getparent().remove(tr)

    decisions = [
        ("R1", "Backend v Pythonu (FastAPI)", "Vysoký asynchronní výkon, nativní OpenAPI dokumentace a validace přes Pydantic v2; moderní standard pro REST mikroslužby.", "5. 10. 2026"),
        ("R2", "Databáze PostgreSQL 16 v Dockeru + SQLite pro testy", "Zadání požaduje relační DB v kontejneru (PostgreSQL); SQLite umožňuje bleskové lokální testování a offline vývoj.", "5. 10. 2026"),
        ("R3", "Řízené migrace schématu přes Alembic", "Verzování databázového schématu garantuje přesnou reprodukovatelnost změn u všech členů týmu i v Dockeru.", "5. 10. 2026"),
        ("R4", "Dvoufázový model rezervací a ochranná tolerance (ADR-001/002)", "Rezervace váže konkrétní fyzický kus (prevence overbookingu); v den výpůjčky je rezervace držena do 10:00 s tolerancí do 10:30, poté auto-uvolnění.", "5. 10. 2026"),
        ("R5", "Tarifikace časových bloků (ADR-006)", "Zavedeny 4 sazby: ranní půlden (8–13h), odpolední půlden (13–18h), celý den a víkendový balíček (pátek 14h až neděle 18h za cenu 2 dnů).", "5. 10. 2026"),
        ("R6", "Autentizace OAuth2 s JWT tokeny a role RBAC", "Bezpečný bezstavový přenos pověření; rozdělení na role ADMIN (vedoucí) a STAFF (pultový personál) a veřejné anonymní zákazníky.", "5. 10. 2026"),
        ("R7", "Frontend jako čistá SPA (HTML5, Modern CSS, Vanilla JS)", "Vysoká rychlost odezvy, nulová zátěž externími node_modules/bundlery a okamžitá spolehlivost na jakémkoli stroji.", "19. 10. 2026"),
        ("R8", "Firemní identita a design bez AI oválů (ADR-008)", "Čistý editorial Light mode (Squarespace styl), paleta Alpine Amber / Glacier Blue / Slate Ink, široký layout 1560 px pro nulový vodorovný scroll.", "19. 10. 2026"),
        ("R9", "Ochrana osobních údajů (GDPR) a oddělení pohledů (ADR-009)", "Striktní maskování dat na backendu na null pro nepřihlášené, skrytí seznamu rezervací před veřejností, veřejný rezervační koncový bod.", "2. 11. 2026"),
        ("R10", "Responzivní mobilní zobrazení pro telefony", "Dvouúrovňová mobilní hlavička s touch-posuvnými záložkami zabraňuje přetečení menu na telefonu; zachování 100% desktop vzhledu na PC.", "2. 11. 2026")
    ]

    for code, dec_title, reason, date in decisions:
        row = t1.add_row()
        set_cell_text(row.cells[0], code, bold=True, size_pt=9.5)
        set_cell_text(row.cells[1], dec_title, bold=True, size_pt=9.5)
        set_cell_text(row.cells[2], reason, bold=False, size_pt=9)
        set_cell_text(row.cells[3], date, bold=False, size_pt=9)

    # Sekce 3: Změny požadované klientem – promažeme nápovědu P[15]
    doc.paragraphs[15].text = ""

    # TABULKA 2 – Změny klienta (Table 2)
    t2 = doc.tables[2]
    while len(t2.rows) > 1:
        tr = t2.rows[-1]._tr
        tr.getparent().remove(tr)

    client_changes = [
        ("Z1", "19. 10. 2026", "„Nedávej tenhle divný dark mode, vezmi si inspiraci z webu Squarespace / Adobe / Microsoft a udělej web moderně.“", "Zrušení tmavého režimu, přechod na čistý minimalistický Light mode s paletou žuly, vápence a papíru. Viz R8.", "hotovo"),
        ("Z2", "19. 10. 2026", "„Equipment table body se nevejde na šířku do prostoru, musí se scrollovat při zoom 100%. Rozšiř hlavní strip, v horní třetině dej fotky/logo a vytvoř firemní identitu půjčovny.“", "Rozšíření kontejneru na 1560 px (eliminace scrollu na PC), doplnění hero sekce s fotkou interiéru půjčovny a hor, emblém značky a manuál docs/corporate_identity.md. Viz R8.", "hotovo"),
        ("Z3", "19. 10. 2026", "„Oprav část v ceníku, kde se tabulka cen zarovnává pod text – chci zarovnat dolů, aby délka textu neničila formátování. Na první stránce odstraň obdélníky přes obrázek.“", "Cenové tabulky v kartách kategorií zarovnány na spodní hranu flex/grid kontejneru, vyčištěna hero sekce od rušivých boxů.", "hotovo"),
        ("Z4", "19. 10. 2026", "„Na první stránce je nadpis a logo dvakrát. Když se kus rezervuje, ukazuje se jen možnost vrátit – chci označit jako půjčený při vyzvednutí nebo zrušit rezervaci. Rezervovaný kus nesmí jít půjčit nikomu jinému a v systému musí být vidět číslo rezervace pro kontrolu.“", "Odstranění duplicitního loga z overlaye, přidán stav RESERVED, generování kódu rezervace (REZ-YYYY-XXXX), tlačítka obsluhy „Vydat (půjčit)“ a „Zrušit rez.“, zablokování rezervovaného kusu pro další zájemce. Viz R4.", "hotovo"),
        ("Z5", "2. 11. 2026", "„Data zákazníka s rezervací jsou vidět i pro nepřihlášené uživatele, to je špatně. Nepřihlášení jsou jen zákazníci a stačí jim vidět, že je to rezervováno, ale další data ne. Vůbec neukazuj seznam rezervací na stránce s rezervací, pokud nejde o admina nebo obsluhu.“", "Implementováno backendové GDPR maskování na null v GET /api/v1/equipment/ pro anonymy, zákaznická data v tabulce skryta, karta aktivních rezervací se zobrazuje výhradně přihlášenému personálu. Zaveden veřejný endpoint POST /api/v1/equipment/{id}/reserve. Viz R9.", "hotovo"),
        ("Z6", "2. 11. 2026", "„Uprav to i pro zobrazení na telefonu. Nech ten web stejný beze změn pro PC a přidej formátování pro mobily, aby např. horní záložky neodešly z prostoru mobilu.“", "Přidány responzivní CSS media queries: adaptivní mobilní hlavička s touch posuvem záložek, přizpůsobení vyhledávání, tlačítek a formulářů na malé displeje bez ovlivnění PC zobrazení. Viz R10.", "hotovo")
    ]

    for code, date, req, sol, status in client_changes:
        row = t2.add_row()
        set_cell_text(row.cells[0], code, bold=True, size_pt=9.5)
        set_cell_text(row.cells[1], date, bold=False, size_pt=9)
        set_cell_text(row.cells[2], req, italic=True, size_pt=9)
        set_cell_text(row.cells[3], sol, bold=False, size_pt=9)
        set_cell_text(row.cells[4], status, bold=True, size_pt=9, color_rgb=(0x15, 0x80, 0x3d) if status == "hotovo" else (0x00, 0x00, 0x00))

    # Uložení vyplněného DOCX souboru
    output_docx = "docs/PPRO-dokumentace-Hory-a-voda.docx"
    doc.save(output_docx)
    print(f"DOCX úspěšně uložen do: {output_docx}")

    # Aktualizace i původního souboru šablony
    doc.save(template_path)
    print(f"Šablona aktualizována v: {template_path}")

    # 3. KONVERZE DO PDF POMOCÍ LIBREOFFICE
    cmd = ["libreoffice", "--headless", "--convert-to", "pdf", output_docx, "--outdir", "docs/"]
    print("Spouštím konverzi do PDF přes LibreOffice...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        pdf_path = "docs/PPRO-dokumentace-Hory-a-voda.pdf"
        print(f"PDF dokumentace úspěšně vytvořena v: {pdf_path}")
    else:
        print("Chyba při konverzi do PDF:", res.stderr)

if __name__ == "__main__":
    main()
