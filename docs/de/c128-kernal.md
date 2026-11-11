# C128DD26 – C128-Kernal für DolphinDos26

Rekonstruierter, deutsch kommentierter ca65-Quelltext des Dolphin-DOS-Kernals
für den C128 (`Referenzen/kernal-dolphin128.rom`, 16 KB, $C000–$FFFF:
Bildschirmeditor, Z80-Teil und Kernal). Er ist die Grundlage für die Anpassung
an DolphinDos26, wie beim C64 (`../C64DD26`).

## Bauen

```
make            # build/c128dd26.bin (US) + byteweiser Vergleich mit ref/, build/c128dd26-de.bin (DE)
make de         # nur die DE-Fassung (ca65 -D DIN), prüft den DIN-Treiber gegen 315078-03
make B=tmp/x    # anderes Build-Verzeichnis
make builds     # beide nach ../Builds: C128DolphinDos26-US.BIN und C128DolphinDos26-DE.BIN (mit MD5),
                # dazu C128DCR_KERNAL_29F040-DE.BIN und -US.BIN für den Kernal-Switcher (tools/u32_image.py)
make generiere  # src/ neu erzeugen (überschreibt src/!)
```

Benötigt `ca65`/`ld65` (cc65). Der Tag `c128dd26-2026-11-10` ist byte-identisch zum Original
(MD5 `854901919a2446bccf68e8392325c021`). Seit `cbm-fixes` vergleicht `make`
mit `ref/kernal-dolphin128-05.bin` (Original + Commodore-Korrekturen).

## DE- und US-Fassung

Aus demselben Quelltext entstehen zwei Kernals:

| Datei | Markt | Tastatur |
|---|---|---|
| `C128DolphinDos26-US.BIN` | international, USA | US-Editor 318020-05; CAPS LOCK wie gewohnt |
| `C128DolphinDos26-DE.BIN` | deutschsprachiger Raum | zusätzlich der deutsche Tastaturtreiber aus 315078-03: die CAPS-LOCK-Taste ist die **ASCII/DIN-Taste** (eingerastet = DIN mit ä ö ü ß, vertauschtem Y/Z und Tottasten, oben = ASCII), beim Umschalten wird der Zeichensatz ins 80-Zeichen-RAM geladen |

Der Treiber (`src/c128dd/din_treiber.s`, 524 Byte) stammt aus `EDITOR_C128_DIN/german.src`. Beim Original liegt er bei $FC80, dort stehen in DolphinDos26 die JiffyDOS-Routinen. In der DE-Fassung liegt er deshalb in der Lücke hinter dem Wedge ($E7C5–$E9D0, Tabellen auf Seite $E8). Eingehängt ist er wie beim deutschen Editor an fünf Stellen (`.ifdef DIN`): Sprungtabelle `scnkey` ($C012), CINT (`nat_init`, Tabellen-Init über `ascii_din`/`nat_scnkey`), Tastenabfrage in der Editorschleife und `keychk` in ed3 (`nat_keychk`). `tools/din_vergleich.py` assembliert den Treiber testweise bei $FC80 und vergleicht ihn byteweise mit 315078-03 (0 Abweichungen). Ohne `DIN` ist das ROM byte-gleich mit der bisherigen Fassung (MD5 `859493314e98777a595d0f2a039e6800`).

Für die richtige Darstellung von ä ö ü ß braucht der deutsche C128 sein deutsches Zeichensatz-ROM (315079-01); mit dem US-Zeichensatz erscheinen an diesen Stellen die US-Zeichen. In VICE liegt die ASCII/DIN-Taste auf F12.

`make builds` baut mit `tools/u32_image.py` auch die beiden 512-KB-Abbilder für den Kernal-Switcher (U32) des C128DCR, passend zu den Bänken von `C1571_C128DCR_29F040.BIN`. Je Bank wird nur die obere Hälfte genutzt ($x8000 C64-BASIC, $xA000 C64-Kernal, $xC000 C128-Kernal):

