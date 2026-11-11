# C1571DD26 – C1571DolphinDos26 für die 1571 (C128DCR, 1571 Multi-Speeder V3)

**C1571DolphinDos26** (`C1571_DOLPHINDOS26.bin`, 64 KB) ist DolphinDos26 für
die interne 1571 des C128DCR (1571CR) mit dem 1571 Multi-Speeder V3 (512 KB
RAM, 8 × 64 KB EPROM, PIA 6821). Es ersetzt **Bank 4** des EPROMs (EPROM-Offset
`$30000`, Umschalten mit `4@RNROM`), in der bisher DolphinDos25 1571 lag.

Grundlage ist DolphinDOS 3 für die 1571 (Bank 3 des EPROMs), dazu das MS-Addon
von DolphinDos26 (1541) mit denselben Befehlen und derselben API, erweitert um
doppelseitige Disketten.

## Bänke des 1571-Multi-Speeder-EPROMs

`n@RNROM` (n = 1–8) wählt die EPROM-Bank n−1; danach startet das Laufwerk neu.

| Befehl | EPROM-Offset | Inhalt |
|---|---|---|
| `1@RNROM` | `$00000` | CBM DOS V3.1 1571CR (318047-01) |
| `2@RNROM` | `$10000` | CBM DOS V3.0 1571 |
| `3@RNROM` | `$20000` | DolphinDOS 3 1571 (Original) |
| `4@RNROM` | `$30000` | **C1571DolphinDos26** (bisher DolphinDos25 1571) |
| `5@RNROM` … `8@RNROM` | `$40000` … `$70000` | JiffyDOS 6.0 1571 |

Speicher des Laufwerks (Adressdecoder ATF16V8 „V3_0PIA_1571“, für alle Bänke
gleich, EPROM-Offset = CPU-Adresse):

| Bereich | Belegung |
|---|---|
| $0000–$1FFF | 1571 (RAM, VIA1 $1800, VIA2 $1C00) |
| $2000–$2FFF | 1571 (WD1770) |
| $3000–$3FFF | EPROM: MS-Addon, API ab $3FFF abwärts |
| $4000–$4FFF | 1571 (CIA bzw. MOS5710) |
| $5000–$5FFF | PIA 6821 (Parallelkabel, RAM-Bank über PB0–PB5) |
| $6000–$7FFF | 8-KB-Fenster ins 512-KB-SRAM |
| $8000–$FFFF | EPROM: DOS (DolphinDOS 3 1571 mit DD26-Änderungen) |

## Installation

1. `C1571_DOLPHINDOS26.bin` an Offset `$30000` des 512-KB-Abbilds des
   1571-Multi-Speeder-EPROMs legen (ersetzt Bank 4), einen 29F040 (alternativ
   27C040 oder SST39SF040) brennen und einsetzen.
2. Am C128 den Kernal **C128DolphinDos26** einsetzen (C128-Modus), für den
   C64-Modus **C64IIDolphinDos26**. Im 8-Bank-EPROM des Kernal-Switchers
   (U32) wird je 64-KB-Bank nur die obere Hälfte genutzt: der C64-Modus (BASIC +
   Kernal, 16 KB wie `C64IIDolphinDos26.bin`) bei `$8000`–`$BFFF` und der
   C128-Kernal (16 KB, `C128DolphinDos26-DE.BIN`) bei `$C000`–`$FFFF`;
   `$0000`–`$7FFF` bleibt frei. Das C128-BASIC liegt nicht in U32.
3. Mit `4@RNROM` umschalten. Das Laufwerk meldet `73,DOLPHINDOS26 1571`.

## Funktionen

| Befehl | Wirkung |
|---|---|
| `CDR1` / `CDR2` | Diskette (Spur 1–35, 40 automatisch) in RAM-Slot 1 bzw. 2 lesen |
| `CDR1+` / `CDR2+` | immer 40 Spuren lesen (nur 1541-Modus) |
| `CDW1` / `CDW2` | RAM-Slot auf Diskette schreiben |
| **`CDRD`** | **doppelseitige Diskette** lesen: Seite 0 → Slot 1, Seite 1 → Slot 2 |
| **`CDWD`** | beide Slots auf eine doppelseitige Diskette schreiben |
| `CDM1` / `CDM2` | RAM-Disk: Laufwerk 8 arbeitet aus Slot 1 bzw. 2 |
| **`CDMD`** | **doppelseitige RAM-Disk**: Laufwerk 8 arbeitet aus beiden Slots (Spur 1–70) |
| `CDM0` | RAM-Disk aus, wieder Diskette |

