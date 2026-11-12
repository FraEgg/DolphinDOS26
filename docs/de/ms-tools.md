# MS-Tools

C64-Programme (C64-Modus, 6510; am C128 nach `GO 64`) für den 1541 Switchless
Multi-Speeder V3 mit DolphinDos26, by Frank Eggen. Jedes Tool lädt wie ein
BASIC-Programm und startet mit `RUN`:

```
LOAD"MS-STATUS",8
RUN
```

Jedes Tool trägt dieselbe Kennung, bei `LIST` und nach `RUN`:

```
10 REM MS-STATUS BUILD 1 / 2026
20 REM BY FRANK EGGEN
30 REM SWITCHLESS MULTI-SPEEDER V3
40 SYS2147
```

Die Buildnummer steht in `buildnr/<tool>.nr` und erhöht sich bei jedem
erfolgreichen Assemblieren des Tools (Quelltext, Includes oder gemeinsame
Routinen geändert); die Jahreszahl ist das Jahr des Builds.

## Oberfläche

Tools mit Bedienung nutzen die gemeinsame PETSCII-Oberfläche (`src/ui.s`,
`include/ui.inc`). Alle Texte der Oberfläche sind englisch (die Kommentare im
Quelltext deutsch):

- Rahmen und Hintergrund rot, Text weiß, Hervorhebungen gelb,
  Nebeninformation hellgrau, Erfolg hellgrün
- Zeile 0 Titelbalken (weiß revers): Toolname links, Build rechts;
  Zeile 1 SWITCHLESS MULTI-SPEEDER V3 (gelb), Zeile 2 BY FRANK EGGEN (grau),
  Zeile 3 Trennlinie; Zeile 24 Hilfezeile (weiß revers)
- Menü: CRSR hoch/runter wählt (gelber Reversbalken), RETURN bestätigt,
  RUN/STOP oder `←` beendet; mit `ui_mlr` melden CRSR links/rechts einen
  geänderten Wert (z. B. Anzahl der Läufe)
- beim Beenden (`ui_exit`) Rahmen, Hintergrund, Textfarbe und
  Zeichensatz-Umschaltung wie vor dem Programmstart (merkt `ui_init`), dann
  leerer Bildschirm in dieser Textfarbe

Routinen: `ui_init`, `ui_exit`, `ui_puts` (Text bei `ui_row`/`ui_col` in
`ui_color`, `ui_rev`), `ui_clrrow`, `ui_help`, `ui_menu` (`ui_mtab`,
`ui_mcnt`, `ui_msel`), `ui_getkey`.

## Aufbau