| Bank | Laufwerk | `C128DCR_KERNAL_29F040-DE.BIN` | `C128DCR_KERNAL_29F040-US.BIN` |
|---|---|---|---|
| 1, 2, 5–8 | CBM-DOS 1571 | 901226-01, 901227-03, 315078-03 (deutsch) | 901226-01, 901227-03, 318020-05 |
| 3 | DolphinDOS 3 | 901226-01, DolphinDOS-3.0-C64-Kernal, Dolphin-C128-Kernal | gleich |
| 4 | DolphinDos26 | `C64IIDolphinDos26.bin`, `C128DolphinDos26-DE.BIN` | `C64IIDolphinDos26.bin`, `C128DolphinDos26-US.BIN` |

Die Quell-ROMs liegen in `ref/orig` (der DolphinDOS-3.0-C64-Kernal stammt aus Bank 3 der früheren Veröffentlichung). Der originale Dolphin-C128-Kernal hat einen US-Editor; eine deutsche Fassung davon gibt es nicht.

## Wie der Quelltext entsteht

`tools/rekon.py` (aus `../JiffyDOS` übernommen) legt die Commodore-Quellen aus
`../Referenzen/cbmsrc` auf das Basis-ROM. Unveränderte Zeilen bekommen die
Originalnamen und die übersetzten Originalkommentare (`uebersetzung/*.tsv`).
Die Dolphin-Änderungen werden neu disassembliert und mit `DD:` markiert. Namen
und Kommentare für den Dolphin-Code stehen in `steuer/c128dd.txt`.

Benutzte Quellen: `EDITOR_C128`, `KERNAL_C128_05`, `EDITOR_C128_DIN` (nur für
den deutschen Tastaturtreiber).

Seit dem JiffyDOS-Einbau (Branch `jiffy`) ist `src/` maßgeblich und wird von
Hand gepflegt. `make generiere` würde die DD26-Änderungen überschreiben und
dient nur noch zum Nachvollziehen der Rekonstruktion (Tags
`c128dd26-2026-11-10`, `c128dd26-cbm-fixes-2026-11-10`).

## Aufbau des Dolphin-ROMs

**Basis:** US-Kernal 318020-05 (Editor $C000–$DFFF unverändert). Darin liegt bei
$FC80–$FE7F der deutsche Tastaturtreiber mit den DIN-Tabellen aus dem Kernal
315078-03 (`german.src`). `tools/mische_basis.py` baut daraus die Basis
`ref/orig/kernal-318020-05+din.bin`. Die Einsprünge in den Treiber
(im DIN-Editor bei $C013, $C090, $C106 usw.) sind **nicht** vorhanden. Der
Treiber ist also toter Code.

**Commodore-Korrekturen:** Dolphin hatte alle Korrekturen von 318020-04/-05
entfernt (Funktion wie 318020-03). Seit dem Branch `cbm-fixes` setzt
`tools/cbm_fixes.py` sie wieder ein und erzeugt `ref/kernal-dolphin128-05.bin`,
aus dem der Quelltext entsteht. Nummern nach den Release Notes 318020-05:

| Nr. | Korrektur | Stelle |
|---|---|---|
| 22 | CAPS LOCK liefert großes Q ($D1 statt $51) | $FC22 |
| 24 | IOINIT belegt die RS-232-Register vor (`ioinit_pat`); entfallen mit RS-232 | ($E159 wieder `sta speed`) |
| 25 | VDC-PAL R0 = $7F (`vdc_patch`), R4 = $26 | $E191, $E337, $FC67 |
| 26 | INPUT# vom Bildschirm (`basin_patch`) | $EF19, $FC40 |
| 27 | OPEN RS-232 ohne falschen Fehler; entfallen mit RS-232 | (frei) |
| 28 | BOOT "datei": Startadresse nach SAL/SAH (`load_patch`) | $FC4A, Aufruf aus `dd_load` ($EC18) |
| 29 | DMA in alle RAM-Bänke (`dma_patch`, liegt schon bei $CF80) | $FF50 |
| 37 | Kernal-Version $01 | $FF80 |