Wie bei der 1541: Spur 18 im Write-back während CDW, CDW ohne Vorlesen der
Zielspur, XQ/XZ (Schnellladen/-speichern) direkt aus/in die RAM-Disk, die
RAM-Disk übersteht einen Laufwerks-Reset.

Für CDRD/CDWD/CDMD stellt das Addon DolphinDOS in den 1571-Modus
(`$6005 = $12`: maxtrk 71, Spur 36–70 auf der Rückseite) und danach wieder
zurück – das geht auch, wenn der C128 im C64-Modus arbeitet.

### MS-Addon-API (unverändert kompatibel zu den MS-Tools)

Sprungtabelle ab $3FFF abwärts wie DolphinDos26 1541 (Version 1, 7 Einträge,
gleiche Adressen). Erweiterung ohne neue Einträge: **Seite 3 = doppelseitig**

- `E0 OPEN` Seite 3: Sitzung über beide Seiten, `E1 TRACK` dann Spur 1–70
  (36–70 → Slot 2), `E2 CLOSE` setzt beide Slots auf 35 Spuren
- `E6 SECTOR` Seite 3 mit Spur 1–70

Bisher war Seite 3 ungültig (31 SYNTAX ERROR), alte Programme sind nicht
betroffen. Die MS-Tools laufen am C128 im C64-Modus (`GO 64`).

## Takt: 2 MHz, 1 MHz und `X-`

Die 1571 kann mit 1 MHz (wie eine 1541) oder mit 2 MHz laufen (Bit 5 von
VIA1 Port A). Das Commodore-ROM nimmt im 1541-Modus 1 MHz und nur im
1571-Modus (C128, Burst) 2 MHz.

**C1571DolphinDos26 verhält sich wie das originale DolphinDOS 3 1571: Das
Laufwerk läuft immer mit 2 MHz**, auch wenn der C128 im C64-Modus arbeitet.
DolphinDOS braucht die 2 MHz für seinen Track-Cache, der die Sektoren schon
beim Lesen dekodiert. Das MS-Addon läuft ebenfalls mit 2 MHz. Die
Parallelübertragung arbeitet mit Handshake und hängt nicht vom Takt ab.

Folge für **Schnelllader, Kopierprogramme und anderen 1541-Floppycode**:
Programme, die eigenen Code ins Laufwerk laden (`M-E`, `B-E`, `U3`–`U8`, `&`)
und dort auf genaues Timing angewiesen sind, laufen bei 2 MHz doppelt so
schnell und können dann versagen. Dafür gibt es zwei Wege:

| Weg | Wirkung |
|---|---|
| **`@X-`** (bzw. `OPEN1,8,15,"X-":CLOSE1`) | Laufwerk auf **1 MHz**, DolphinDOS aus (kein Track-Cache, keine Parallel- und Schnellladefunktionen, `X`-Status `R-:…:P-`); es verhält sich wie eine 1571 mit Commodore-ROM im 1541-Modus. Der Zustand steht im Laufwerks-RAM und übersteht einen Laufwerks-Reset. |
| **`@X+`** | wieder **2 MHz** und DolphinDOS mit allen Funktionen |
| **`1@RNROM`** | Commodore-ROM 1571CR (1 MHz im 1541-Modus) für Programme, die ein unverändertes Laufwerk erwarten; zurück mit `4@RNROM` |

Empfehlung: Für Spiele und Programme mit eigenem Schnelllader vor dem Laden
`@X-` eingeben; für Kopierschutz-Software, die das Original-ROM prüft,
`1@RNROM`.

## PAL und NTSC