| Datei | Inhalt |
|---|---|
| `ms-tools.d64` | Diskette "MS-TOOLS", ID 26 – `make` schreibt die Tools hierher |
| `src/<tool>.s` | ein Tool (ca65): `.define TOOLNAME "NAME"`, `.include "tool.inc"`, dann der Einsprung |
| `include/tool.inc` | BASIC-Vorspann (REM-Zeilen + SYS, Adresse berechnet) und Titeltext `ms_title` |
| `src/common.s` | gemeinsame Routinen für Textausgabe: `ms_header` (Titel + Trennlinie), `print` |
| `src/drive.s`, `include/drive.inc` | Laufwerksroutinen: Kanal 15, Befehl, `M-E` mit Parametern, `M-R` (beide mit Wiederholung), Statusmeldung; Adressen der MS-Addon-API |
| `src/ui.s`, `include/ui.inc`, `include/ui_def.inc` | PETSCII-Oberfläche (siehe oben) |
| `include/kernal.inc` | KERNAL-Einsprünge, Zeropage, PETSCII |
| `c64-prg.cfg` | ld65: Ladeadresse $0801, BASIC-Vorspann, dann Code des Tools, dann common |
| `src/drv-<name>.s`, `drive.cfg` | Laufwerksprogramme (ab $0400, höchstens 512 Bytes), per `.incbin` im Tool, per M-W hochgeladen und per M-E gestartet |
| `buildnr/<tool>.nr` | Buildnummer je Tool |
| `tests/test_tools.py` | LOAD, LIST, RUN, Oberfläche, Farben und Beenden jedes Tools im gepatchten VICE (GUI); vor jedem Start andere Farben gesetzt, nach dem Beenden müssen Rahmen, Hintergrund und Textfarbe wieder so sein |
| `tests/test_memtest.py` | MS-MEMTEST: Laufwerk 9 (fehlt) wählen, Lauf ohne Fehler, Lauf mit per Monitor verfälschtem Byte, DolphinDOS danach |
| `tests/test_fastcopy.py [on/off] [40] [side2]` | MS-FASTCOPY: lesen und zwei Kopien, Ziel-D64 byte-gleich zur Quelle |
| `tests/test_fastcopy_reu.py [fall]` | MS-FASTCOPY mit REU: VIA1/PIA-Erkennung, Kopien byte-gleich, 40 Spuren, Formatieren, Schreibschutz, ohne REU/Parallel |
| `tests/test_fastcopy_d64.py [fall]` | MS-FASTCOPY: IMPORT/EXPORT D64 FILE mit MS-RAM und REU, 35/40 Spuren, Datei = Diskette, ungültige Dateien |
| `tests/test_fastcopy_fast.py [fall]` | MS-FASTCOPY `TRANSFER: FAST`: VIA1, PIA, DD2, 40 Spuren, unformatiert, Schreibschutz |
| `tests/test_fastcopy_led.py` | MS-FASTCOPY: rote LED beim Lesen/Schreiben, DIRECTORY mit Blättern, fehlendes Laufwerk |
| `tests/test_nibcopy.py` | MS-NIBCOPY: Lesen/Schreiben über MS-RAM und REU, Ziel bitweise = Quelle, TRACK INFO, Presets (20 Prüfungen) |
| `tests/test_rs232.py` | MS-RS232: LIST-Kopf, Installieren, Senden/Empfangen über die RS-232-Emulation von VICE (TCP-Testserver), Floppyzugriff bei offener RS-232-Datei, Aushängen, Wiedereinhängen (8 Prüfungen) |
| `tests/test_import.py [name\|test] [reu]` | MS-NIBCOPY: IMPORT G64 FILE von Laufwerk 9, WRITE DISK, Ziel = G64-Datei, bei Spielen Start der Kopie |
| `tests/test_nibcopy_index.py [1571\|cr\|1541] [off]` | MS-NIBCOPY: Kopie mit Indexloch (1571, 1571CR im C128DCR), gleiche Lage jeder Spur zum Loch; 1541: passender Payload ohne Index |
| `tests/test_nibcopy_1571.py [1571\|cr]` | MS-NIBCOPY: Befehle des 1571-Payloads (INDEX, READ/WRITE ab Index) direkt |
| `tests/test_nibcopy_dir.py` | MS-NIBCOPY: DIRECTORY, END TRACK nach dem Import, Spuren im MS-RAM überstehen das Directory |
| `tests/test_nibcopy_names.py [Füllbyte ...]` | MS-NIBCOPY: Vorschlag und Eingabe von Laufwerk und Dateiname bei vorbelegtem RAM |
| `tests/test_led.py` | MS-NIBCOPY: rote LED beim Lesen an, danach aus |
| `tests/test_export.py [name\|test] [reu]` | MS-NIBCOPY: EXPORT G64 FILE auf Laufwerk 9 (Verzeichnis), Datei = Quelle, bei Spielen aus `../G64` Start der exportierten Datei |
| `tests/test_protected.py` u. a. | MS-NIBCOPY mit G64-Images mit Kopierschutz (Ordner `../G64`), Profiling (`profile_*.py`) |

## Bauen

```
make          # Tools bauen, packen, auf ms-tools.d64 schreiben (gleichnamige ersetzen)
make clean
```

Auf die Diskette kommen die mit **Exomizer 3** gepackten Fassungen
(`build/<name>.exo.prg`, `tools/exopack.py`). Der BASIC-Vorspann mit Name,
Build und Autor bleibt ungepackt vorne (LIST zeigt ihn wie bisher), dahinter
steht die selbstentpackende Datei, assembliert für genau die Adresse, auf
die das `SYS` zeigt (`exomizer3 sfx <einsprung> -n -Di_load_addr=… -Di_raw=1`;
`-n`: kein Rahmenflackern, die Tools merken sich beim Start die Farben).
Nach dem Entpacken springt sie an den Einsprung des Tools. Exomizer 3.1
baut man aus `../Referenzen/krill-loader-v194/loader/tools/exomizer-3.1/src`
(`make`) und legt das Programm als `exomizer3` in den Pfad
(`make EXOMIZER=…` für einen anderen Ort). Ersparnis: MS-NIBCOPY 86 → 47,
MS-FASTCOPY 17 → 12, MS-MEMTEST 15 → 12 Blöcke.

Neues Tool: `src/<name>.s` anlegen, `<name>` in `TOOLS` im Makefile eintragen,
Testfall in `tests/test_tools.py` ergänzen.

