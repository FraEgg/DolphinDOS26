# DolphinDos26 – Quelltext

Kommentierter ca65-Quelltext von DolphinDos26 für den 1541 Switchless
Multi-Speeder V3 DD3 (512 KB). DolphinDos26 ist die Weiterentwicklung der
Firmware `1541DolphinDos25.bin` (26 = Jahr 2026). Der unveränderte Stand
DolphinDos25 baut byte-identisch zum Original (Tag `referenz-2026-10-27`).
Einschaltmeldung: `73, DOLPHINDOS26 1541`.

Die Firmware liegt in der letzten 64-KB-Bank des EPROMs (Bank 8, `8@RNROM`,
EPROM-Offset `$70000`). Im Abbild entspricht der Offset der CPU-Adresse.
Die Bänke sind hier wie bei `@RNROM` ab 1 gezählt (Bank 1 = CBM-DOS bei `$00000`,
Bank 8 = DolphinDos26 bei `$70000`); `tools/rom.py` und seine Ausgabe zählen
intern ab 0 und nennen dieselbe Bank deshalb „Bank 7“.

## Bauen

    make            # baut build/dd26.bin und vergleicht mit ref/1541DolphinDos25.bin
    make B=tmp/x    # in ein anderes Build-Verzeichnis

    make rom        # zusätzlich das 512-KB-EPROM-Abbild für den Multi-Speeder
    make builds     # beides bauen und nach ../Builds kopieren

`make rom` nimmt das Referenz-EPROM
`ref/AM27C040-…+7DolphinDos25_v3.3.bin` (MD5
`86ca5649c56219aeeff1dc6b7768eb35`), übernimmt die Bänke 1–7 unverändert und
ersetzt Bank 8 (`$70000`) durch den Build. Ergebnis:
`build/AM27C040-…+7DolphinDos26_v3.3.bin`.

`make builds` legt die fertigen ROMs im Projektverzeichnis `../Builds` ab:
`1541DolphinDos26.bin` (64 KB, Bank 8), das 512-KB-EPROM-Abbild,
`C1541_DOLPHINDOS26UL.bin` und `C1541_DOLPHINDOS26DD2.bin` (siehe unten). Vorhandene Dateien dort werden
überschrieben (`make builds BUILDS=…` für ein anderes Ziel).

## DolphinDos26DD2 (Multi-Speeder V3 mit SpeedDOS-Parallelkabel)

`make dd2` baut `build/dd26dd2.bin`, `make builds` legt es als
`C1541_DOLPHINDOS26DD2.bin` (64 KB) neben `C1541_DOLPHINDOS26UL.bin` ab. Es
ersetzt `1541DolphinDos26.bin` als Bank 8 des Multi-Speeder-EPROMs (`$70000`).

- Parallelkabel wie DolphinDos26UL (SpeedDOS-Art, Daten `$1801`, Handshake
  CB1/CA2; `-D DD26VIA`), also kompatibel mit Programmen für dieses Kabel.
- Alle Funktionen von `1541DolphinDos26.bin`: MS-Addon, `CDR`/`CDW`/`CDM`,
  MS-Addon-API; XQ/XZ aus der RAM-Disk laufen ebenfalls über das Kabel.
- Der PIA schaltet nur noch die RAM-Bänke (Port B). Jeder Reset (auch `UJ`)
  stellt Port A (`DDRA=0`) und CA2 (`CRA=4`) auf Eingang, die Leitungen dürfen
  also 1:1 parallel zum Kabel liegen.
- Einschaltmeldung `73, DOLPHINDOS26  DD2` (gleiche Länge wie `1541`).
- Kaltstart wie bei UL, Kennung `$A5 $5A` aber in `$60ED` (`$60F0` ist hier
  `ms_trks`). `UJ` behält Einstellungen und RAM-Disk.
- MS-NIBCOPY512 braucht mindestens Build 48. Ältere Builds finden den PIA und
  senden dort; sie melden am DD2-ROM `NO ANSWER FROM DRIVE CODE`.

Test: `tests/test_dd2.py`.