Bei Nr. 28 ruft `dd_load` `load_patch` statt `loding` auf, weil Dolphin den
Commodore-Aufruf bei $F2CC für `dd_load` belegt. Die Editor-Korrekturen
(Nr. 23, 30–36) waren im Dolphin-ROM schon vorhanden.

Geprüft (Multi-Speeder mit DolphinDos26, Parallelkabel): LOAD, VERIFY, BSAVE
und VERIFY wie beim Original; `BOOT"datei"` startet das Programm jetzt richtig
(das Original springt mit falscher Adresse und landet im Reset); $FF80 = $01.
Nr. 24 und 27 sind mit dem Entfernen von RS-232 (siehe unten) wieder entfallen.

**Dolphin-Code** (Platz des Kassettenteils):

| Bereich | Datei | Inhalt |
|---|---|---|
| $EA1C–$EA48 | `ea1c_dd_name.s` | Ersatzname `":*"`, PETSCII→ASCII-Tabellen |
| $EAA1–$EC17 | `eaa1_dd_bus.s` | Sekundäradresse + Kabelerkennung, Byte senden/empfangen parallel, Centronics |
| $EC18–$ED4F | `ec18_dd_lade.s` | Parallel-LOAD/VERIFY ("XQ"), Hilfsroutinen |
| $ED60–$EE50 | `ed51_dd_save.s` | Warteschleifen, Adressausgabe, Parallel-SAVE ("XZ") |

Merker `dd_flags` = $DD0C (SDR der CIA 2; der C128 braucht die SDR der CIA 1
für den schnellen seriellen Bus): b7 Parallelkabel aktiv, b6 Centronics aktiv,
b1 Drucker erkannt, b0 ASCII-Wandlung (Sekundäradresse 7). Bei 2 MHz
(`$D030` b0) sind die Wartezeiten doppelt so lang.

Weitere Eingriffe: LOAD/VERIFY ohne Namen lädt `":*"` bzw. vergleicht `"*"`.
LOAD/SAVE auf Gerät 1 gehen an Floppy 8, OPEN auf Gerät 1 gibt ILLEGAL DEVICE.
Die Meldung „PRESS RECORD & PLAY ON TAPE“ ist gekürzt, um Platz für „ $“/„-$“
zu schaffen (Anzeige `LOADING  $bAAAA-$bAAAA`, b = Bank). Die Wartezeit in
`isoura` ist verkürzt ($64 statt 184). In der Tastaturtabelle steht bei $FC22
$51 statt $D1.

## DD26: JiffyDOS

Für jede Übertragung gilt diese Reihenfolge:
1. **DolphinDos26 parallel** (Kabel nach der Sekundäradresse erkannt), wie bisher.
2. Unter ATN (LISTEN, TALK, Sekundäradresse) seriell, dabei **JiffyDOS-Erkennung**
   in der Bitschleife von `isour`.
3. **Burst-Laufwerk** (1571, 1581): unverändert der Commodore-Schnellmodus.
4. **JiffyDOS-Gerät** (JiffyDOS-1541/1571, SD2IEC …): alle Bytes im
   JiffyDOS-Protokoll – LOAD, SAVE, SEQ-Dateien, Directory, Status.
5. Sonst normal seriell.

Beim LOAD schaltet ein JiffyDOS-Gerät zusätzlich auf das blockweise
Schnellladen um (TALK mit SA+1). Das passiert nicht bei Sekundäradresse 2
(`LOAD"x",8,2`), beim Directory (`$`) und bei Ladeadressen unter $0400. Geladen
wird über einen umgebauten STASH-RAM-Code in jede Bank (`BLOAD …,B1`, `BOOT`).
Während des Schnellladens ist der Bildschirm kurz aus (keine Badlines).