## Tools

| Name | Funktion |
|---|---|
| `MS-STATUS` | Fehlerkanal des Laufwerks anzeigen, Menü READ STATUS / QUIT (Vorlage für weitere Tools) |
| `MS-MEMTEST` | RAM-Test der 512 KB SRAM (64 Bänke): 4 Muster, 1-99 Läufe, Anzeige je Bank |
| `MS-FASTCOPY` | Diskettenkopie über das 512-KB-RAM (Datenkopie wie CDR/CDW), 35/40/AUTO Spuren, Verify an/aus, CDR1/CDR2 und CDW1/CDW2, mehrere Kopien |
| `MS-NIBCOPY` (BETA) | Nibble-Kopierer nach dem Vorbild der nibtools: Spuren bitgenau lesen und schreiben (Syncs, Lücken, Spur 36–42, Halbspuren, Weak Bits), Ablage im Multi-Speeder-RAM oder in der REU; läuft auch mit DolphinDos26UL (C64U), dann nur mit REU |
| `MS-RS232` | RS-232-Treiber für Gerät 2 am User-Port (der DolphinDos26-Kernal hat keine RS-232-Routinen): Routinen des Original-Kernals im RAM bei $9800-$9FFF, OPEN 2,2,… wie beim Original-C64 |

### MS-MEMTEST

Das Prüfprogramm `src/drv-memtest.s` läuft im Laufwerk. Ein Lauf: für jedes
Muster (`$55`, `$AA`, Adresse = Offset ⊕ Seite ⊕ Bank, Adresse invertiert)
erst Bank 1-63 füllen, dann alle prüfen – so fallen auch überlagerte Bänke
oder Seiten auf. Bank 0 (Arbeits-RAM von DolphinDOS) wird am Ende in einem
Aufruf getestet und dafür in Bank 1 gesichert. Der übrige RAM-Inhalt
(CDR-Seiten, RAM-Disk) geht verloren: das Tool schaltet vorher die RAM-Disk
ab (`CDM0`).

Anzeige: 8×8 Bänke (logische Nummern 00-63), grau = offen, gelb revers =
wird getestet, grün = OK, schwarz revers = FAIL (bleibt über alle Läufe),
dazu Anzahl fehlerhafter Bytes und der erste Fehler mit Bank, Adresse, Soll
und Ist. Ein Lauf dauert etwa 2 Minuten.

Menü: START TEST, RUNS (1-99), DRIVE (8-11, voreingestellt das Laufwerk, von
dem das Tool geladen wurde), QUIT; Werte mit Cursor links/rechts oder RETURN
ändern. Die Laufwerksroutinen kommen aus `src/drive.s` (`M-E`/`M-R` werden
bei Übertragungsfehlern bis zu dreimal wiederholt).

### MS-FASTCOPY

> **Achtung:** Mit Speicher `MS-RAM` überschreibt das Tool beim Lesen und beim D64-Import
> den Inhalt des gewählten Slots, also die CDR-Seite und eine dort liegende RAM-Disk.
> Wichtige Daten vorher mit `@CDW1` bzw. `@CDW2` auf Diskette sichern.

Mindestanforderungen an die Hardware: C64 oder C128 im C64-Modus; für den Speicher MS-RAM
eine 1541 mit Switchless Multi-Speeder V3 und DolphinDos26 oder DolphinDos26DD2 (MS-Addon-API);
für den Speicher REU ein aktives Parallelkabel, ein DolphinDOS-Kernal (empfohlen
`C64DolphinDos26.bin`) und eine REU ab 256 KB (zwei Slots ab 512 KB). Eine der beiden Ablagen
(MS-RAM oder REU) ist zwingend nötig; ohne sie wird nicht kopiert, es bleibt nur DIRECTORY.

Kopiert eine Diskette in einem Durchgang über das RAM des Multi-Speeders,
Spur für Spur mit Anzeige (Datenkopie wie `CDR`/`CDW`).
Benutzt die MS-Addon-API von DolphinDos26 (Sprungtabelle ab `$3FFF`, siehe
`dd25/README.md`).

Menü zweispaltig wie bei MS-NIBCOPY: links `SETTINGS`, rechts `ACTIONS`.
CRSR hoch/runter geht durch alle Punkte, CRSR links/rechts ändert eine
Einstellung bzw. springt von rechts nach links.