## DolphinDos26UL (C64 Ultimate / einfaches DolphinDOS 3)

    make ul         # baut build/dd26ul.bin (32 KB, $8000-$FFFF)

`C1541_DOLPHINDOS26UL.bin` ist die Firmware für das Diskettenlaufwerk im
Commodore C64 Ultimate (C64U): 8 KB Zusatz-RAM bei `$6000–$7FFF` und
**Parallelkabel am VIA1** (SpeedDOS-Art wie DolphinDOS 2.0, Daten `$1801`,
Handshake CB1/CA2), ohne 6821-PIA, ohne Multi-Speeder-RAM-Bänke und ohne
MS-Addon bei `$3000–$3FFF`. Der C64U bildet kein DolphinDOS-3-Kabel (PIA bei
`$5000`) nach, nur das VIA-Parallelkabel. Der C64U lädt ein 1541-ROM mit
genau 16 oder 32 KB nach `$8000–$FFFF`; dieses ROM hat 32 KB.

- DOS und DolphinDOS stammen aus denselben Quellen wie `1541DolphinDos26.bin`,
  übersetzt mit `-D DD26UL -D DD26VIA`: Einschaltmeldung `73, DOLPHINDOS26 C64U` und
  Parallelroutinen für das VIA1-Kabel (Kabelerkennung, Einzelbytes, XQ/XZ-
  Blocktransfer, Port-Rücksetzen in Reset und Idle-Schleife; übernommen aus
  `../DolphinDos2`). Ohne `DD26VIA` entsteht unverändert der PIA-Code; die
  C64-Seite (Kernal) ist für beide Kabel gleich. Statt des
  MS-Addons wird `addon/ul.s` ab `$8000` gelinkt (`dd26ul.cfg`): die
  Original-Abläufe für `setjob`, `format`, `job_write`, XQ/XZ sowie die
  schnellen Routinen aus `addon/fast.s` (GCR-Dekodierung, Pufferkopie).
- Nicht enthalten: `CDR`/`CDW`/`CDM` (→ `31 SYNTAX ERROR`), RAM-Disk,
  MS-Addon-API (MS-Tools laufen damit nicht).
- Kaltstart: Fehlt die Kennung `$A5 $5A` in `$60F0`, werden `$6000–$60FF`
  gelöscht (alle Schalter an, Spuranzahl automatisch) und 35 Spuren gesetzt.
  Beim C64U ist das Laufwerks-RAM nach dem Einschalten nicht gelöscht (z. B.
  `$12` in `$6003` würde den Parallelbetrieb abschalten). Ein Laufwerks-Reset
  (`UJ`) behält die Einstellungen.
- Test in VICE (ohne Multi-Speeder, Standard-Parallelkabel): `-dos1541
  build/dd26ul.bin -drive8ram6000 -parallel8 1`, automatisch:
  `tests/test_ul.py` (`MS_PORT` = anderer Monitor-Port bei parallelen
  VICE-Läufen).

Benötigt cc65 (ca65/ld65) und Python 3 (nur für den Vergleich).

## Aufbau

| Datei | Bereich | Inhalt |
|---|---|---|
| `addon/addon.s` | `$3000–$3BFF` | MS-Addon: `CDR`/`CDW` (Diskette ↔ 512-KB-RAM), RAM-Disk `CDM`, XQ/XZ aus dem RAM |
| `addon/addon.s` | `$3FC0–$3FFF` | MS-Addon-API: Sprungtabelle von `$3FFF` abwärts (siehe unten) |
| `dolphin/dolphin_a.s` | `$A000–$AFFF` | DolphinDOS: Sprungleiste, Track-Cache, Jobs, Parallel-Transfer, X-Befehle |
| `dolphin/dolphin_b.s` | `$B000–$BFFF` | GCR-Tabellen (per Makro erzeugt), Lock/Unlock-Meldungen, stpout-Hook |
| `dos/*.s` | `$C000–$FFFF` | CBM-DOS 901229-05 (mist64/dos1541) mit den DD25-Patches, markiert mit `; DD25:` |
| `dos/dd25ext.s` | – | Konstanten für Einsprünge nach DolphinDOS/Addon, PIA, DD-Variablen `$6000+` |
| `include/dos05.inc` | – | DOS-Symbole für die separaten Übersetzungseinheiten |
| `dd25.cfg` | – | Linker-Konfiguration (64-KB-Bank) |
| `tools/vergleich.py` | – | byteweiser Vergleich mit der Referenz |
| `tools/rom.py` | – | setzt eine Bank in das 512-KB-Referenz-EPROM ein |
| `addon/fast.s` | – | schnelle GCR-Dekodierung/Pufferkopie (von `addon.s` und `ul.s` eingebunden) |
| `addon/ul.s` | `$8000–$82FF` | nur DolphinDos26UL: Ersatz für das MS-Addon, Kaltstart-Vorbelegung |
| `dd26ul.cfg` | – | Linker-Konfiguration DolphinDos26UL (32 KB) |