| Datei | Inhalt |
|---|---|
| `fc80_jiffy.s` ($FC80–$FEF3) | Erkennung, `jd_listen_init`, `jd_acptr`/`jd_getbyte`, `jd_ciout`/`jd_sendbyte`, `jd_fastload`, `jd_stash_init` (früher unbenutzter deutscher Tastaturtreiber) |
| `f265_load.s` ($F32F–$F382) | `jd_ladeadr_hi`, `jd_load_weiter`, `jd_stash_wieder` (früher unerreichbarer Rest von LOAD Kassette) |
| `e33b_serial.s` | Bitschleife mit Erkennung, `untlk` erst ATN dann CLK, `list1` mit `jd_listen_init` |
| `eaa1_dd_bus.s`, `ec18_dd_lade.s` | Weichen: `dd_ciout_seriell` → `jd_ciout`, `dd_acptr_seriell` → `jd_acptr`, `dd_load_seriell` → `jd_load_weiter` |

Zeiten im Emulator gemessen (x128, 8-KB-Datei, über ein Testskript; nur
untereinander vergleichbar):

| Laufwerk | LOAD | VERIFY | BSAVE |
|---|---|---|---|
| Multi-Speeder DolphinDos26 parallel | 14,2 s | 11,2 s | 24,5 s (wie ohne JiffyDOS) |
| JiffyDOS-1541 | 27,7 s | 24,5 s | 64,8 s |
| JiffyDOS-1541 mit Original-JiffyDOS-C128-Kernal | 29,3 s | 24,8 s | 65,3 s |
| Original-1571 (Burst) | 27,6 s | 23,0 s | 100,5 s (wie ohne JiffyDOS) |

Außerdem geprüft: Original-1541 seriell (wie ohne JiffyDOS), `BOOT"datei"` mit
Schnellladen, `BLOAD` in Bank 1.

### Herkunft der JiffyDOS-Routinen und Lizenz

Die JiffyDOS-Übertragungsroutinen sind **keine Neuentwicklung**. Sie stammen
befehlsgleich aus dem Kernal-ROM JiffyDOS C128 (`Referenzen/JiffyDOS_C128.bin`,
MD5 `cbbd1bbcb5e4fd8046b6030ab71fc021`; kommentierte Rekonstruktion in
`../JiffyDOS/src/c128`): Bitschleife, `jd_erkennung`, `jd_listen_init`,
`jd_getbyte`, `jd_sendbyte`, `jd_nibtab`, `jd_spritesaus`, `jd_fastload` mit
Byteschleife und STASH-Vorlage. Neu sind nur die Weichen und die Anschlüsse an
den Dolphin-Code. Die JiffyDOS-Firmware für das Laufwerk ist nicht enthalten.

Jim Brain von RETRO Innovations hat am 2. November 2026 die Veröffentlichung
des DolphinDos26-Kernals auf GitHub erlaubt und empfohlen, die Herkunft der
Routinen anzugeben. Ist der Übertragungscode gleich – das trifft hier zu –,
wäre nach seiner Einschätzung beim **Endnutzer** eine Lizenz erforderlich.
**Bitte prüfe als Nutzer selbst, ob du eine JiffyDOS-Lizenz erwerben solltest.**
<https://www.jiffydos.com>

## DD26: Einschaltbild und LOADING-Kennung

**Einschaltbild:** Das Einschaltbild des C128 druckt das BASIC-ROM. Der Kernal
hängt sich wie JiffyDOS in `phoenix` ein (BASIC ruft es beim Kaltstart direkt
nach seiner Meldung auf) und gibt darunter zwei Zeilen aus, zentriert für 40
und 80 Zeichen (`dd_einschalt`, `dd_einr`):

```
 COMMODORE BASIC V7.0 122365 BYTES FREE
   (C)1986 COMMODORE ELECTRONICS, LTD.
         (C)1977 MICROSOFT CORP.
           ALL RIGHTS RESERVED
       DOLPHINDOS26/JIFFY/SD2IEC
  MULTISPEEDER BY FRANKEGGEN@EMDEN.NET
               PAL SYSTEM
READY.
```