- Einstellungen (CRSR links/rechts oder RETURN):
  - `STORAGE` – `MS-RAM 1/2`: eine der beiden RAM-Hälften des Multi-Speeders
    (intern Seite 1/2 wie `CDR1`/`CDR2`), `REU 1/2`: je 256 KB am oberen Ende
    der REU (1 Slot ab 256 KB, 2 ab 512 KB); Lesen und Schreiben benutzen immer
    den gewählten Speicher. Die REU geht auch ohne Multi-Speeder und ohne API,
    aber nur mit Parallelverbindung: Das Tool prüft sie beim Start und bei jedem
    Laufwerkswechsel und zeigt `PARALLEL: PIA` bzw. `PARALLEL: VIA1` (auch an DolphinDos26DD2, dessen
    PIA nur die RAM-Bänke schaltet, und am Original-DolphinDOS 2.0 aus Bank 2, ab Build 29); ohne sie
    `NO PARALLEL`, und REU wird nicht angeboten. Die Sektoren laufen dabei über
    `U1`/`U2` (langsamer als `MS-RAM`, das nur im Laufwerk arbeitet). MS-NIBCOPY
    benutzt die REU von unten: Bei einer kleinen REU können sich die Daten beider
    Tools überschreiben, das Tool erkennt das nicht in jedem Fall
  - `TRACKS: 35/40/AUTO` – AUTO prüft Spur 36 wie `CDR`
  - `TRANSFER: FAST/DOS` – gilt für `STORAGE: REU` und für `COPY DISK` mit `STORAGE: MS-RAM`
    (Roh-Weg, siehe unten). Bei der REU ist `FAST` (Voreinstellung) ein eigener
    Laufwerkscode (`src/drv-fast.s`, je eine Fassung für VIA1 und PIA): rohes GCR im Takt der
    Diskette über das Kabel, gemeldet durch Flanken der CLK-Leitung; die Spur wird am C64
    gewandelt und geprüft, beim Schreiben komplett neu erzeugt (Spur vorab gelöscht).
    Bildschirm während der Sitzung aus. In VICE etwa 30 s Lesen, 44 s Schreiben mit Verify
    für 35 Spuren. `DOS` ist der langsamere Weg über `U1`/`U2`
  - `VERIFY: ON/OFF` – XV nur für das Schreiben
  - `DRIVE: 8-11` – voreingestellt ist das Laufwerk, von dem das Programm
    geladen wurde; beim Wechsel wird die API auf dem neuen Laufwerk geprüft
    ("DRIVE 09: NO MS-ADDON API", wenn sie fehlt)
- Aktionen: `COPY DISK` (lesen, dann schreiben), `READ DISK`, `WRITE DISK`; nach
  jedem Schreiben fragt `ANOTHER COPY?` – so entstehen beliebig viele Kopien aus
  einer Lesung
- `EXPORT D64 FILE` / `IMPORT D64 FILE`: Inhalt des Speichers als D64-Datei auf
  ein Laufwerk schreiben bzw. von dort laden, typischerweise ein SD2IEC. Dialoge
  wie bei MS-NIBCOPY (`EXPORT TO DRIVE: 09`, `FILE NAME:`, `.D64` wird
  angehängt, eine vorhandene Datei wird beim Export ersetzt). Import: 35 oder 40
  Spuren, auch mit Fehlertabelle (wird ignoriert), andere Größen melden
  `NOT A VALID D64 FILE`. Bei `MS-RAM` kann dessen Laufwerk nicht Ziel oder Quelle
  sein; das Schreiben ins MS-RAM braucht keine neue API (Sektor per `#0` nach
  `$0300`, Code im `M-E`-Befehl kopiert ihn in die Bank)
- `DIRECTORY` zeigt das Inhaltsverzeichnis der Diskette im gewählten Laufwerk
  (CRSR hoch/runter: Zeile, links/rechts: Seite, RETURN oder `←`: zurück);
  geht auch ohne MS-Addon-API. Bis 160 Zeilen; die letzte (`BLOCKS FREE`)
  bleibt immer sichtbar
- Die rote LED leuchtet während des gesamten Lesens und Schreibens: Das Tool
  hält in der Sitzung einen Direktzugriffskanal (`#`) offen, denn die
  Idle-Schleife des DOS schaltet die LED sonst nach jedem Befehl aus;
  API-OPEN/-CLOSE schalten sie selbst ein (Code im `M-E`-Befehl, kein ROM-Eingriff)
- Ist die Zieldiskette nicht lesbar (Lesefehler 20-29 beim Öffnen), fragt
  das Tool `NOT FORMATTED - FORMAT 35 TRACKS?` (bzw. 40) und formatiert bei
  RETURN mit `N:` – Name und ID aus der BAM der Quelle im RAM-Slot (API E6),
  damit die ID der Sektorheader zur kopierten BAM passt