Die originalen englischen Commodore-Kommentare bleiben erhalten. Alle
DD25-Änderungen und der neue Code sind deutsch kommentiert. Unsichere
Deutungen sind mit „(vermutlich)“ markiert.

## Hinweise

- DolphinDOS nutzt illegale NMOS-6502-Opcodes (`.setcpu "6502X"`).
- RAM-Bänke: Die Banknummer wird bei CRB-Bit 2 = 0 in DDRB (`$5002`)
  geschrieben. Wegen der Pull-ups an PB0–5 gilt: logische Bank n = physische
  Bank 63−n. Logische Bank 0 ist das Arbeits-RAM von DolphinDOS.
- Es gibt keine ROM-Prüfsummen mehr: DD25 wertet sie beim Reset nicht aus.

## MS-Addon-API (für C64-Programme)

Feste Einsprünge am Ende des Addon-Bereichs, von `$3FFF` abwärts. Die
Adressen bleiben gleich, auch wenn sich der Code des Addons ändert; neue
Einsprünge kommen unten dazu (E7 = `$3FE4` …). Eine spätere
Fassung (z. B. für die 1571) stellt dieselbe Tabelle bereit.

| Adresse | Inhalt |
|---|---|
| `$3FFF` | API-Version (1) |
| `$3FFE` | Anzahl der Einsprünge (7) |
| `$3FFC` | Kennung `"MS"` |
| `$3FF9` | E0 `OPEN` (Seite 1/2, Richtung 0 = lesen / 1 = schreiben, Verify 0 = aus / 1 = an / 2 = XV wie eingestellt). Schreiben einer 40-Spur-Seite: Ziel wird wie bei `CDW` geprüft (`66`, `21`, `29`) |
| `$3FF6` | E1 `TRACK` (Spur 1–40): eine Spur lesen bzw. schreiben, RAM-Lage wie `CDR1`/`CDR2` |
| `$3FF3` | E2 `CLOSE` (Spuranzahl 35/40, beim Lesen für `CDW` und `INFO` gemerkt; beim Schreiben wird die letzte Spur zurückgeschrieben) |
| `$3FF0` | E3 `PROBE` (Spur): Suchjob, `00` = Header mit der ID der Diskette gefunden, andere ID: `29` |
| `$3FED` | E4 `INFO`: Meldung `00, OK,t1,t2` = Spuranzahl von Seite 1 und 2 |
| `$3FEA` | E5 `ABORT`: nach einem Fehler aufräumen (Cache verwerfen, XR/XV/Write-back wie vor `OPEN`) |
| `$3FE7` | E6 `SECTOR` (Seite 1/2, Spur, Sektor): Sektor aus dem RAM in den DOS-Puffer `$0300` kopieren, danach per `M-R` lesen (z. B. BAM 18/0 für Diskname und ID) |

Aufruf: `"M-E" <lo> <hi> <p1> <p2> <p3>` an Kanal 15, die Parameter stehen
ab `cmdbuf+5`. Das Ergebnis steht wie bei jedem Befehl im Fehlerkanal
(`00, OK,00,00` oder z. B. `23,READ ERROR,17,05`). Programme prüfen vorher
Kennung und Version per `M-R` ab `$3FFC`. Beispiel: MS-FASTCOPY512.