Die letzte Zeile lautet je nach System „PAL SYSTEM“ oder „NTSC SYSTEM“, wie beim
C64-Kernal. Eine eigene Erkennung ist dafür nicht nötig: `ioinit` misst schon im
Original-Kernal die Rasterzeile und legt das Ergebnis in `palnts` ($0A03) ab.

**LOADING/VERIFYING** zeigen die Übertragungsart (nur im Direktmodus), wie beim C64:

| Übertragung | Anzeige |
|---|---|
| DolphinDos26 parallel, blockweise | `LOADING DD: $bAAAA-$bAAAA` (b = Bank) |
| Parallelkabel byteweise (`,8,2`, `$`) | `LOADING DD:` |
| JiffyDOS-Schnellladen | `LOADING JF: $bAAAA-$bAAAA` |
| JiffyDOS-Protokoll ohne Schnellladen (`,8,2`, `$`) | `LOADING JF:` |
| normal seriell / Burst | `LOADING` |

Texte statt der Kassettenmeldungen in `f6b0_messages.s` (Offsets aller anderen
Meldungen unverändert; die Datei ist von Hand neu geschrieben, die generierte
Fassung hatte `spmsg`/`msg`/`setnam`/`setlfs`/`setbnk` als Daten ausgegeben).
Auswahl in `dd_mode_msg`, Adressen beim Schnellladen über `jd_adr_aus`.

**OPEN auf Gerät 1:** Dolphin meldet dort ILLEGAL DEVICE, ließ den Eintrag aber
in der Dateitabelle stehen; ein folgendes `PRINT#1` lief in den Kassettencode.
`opn_illegal` entfernt den Eintrag jetzt wieder (`?FILE NOT OPEN`).

Geprüft: Einschaltbild in 40 und 80 Zeichen, PAL und NTSC, alle Kennungen mit
Multi-Speeder parallel, JiffyDOS-1541 und Original-1541, `OPEN1,1`/`PRINT#1`.

## DD26: @-Wedge (DOS-Befehle)

Im Direktmodus, wie bei DolphinDOS 3 und dem C64-Kernal DolphinDos26:

| Eingabe | Wirkung |
|---|---|
| `@` | Fehlerkanal des Standardgeräts lesen und ausgeben |
| `@befehl` | Befehl über Kanal 15 senden, danach den Status (z. B. `@I`, `@S:DATEI`, `@CD←`, `@CD:ORDNER`, `@N:NAME,ID`) |
| `@$`, `@$:MUSTER` | Directory anzeigen, ohne das BASIC-Programm zu überschreiben (STOP bricht ab) |
| `@8` … `@11` | Standardgerät wählen (nach dem Einschalten 8), gilt auch für `LOAD`/`SAVE` ohne Gerätenummer |
| `"befehl"…` | wie `@befehl` (für C=F5 auf einer Directory-Zeile) |

`dd_wedge_init` hängt sich beim BASIC-Kaltstart (aus `dd_einschalt`) in den
BASIC-Vektor `icrnch` ($0304); der alte Vektor bleibt in `dd_crnch` erhalten,
dadurch hängt der Wedge nicht von der BASIC-Version ab. Beginnt eine
eingegebene Zeile mit `@`, führt `dd_wedge` den Befehl aus und leert die Zeile.
Der Wedge blendet dazu wie BASIC (`put_io_in_map`) die I/O ein. Ohne Gerät
erscheint `?DEVICE NOT PRESENT ERROR`. Der STOP+RESTORE-Warmstart lässt den
Vektor stehen. RAM: `dd_defdev` $0A10, `dd_crnch` $0A11/$0A12 (frühere
RS-232-Register).

## DD26: F-Tasten wie beim C64-Kernal

Die F-Tasten sind belegt wie beim C64-Kernal DolphinDos26, damit man beim
Wechsel zwischen C64- und C128-Modus nicht umlernen muss. F2/F4/F6/F8 mit
SHIFT, die C=-Ebene hat eigene Texte (beim C128 liefern C= und SHIFT sonst
denselben Code).