- Raster der Spuren 1–40: grau offen, gelb revers aktuell, grün fertig,
  schwarz revers Fehler; darunter Tätigkeit, Meldung des Laufwerks und die
  Spuranzahl der beiden RAM-Slots

**Roh-Weg ins MS-RAM (`COPY DISK`, `STORAGE: MS-RAM`, `TRANSFER: FAST`):** Eigener Laufwerkscode
(`src/drv-fast.s` mit `-D RAW`, ein Teil bei `$0300`, der Rest bei `$7000` in Bank 0) liest die
Spuren roh als GCR direkt in die Bänke (Slot 1: Bank 1-31, Slot 2: Bank 32-62, Kennung in Bank 63,
25 Sektoren je Bank) und schreibt sie von dort zurück, mit eigener Prüfung (vier Paritäten) und
Verify im Laufwerk. In VICE etwa 18 s Lesen, 30 s Schreiben mit Verify für 35 Spuren.

> **Achtung:** Nach `COPY DISK` mit dem Roh-Weg steht der Slot **roh** im RAM und wird nicht
> zurückgewandelt. `@CDW1`/`@CDW2` und die RAM-Disk `@CDM` würden daraus Unsinn machen. Im Tool wird
> ein Roh-Slot erkannt: `WRITE DISK` schreibt ihn richtig, `EXPORT D64 FILE` lehnt ihn ab
> (`RAW COPY IN SLOT`), `READ DISK` und `IMPORT D64 FILE` machen den Slot wieder normal.

### MS-15SECCOPY

Eine neue Fassung von **15 Seconds Copy**, das **Mike Pall** 1986 geschrieben hat.
Danke an Mike Pall für seine Pionierarbeit! Kopiert normal formatierte Disketten als rohes GCR über
das Parallelkabel, mit Spur- und Sektorraster und Oberfläche nach MS-FASTCOPY. Liegt auf
`ms-tools.d64` und zusätzlich auf der eigenen Diskette `ms-15seccopy.d64`, Quelltext in `15SecCopy/neu/`.

Mindestanforderungen:

| Komponente | Mindestanforderung |
|---|---|
| C64 | C64 oder C128 im C64-Modus, auch C64U |
| REU (zwingend) | mindestens 256 KB für 35 Spuren, 512 KB für 40 Spuren |
| Parallelkabel (zwingend) | am VIA1 der 1541 (SpeedDOS-Kabel) oder am PIA (DolphinDOS 3, Multi-Speeder); liegt bei `$5000` kein PIA (z. B. unter DolphinDOS 2.0 auf dem Multi-Speeder), ist `PIA` gesperrt (`NO PIA AT $5000 IN THIS DRIVE ROM`); ob ein Kabel steckt, prüft das Programm nicht |
| Laufwerk | 1541 oder 1571 als Gerät 8; das Original-ROM genügt, DolphinDos26, Multi-Speeder und RAM-Erweiterung sind nicht nötig; eine 1571 mit DolphinDOS stellt das Programm für `BACKUP` und `VERIFY` mit `X-` auf 1 MHz und danach mit `X+` wieder auf 2 MHz |
| C64-Kernal | der Original-Kernal genügt |

Auf echter Hardware (C64U, 1541, REU) liefen `BACKUP` und `VERIFY` über alle 683 Blöcke ohne Fehler,
am VIA1 unter DolphinDOS 2.0 und am PIA unter DolphinDos26DD2; 35 Spuren brauchten höchstens 12 s
zum Lesen und 18 s zum Schreiben. Quelle und Ziel waren dabei dieselbe Diskette.

> **Achtung:** Das Programm benutzt die REU als Zwischenspeicher. Dort abgelegte Daten, auch Slots
> von MS-FASTCOPY und MS-NIBCOPY, können überschrieben werden.

### MS-NIBCOPY (BETA)

> **Achtung:** Mit Ablage `MS-RAM` überschreibt das Tool beim Lesen und beim G64-Import
> fast das gesamte RAM des Multi-Speeders (Bank 1-63), also beide CDR-Seiten und eine
> RAM-Disk. Wichtige Daten vorher mit `@CDW1` und `@CDW2` auf Diskette sichern.

**BETA:** MS-NIBCOPY befindet sich im BETA-Stadium und wird weiterentwickelt. Funktionen und
Bedienung können sich noch ändern; auf echter Hardware ist es erst teilweise getestet. Die
Oberfläche zeigt `MS-NIBCOPY BETA`.