Die Firmware hängt nicht von der Videonorm des Rechners ab (das Laufwerk hat
seinen eigenen Takt). Die Kernals C128DolphinDos26 und C64DolphinDos26 erkennen
PAL und NTSC selbst. Parallelübertragung und JiffyDOS laufen in beiden Normen,
im C128- und im C64-Modus.

## Eingriffe in DolphinDOS 3 1571 (`make vergleich` listet alle Bytes)

| Adresse | Original | DD26 |
|---|---|---|
| $C8C1 | duplct: 31 SYNTAX | `jmp ms_addon` (wie DD25-1571) |
| $C8D5 | format: `jsr jformat` | `jsr ms_format` (RAM-Disk: Slots löschen) |
| $D580 | sjb1: `sta jobs,x / sta lstjob,x / rts` | `jmp ms_setjob` (RAM-Disk) |
| $BA20 | job_write: Write-through Spur 18/53 | `jsr ms_wtchk` (Write-back bei CDW) |
| $F815 | xcmd_q-Rückfallweg | `jmp ms_xq` (RAM-Disk-Blocktransfer) |
| $FC97 | xcmd_z: `jsr z_prepare` | `jmp ms_xz` |
| $AADD | ptch64 (Suchjob Spur 53 ohne setjob) | `jmp ms_ptch64` (doppelseitige RAM-Disk) |
| $C000 | cchksm $84 | Abgleichbyte der ROM-Prüfsumme, berechnet von `tools/pruefsumme.py` (die Prüfung bei $EAE5, `bne perr2`, ist wieder eingeschaltet) |
| $E5C1 | „.3“ | „26“ → `73,DOLPHINDOS26 1571` |

Unterschiede zur 1541, die das Addon berücksichtigt: binärer Track-Cache
(Sektorstatus $10 = geändert, $00 = gültig), Modusflag $6005 statt pota1
(daher `ms_save_r` jetzt $60E9), im 1541-Modus fährt DD3-1571 den Kopf nicht
hinter `dd_maxtrk-1` (Probe auf Spur 36 meldet deshalb selbst 21).

## Leistung

Echtzeit, 35-Spur-Diskette bzw. 30-KB-Datei:

| | DolphinDos25 1571 | C1571DolphinDos26 |
|---|---|---|
| CDR1 | 20,8 s | 16,0 s |
| CDW1 | 42,6 s | 23,3 s |
| CDRD / CDWD (doppelseitig) | – | 40 s / 59 s |
| LOAD parallel (C128- / C64-Modus) | 6,2 s | 6,3 s / 5,3 s |
| LOAD aus der RAM-Disk | – | 3,8 s |

## Bauen

    make            # Bank bauen + Abweichungen zu DD3-1571 auflisten
    make bank       # build/dd26_1571.bin (64 KB)
    make rom        # build/C1571_AM27C040_DD26.bin (512 KB, Bank 4 ersetzt)
    make builds     # Bank als ../Builds/C1571_DOLPHINDOS26.bin (mit MD5)

Die Rekonstruktion selbst ist mit Tag `referenz-2026-11-10` byte-identisch
(`src/` darf seitdem nicht mehr mit `make generiere` überschrieben werden).

## Tests (gepatchter VICE mit 1571-Multi-Speeder, GUI)

    tests/t1571.py  <eprom> 3     # C128-Modus: LOAD, CDR1/CDW1, RAM-Disk, BSAVE
    tests/t_d71.py  <eprom> 3     # CDRD/CDWD, CDMD, API Seite 3 (NOAPI=1 kürzer)
    tests/t_c64.py  <eprom> 3     # C64-Modus (x128 -go64) mit C64DolphinDos26
    tests/t_api.py  <eprom> 3     # API einzeln (GO64=1 für den C64-Modus)
    tests/ms_tools_1571.py build/dd26_1571.bin test_fastcopy.py on
                                  # MS-Tools-Tests unverändert, x128 -go64 + 1571CR

Die Bankangabe `3` der Testskripte ist die VICE-Zählung ab 0 (= `4@RNROM`).
x128 übernimmt `-kernal64` nicht (setzt es beim Laden des C128-Kernals
zurück); die Tests legen deshalb ein eigenes Systemverzeichnis an
(`-directory`), in dem der Standardname auf `C64DolphinDos26.bin` zeigt.