| Taste | Text | | Taste | Text |
|---|---|---|---|---|
| F1 | CLR, `LIST` | | F2 | `RUN:` |
| F3 | CLR, `RUN` | | F4 | `VERIFY` (ohne Namen: `*`) |
| F5 | `LOAD` (ohne Namen: `:*`) | | F6 | `SAVE"@:` |
| F7 | CLR, `@$` (Directory) | | F8 | `@X` (X-Status der Floppy) |
| C=F1 | `OPEN4,4:CMD4:LIST` | | C=F3 | `@CD←` + RETURN (SD2IEC: zurück) |
| C=F5 | `  "CD:` + RETURN (auf einer Directory-Zeile: hinein) | | C=F7 | ` LOAD` + 3×TAB + `:` (auf einer Directory-Zeile: laden, RETURN selbst) |

SHIFT+RUN/STOP und HELP behalten die C128-Belegung. F1–F8 stehen in
`pkytbl` ($CEA8) und lassen sich mit `KEY` umbelegen; die C=-Texte stehen fest
im ROM (`dd_cfk_texte`, Editor-Patchbereich $CF19). `dopfky_patch` erkennt C=
(`shflag` Bit 1) bei F1/F3/F5/F7 und setzt den Merker `dd_fk_flag` ($0A13);
`lp2` holt die Zeichen über `dd_fk_zeichen` aus `pkybuf` oder aus dem ROM.

C=F5 ergibt auf einer Directory-Zeile `  "CD:NAME"  DIR`; der @-Wedge führt
Zeilen, die mit einem Anführungszeichen beginnen, als Floppy-Befehl aus (Text
zwischen dem ersten und dem letzten Anführungszeichen, innere fallen weg).
Dadurch passen C=F5 und C=F7 auch bei 5-stelligen Blockzahlen, ohne die
Sonderprüfung des C64-Kernals. `LOAD`/`SAVE` ohne Gerätenummer benutzen das mit
`@n` gewählte Gerät (sonst 8); `LOAD"name"` lädt wie beim C128 üblich an den
BASIC-Anfang (SA 0).

Geprüft: F1, SHIFT+F3, F7, F8 (X-Status vom DolphinDos26-Laufwerk), C=F1, C=F3,
C=F5 und C=F7 auf einer Directory-Zeile (lädt die Datei), `KEY`-Anzeige.
Hinweis für den Emulator VICE: Dort liegt C= auf der Tab-Taste des PCs.

## DD26: Kassette und RS-232 entfernt

Für den Wedge sind der restliche Kassettencode und die RS-232-Routinen
(User-Port) entfernt; alle übrigen Routinen stehen weiter an ihren Adressen.
OPEN auf Gerät 1 oder 2 meldet ILLEGAL DEVICE, CHKIN/CHKOUT/BASIN/BSOUT/GETIN
für diese Geräte ebenso, CLOSE entfernt nur den Tabelleneintrag. LOAD und SAVE
auf Gerät 1 (ohne Gerätenummer) gehen an das mit `@n` gewählte Gerät (sonst 8).
`cmpste`/`incsal` (SAVE) und
die Kassettentasten-Abfrage im IRQ bleiben. Programme mit eigenem RS-232-Treiber
sind davon nicht betroffen; `OPEN …,2` über den Kernal gibt es nicht mehr.

## Freier Platz für DD26

Rund 1170 Byte (Füllung $FF, die DD26-Lücken sind mit `frei_…` markiert):
$E7C5–$EA1B (599, hinter dem Wedge; in der DE-Fassung belegt der DIN-Treiber davon 524, frei bleiben $E9D1–$EA1B), $EE51–$EEB6 (102), $F06B–$F0CA (96),
$EA4B–$EAA0 (86), $EF27–$EF5B (53), $F1A1–$F1CE (46), $CF9E–$CFBF (34, Editor),
$EF8E–$EFAA (29), $CEEA–$CEFF (22, hinter der F-Tastentabelle),
$EF67–$EF78 (18), $FC55–$FC66 (18) sowie kleinere Reste von 7 bis 12 Byte.