Auf echter Hardware (C64U mit einer 1541, Multi-Speeder V3 mit DolphinDos26DD2 am VIA1) liest und
schreibt es normale Disketten mit MS-RAM und REU (35 Spuren, Verify an, Dateien danach byte-gleich).

Mindestanforderungen an die Hardware: C64 oder C128 im C64-Modus; 1541 mit Switchless
Multi-Speeder V3 und DolphinDos26 oder DolphinDos26DD2, 1571/1571CR (C128DCR) mit Multi-Speeder
und DolphinDos26 für die 1571, oder DolphinDos26UL (C64U bzw.
DolphinDOS-2-Hardware); aktives Parallelkabel (PIA oder VIA1); Speicher MS-RAM (nur Multi-Speeder)
oder eine REU, die für die letzte Spur reicht (512 KB für 35-40 Spuren, ab 1 MB für Spur 42 mit
Halbspuren). Eine der beiden Ablagen ist zwingend nötig; unter DolphinDos26UL nur die REU, ohne sie
zeigt das Tool `NEED REU` und sperrt Lesen und Schreiben.
MS-NIBCOPY ist nicht mit DolphinDOS 2 getestet.

**1571 und C128:** Beim Verbinden wählt das Tool den Laufwerks-Payload nach dem Einschalttext im
Laufwerks-ROM (`…1571` bei `$E5C4`): an der 1541 wie bisher (PIA oder VIA1-Kabel), an der 1571 die
1571-Fassung (`src/drv-nib.s` mit `-D D1571`: nur PIA, Seite 0, 1 MHz für alles mit Byte-Ready,
2 MHz für die Übertragung). Beide Payloads liegen nach dem Start im RAM unter dem I/O-Bereich
(`$D000`). Mit der 1571 nutzt das Tool das **Indexloch** (EDIT PRESET: `INDEX HOLE AUTO/OFF`,
Byte 7 der Voreinstellung, 0 = AUTO): Der Payload erkennt es am Bit, das sich an `$2000` mit dem
Loch ändert (WD1770 Bit 1 an der 1571, MOS 5710 Bit 6 an der 1571CR; `$D0` an den WD1770 nur,
wenn sich ohne nichts ändert), liest jede Spur ab dem Loch und schreibt sie mit einem Vorlauf nach
dem Loch so, dass sie dieselbe Lage zum Loch hat wie im Original; die Naht bleibt in einer Lücke.
Auf dem **C128** (im C64-Modus, erkannt an `$D030`) rechnet und überträgt das Tool mit 2 MHz;
während READ/WRITE ist das VIC-Bild dunkel und je Spur kurz zu sehen. Gemessen (Emulator, Spur
1–35 mit Indexloch): C128DCR Lesen 115 s / Schreiben 134 s, C64 mit 1571 138 s / 174 s.


Nibble-Kopierer nach dem Vorbild der nibtools
(github.com/rittwage/nibtools), auf den C64 portiert. Ein Payload
(`src/drv-nib.s`, 1280 Bytes, `$0300–$07FF`, damit voll; Variablen im Befehlspuffer
`$0200`) wird per M-W nach `$0300` geladen und per M-E gestartet; er
spricht über das Parallelkabel mit dem C64 (`src/nibdrv.s`). Welches Kabel
im Laufwerk steckt, erkennt der Payload beim Start selbst: Sitzt bei `$5000`
ein 6821-PIA (Multi-Speeder bzw. DolphinDOS-3-Kabel; Prüfung über das
DDRA/ORA-Umschalten mit CRA Bit 2), arbeitet er über den PIA, sonst über
das SpeedDOS-Kabel am VIA1 (`$1801`, CB1/CA2) wie DolphinDos26UL am C64
Ultimate. Auch die Firmware DolphinDos26DD2 (letztes Zeichen der
Einschaltmeldung `$E5C7` = `$B2`) nutzt das VIA1-Kabel; ihr PIA schaltet nur
die RAM-Bänke, MS-RAM bleibt als Ablage verfügbar. Die C64-Seite ist für beide Kabel gleich. Im VIA-Betrieb prüft der
Payload DATA beim Warten nur etwa einmal pro Sekunde, weil jedes Lesen von
`$1800` das CB1-Flag löscht. Die Auswertung läuft auf dem C64: Dichte (`scan_track`),
Zyklus und Ausrichtung (`src/nibana.s`), Schreibpuffer (`src/nibwr.s`),
Weak Bits (`src/nibweak.s`), REU (`src/reu.s`).

Warum langsamer als nibtools am PC mit XUM1541: Eine volle Spur braucht beim Lesen rund
1,5 s (VICE, `tests/profile_nibcopy.py`): 220 ms lesen, 363 ms übertragen, rund 850 ms
Auswertung auf dem 6510. nibtools rechnet dieselben Schritte auf dem PC und hat das Verify
beim Schreiben in der Vorgabe aus (`track_match = 0`), hier ist VERIFY in der Vorgabe an.
Das Laufwerk selbst ist kein großer Unterschied: nibtools holt an einer 1541 die Rohdaten
ebenfalls über ein Parallelkabel, 8 KB je Spur.

- Hauptmenü zweispaltig: links SETTINGS – PRESET (STANDARD / EXTENDED /
  CUSTOM 1-3), END TRACK, HALFTRACKS, EDIT PRESET (Spuren, Halbspuren,
  ALIGNMENT, DENSITY, RETRIES, VERIFY, SAVE PRESETS als `MS-NIBCOPY.CFG`),
  DRIVE 8-11, STORAGE; rechts ACTIONS – COPY DISK, READ DISK, WRITE DISK
  (danach ANOTHER COPY?), IMPORT G64 FILE, EXPORT G64 FILE, TRACK INFO, DIRECTORY, QUIT.
  CRSR auf/ab geht durch alle Punkte, CRSR links/rechts ändert eine
  Einstellung bzw. springt aus der rechten Spalte nach links
- Während Lesen und Schreiben leuchtet die rote LED des Laufwerks (Payload:
  mit dem Motor; danach setzt das DOS sie wieder selbst)
- DIRECTORY: Inhaltsverzeichnis des gewählten Laufwerks wie bei MS-FASTCOPY
  (CRSR auf/ab: Zeile, links/rechts: Seite; RETURN oder `_`: zurück). Die Spuren
  im Speicher bleiben erhalten; der Payload wird danach neu geladen, weil die
  DOS-Puffer dort liegen, wo er steht
- STORAGE: MS-RAM (Spur t -> Bank t, Halbspuren Bank 43-62) oder REU
  (8 KB je Platz, Größe wird erkannt; im Laufwerk dient Bank 63 als Puffer)
- Schreiben: Schreibschutz, Drehzahl und Kapazität je Dichte messen, dann
  Spur für Spur mit Verify (bis zu 3 Versuche)
- EXPORT G64 FILE: den Speicher (MS-RAM oder REU) als G64-Datei auf ein
  anderes Laufwerk schreiben, z. B. ein SD2IEC. Abfrage `EXPORT TO DRIVE:`
  (CRSR links/rechts 8-11, RETURN; das Gerät wird geprüft; bei MS-RAM ist
  das Lese-Laufwerk gesperrt, weil es die Daten liefert) und
  `FILE NAME:` (bis 12 Zeichen, `.G64` wird angehängt, gleichnamige Datei
  wird ersetzt). Je Halbspur wie beim Schreiben ausgerichtet, Syncs
  verlängert; Spurlänge = Kapazität der Dichte bei 300 U/min (längere
  Spuren: ihre Länge), Weak Bits als `$00`; G64 mit 84 Plätzen zu 7928
  Bytes (etwa 300 KB). Bei MS-RAM öffnet das Tool je Spur kurz eine
  Payload-Sitzung, damit der serielle Bus für das Ziel frei ist.
- IMPORT G64 FILE: G64-Datei von einem Laufwerk (`IMPORT FROM DRIVE:`,
  `FILE NAME:`) in den Speicher laden, danach WRITE DISK. Je Halbspur:
  Daten nach TBUF, bis 8192 Bytes wiederholt, Killer/ohne Sync erkennen,
  auswerten wie eine Lesung; passt die gefundene Länge nicht zur Datei,
  gilt die Spur ab ihrem Anfang. Die Bytes werden unverändert geschrieben
  (nur Syncs aus mindestens zwei `$FF` werden angepasst), auch kurze Syncs
  und Weak Bits bleiben erhalten. Die Spuren der Datei müssen in
  aufsteigender Reihenfolge liegen (VICE, nibtools, EXPORT G64 FILE). Danach
  zeigt END TRACK die letzte Spur der Datei (Wert der aktuellen Voreinstellung,
  gilt also auch für die nächste Lesung; gespeichert nur mit SAVE PRESETS).
- Speicher: Programm $0801-$5FFF, CODE2 (Import, Export, Menü) wird
  dahinter mitgeladen und beim Start nach $A000 kopiert (BASIC-ROM aus,
  beim Beenden wieder an); die wartende Halbspur liegt unter dem KERNAL
  bei $E000 (Zugriff ohne Interrupts)
- **DolphinDos26UL (C64U, ohne Multi-Speeder):** beim Verbinden liest das
  Tool per M-R den Text der Einschaltmeldung im Laufwerks-ROM (`$E5B8`,
  „OLPHINDOS26 C64U“). Erkannt: Anzeige `READY - DRIVE 08 (C64U)`, STORAGE
  fest REU; ohne REU `NONE (NEED REU)`, Lesen/Schreiben werden mit
  `C64U FIRMWARE: STORAGE NEEDS A REU` abgelehnt. Spurpuffer sind dann die
  8 KB Laufwerks-RAM bei `$6000`; nach jeder Sitzung setzt das Tool das
  Laufwerk selbst mit `UJ` zurück (DolphinDos26UL stellt dabei seine
  Grundeinstellung wieder her). Übertragung über das VIA1-Kabel des C64U.
- Tests (VICE, GUI): `tests/test_nibcopy.py` (Multi-Speeder, PIA) und
  `tests/test_nibcopy_ul.py` (DolphinDos26UL, Standard-Parallelkabel am VIA1
  ohne PIA, REU; `UL_ROM`, `MS_PORT`).

### MS-RS232

Der DolphinDos26-Kernal hat – wie schon der DolphinDOS-Kernal – keine
RS-232-Routinen; ihr Platz ($EEBB-$F0BC, NMI-Teil, OPEN) wird für
Parallel-LOAD/SAVE und JiffyDOS gebraucht (zusammen rund 1000 Bytes, frei
sind im Kernal nur 167). MS-RS232 bringt sie als RAM-Treiber zurück:

- `src/rs232drv.s`, gebunden für `$9800` (`rs232drv.cfg`), per `.incbin`
  im Tool: Senden, Empfangen, NMI und OPEN befehlsgleich aus den CBM-Quellen
  `KERNAL_C64_03` (rs232trans/rcvr/inout/nmi, open, channelio, irqfile)
- Speicher `$9800-$9FFF`: Code bis `$9DFF`, Empfangspuffer `$9E00`,
  Sendepuffer `$9F00`; das BASIC-Speicherende wird auf `$9800` gesenkt
- eingehängt in die Kernal-Vektoren NMINV, IOPEN, ICLOSE, ICHKIN, ICKOUT,
  IBASIN, IBSOUT, IGETIN, ILOAD, ISAVE: Gerät 2 erledigt der Treiber, alles
  andere geht an den Kernal weiter; vor Zugriffen auf andere Geräte ruhen die
  RS-232-NMIs (RSP232 wie im Original vor seriellen Zugriffen) – Floppy und
  Dolphin-Parallelkabel (FLAG an CIA 2) werden nicht gestört
- eigene Variablen statt der Original-Adressen ($A7-$AB, $B4-$B6, $BD,
  $F7-$FA, $0293-$029E), weil der DolphinDos26-Kernal diese selbst benutzt;
  nur ENABL ($02A1) bleibt (NMI-Ende des Kernals bei $FEB6)
- Status: READST liefert im DolphinDos26-Kernal immer ST ($90); der
  RS-232-Status wird nach jedem Zeichen nach ST kopiert und gelöscht
- Fehlerbehebung gegenüber dem Original: beim Einschalten des Empfangs
  (CHKIN) wird ein Startbit erwartet (RINONE); im Original wurde das erste
  Zeichen danach oft um ein Bit verschoben gelesen (im VICE-Test: „?ORLD“
  statt „WORLD“)
- `SYS 38912` hängt wieder ein (z. B. nach RUN/STOP-RESTORE), `SYS 38915`
  hängt aus und setzt das Speicherende wieder auf `$A000`; ist der Treiber
  schon eingehängt, kopiert MS-RS232 ihn nicht neu
- Beispiel: `OPEN 2,2,0,CHR$(8)` = 1200 Baud 8N1 (`CHR$(6)` 300,
  `CHR$(10)` 2400), `PRINT#2,A$`, `GET#2,A$`, `CLOSE 2`
- RS-232 und das Dolphin-Parallelkabel teilen sich den User-Port; der
  Treiber prüft beim Einhängen, ob die NMI-Behandlung des Kernals bei
  `$FE56`/`$FEB6` liegt (Original-Kernal und DolphinDos26)
