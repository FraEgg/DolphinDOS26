# C64DD26 – C64-Kernal für DolphinDos26

Rekonstruierter, deutsch kommentierter ca65-Quelltext des C64-Kernals
`Referenzen/1-C64_Dolphin_DOS_Silver.rom` (Dolphin DOS „Silver“, $E000–$FFFF).
Er ist die Grundlage für die Weiterentwicklung des C64-Kernals zu DolphinDos26
(Gegenstück zur Floppy-Firmware in `../dd25`). Er enthält Routinen aus einem
JiffyDOS-Kernal, siehe
[Herkunft der JiffyDOS-Routinen und Lizenz](#herkunft-der-jiffydos-routinen-und-lizenz).

## Bauen

```
make            # build/c64dd26.bin + byteweiser Vergleich mit ref/
make B=tmp/x    # anderes Build-Verzeichnis
make builds     # zusaetzlich nach ../Builds kopieren: C64DolphinDos26.bin und C64IIDolphinDos26.bin (mit MD5)
```

Benötigt `ca65`/`ld65` (cc65). `make` vergleicht das Ergebnis mit
`ref/1-C64_Dolphin_DOS_Silver.rom` und listet die abweichenden Adressen auf.
Der Tag `c64dd26-2026-10-30` ist noch byte-identisch zum Original
(MD5 `ab781ee4d19eb2e096b298317b2d0811`).

## DD26-Änderungen

### JiffyDOS (volles Protokoll, LOAD und SAVE)

Für jede Übertragung gilt diese Reihenfolge:
1. **DolphinDos26 parallel** (Kabel nach der Sekundäradresse erkannt), wie bisher.
2. **JiffyDOS**, wenn sich das Gerät beim TALK/LISTEN als JiffyDOS-Gerät meldet
   (JiffyDOS-1541, SD2IEC …). Dann laufen alle Bytes im Jiffy-Protokoll:
   LOAD, SAVE, SEQ-Dateien, Directory, Status.
3. **Sonst** normal seriell.

Beim LOAD schaltet ein Jiffy-Gerät zusätzlich auf das blockweise
Schnellladen um (TALK mit SA+1). Das passiert nicht bei Sekundäradresse 2
(`LOAD"x",8,2`), Directory (`$`), Ladeadressen unter $0400 und bei
Dolphin-Parallelbetrieb. Bei `,8,2` laufen die Bytes trotzdem im
Jiffy-Protokoll.

Die Routinen stammen befehlsgleich aus dem JiffyDOS-sd2iec-Kernal
(`../C64JiffySD2IEC`). `tools/vergleich_jiffy.py` prüft das, dazu die
Seitengrenzen in den zeitkritischen Abschnitten.

| Routine | Adresse | Zweck |
|---|---|---|
| Bitschleife | $ED62 | serielles Senden mit Aufruf von `jd_detect` |
| `jd_detect` | $F1DF | Jiffy-Gerät beim ATN-Befehlsbyte erkennen (r2d2 Bit 6) |
| `jd_acptr`, `jd_getbyte` | $F409 | Byte im Jiffy-Protokoll empfangen (aus `dd_acptr`) |
| `jd_ciout`, `jd_sendbyte`, `jd_nibtab` | $F8AF | Byte senden (aus LIST1 $ED19 und CIOUT $EDE7) |
| `jd_list2` | $F26C | LIST2: Jiffy-Merker löschen |
| `jd_loadadr` (+`jd_loadadr2` $F0A7) | $E4E0 | auf Schnellladen umschalten |
| `jd_retalk` | $FF61 | UNTALK/TALK/TKSA |
| `jd_load_chk`, `jd_fastload` | $F816 | Auswahl, Vorspann des Schnellladers |
| `jd_block`, `jd_fl_byte` | $F9C3 | Schnelllader (zeitkritisch) |
| `jd_print_end` | $FEC2 | Endadresse ausgeben |

Für den Platz wurden tote Kassettenreste entfernt (FAH $F750, `cste1`/`cste2`
$F816, `tstop` $F8D0, `tnif`/`tnof` $FC93/$FCCA, `fpatch` $E4E0). Verschoben
wurden `dec_tab_lo` (jetzt $F72C) und `dd_second_hook` (jetzt $FC93).

Messung in VICE, 16000 Bytes:

| | JiffyDOS-1541 | Standard-1541 | DD26 parallel |
|---|---|---|---|
| LOAD | 6,7 s | 41,2 s | 2,1 s |
| LOAD `,8,2` | 15,8 s | – | – |
| SAVE | 19,1 s | 48,4 s | 4,6 s |

### Herkunft der JiffyDOS-Routinen und Lizenz

Die JiffyDOS-Übertragungsroutinen dieses Kernals sind **keine Neuentwicklung**.
Sie stammen aus dem Kernal-ROM „JiffyDOS, SD2IEC enhanced“
(`JiffyDOS-C64-sd2iec.rom`, MD5 `c9fe23f3273d9beef0bd4c39af86cce9`, Einschaltbild
„JIFFYDOS (C)1989 CMD“). Rund 540 Bytes sind befehlsgleich übernommen, nur
Adressen und Sprungweiten weichen ab; `tools/vergleich_jiffy.py` weist das nach:
Bitschleife, `jd_detect`, `jd_acptr`, `jd_getbyte`, `jd_sprites_off`, `jd_ciout_spr`, `jd_ciout_chk`,
`jd_sendbyte`, `jd_nibtab`, `jd_block`, `jd_fl_byte`, der Vorspann von
`jd_fastload` und `jd_retalk`. Die übrigen Anschlussroutinen (`jd_ciout`, `jd_list2`,
`jd_loadadr`, `jd_load_chk`, `jd_print_end`) sind danach aufgebaut. Die JiffyDOS-Firmware
für das Laufwerk ist hier **nicht** enthalten.

**Dank an Jim Brain von RETRO Innovations** für die Unterstützung bei der
JiffyDOS-Implementierung des C64/C128-Kernals DolphinDos26. RETRO Innovations
hält die JiffyDOS-Lizenzrechte; Jim Brain hat am 2. November 2026 auf Anfrage
die Veröffentlichung dieses Kernals auf GitHub erlaubt und empfohlen, die
Herkunft der Routinen anzugeben, damit jeder selbst entscheiden kann, ob er eine
Lizenz braucht. Nach seiner Beschreibung ist für Code, der dasselbe
Übertragungsverhalten umsetzt, aber keine genaue Kopie der JiffyDOS-Routinen ist,
keine Lizenz nötig. Ist der Übertragungscode gleich – das trifft hier zu –, wäre
nach seiner Einschätzung beim **Endnutzer** eine Lizenz erforderlich; das
Repository selbst ist davon nicht betroffen.

**Bitte prüfe als Nutzer selbst, ob du wegen der Nutzung eine offizielle
JiffyDOS-Lizenz erwerben solltest.** Weitere Informationen:
<https://www.jiffydos.com>

*English:* The JiffyDOS transfer routines in this kernal are not a new
implementation. About 540 bytes are instruction-identical copies from the kernal
ROM "JiffyDOS, SD2IEC enhanced" (boot screen "JIFFYDOS (C)1989 CMD"); only
addresses and branch distances differ (see `tools/vergleich_jiffy.py`). The
JiffyDOS drive firmware is not included. **Thanks to Jim Brain of RETRO
Innovations** for his support with the JiffyDOS implementation of the C64/C128
DolphinDos26 kernal. RETRO Innovations holds the JiffyDOS license rights; Jim Brain
confirmed on 2 November 2026 that publishing this kernal on GitHub is fine. As he
describes it, code that implements the same transfer behavior without being an
exact copy of the JiffyDOS routines needs no license. If the transfer code is the
same, as it is here, he believes the end user would need a license, while the
repository itself is not affected. **Please check for yourself whether your use
calls for an official JiffyDOS license.** More information:
<https://www.jiffydos.com>

Aus demselben ROM stammen als Vorlage auch die SD2IEC-F-Tasten, das Einschaltbild
und die PAL/NTSC-Erkennung (siehe unten).

### SD2IEC-F-Tasten

Nach dem JiffyDOS-sd2iec-Kernal (auf den früheren Monitor-Tasten):

| Taste | Text | Wirkung |
|---|---|---|
| C=F3 | `@CD←` + RETURN | SD2IEC: ein Verzeichnis bzw. Disk-Image zurück |
| C=F5 | ` "CD/:` + RETURN | auf einer Directory-Zeile: in dieses Verzeichnis/Image wechseln |
| C=F7 | `LOAD` + Tab + `,8,1` | auf einer Directory-Zeile: diese Datei laden (RETURN selbst drücken) |

Vor jedem F-Tasten-Text prüft `dd_fkey_init` ($F750), ob die Cursorzeile eine
Directory-Zeile mit Anführungszeichen in Spalte 6 ist (5-stellige
Blockzahlen, z. B. beim SD2IEC). Dann setzt es ein Leerzeichen davor, damit
C=F5 und C=F7 genau auf den Dateinamen passen.

### Monitor und Centronics entfernt

Neu sind ein farbiges Einschaltbild (Balken, „**** COMMODORE 64 ****“,
„DOLPHINDOS26/JIFFY/SD2IEC“, „PAL SYSTEM“ bzw. „NTSC SYSTEM“) und eine PAL/NTSC-Erkennung
über die Rasterzeile. Beides ist nach dem JiffyDOS-sd2iec-Kernal
(`../C64JiffySD2IEC`) aufgebaut: `dd_banner` $EFFE, `dd_palntsc` $F08E (aus
PCINT), `words` $E460, `dd_banner_sys` $FEA3 mit `txt_pal` $F0AF und
`txt_ntsc` $FE0A.

Zwischen dem Farbbalken und „PAL/NTSC SYSTEM“ steht mit je einer Leerzeile
Abstand der Hinweis „MULTISPEEDER BY FRANKEGGEN@EMDEN.NET“ (`txt_ms` $E47E,
direkt hinter `words`; im Großschrift-Zeichensatz in Großbuchstaben).

```
       ▌ 38911 BASIC BYTES FREE      (letzter Balken)
     ▌
                                      (Leerzeile)
MULTISPEEDER BY FRANKEGGEN@EMDEN.NET
                                      (Leerzeile)
PAL SYSTEM
```

Alle übrigen Routinen stehen weiter an ihrer Originaladresse. Die Lücken sind
mit `FREI:` und dem Label `frei_xxxx` markiert und mit `$AA` gefüllt.
`make && python3 -I tools/pruefe_frei.py` listet die freien Bereiche, prüft die Füllung und zeigt alle Abweichungen zum Original außerhalb der Lücken.

| Bereich | Bytes | vorher |
|---|---|---|
| $E4A5–$E4AB | 7 | Rest hinter txt_ms |
| $EA79–$EA7A | 2 | Rest hinter dd_mode_msg (Datasettenabfrage im IRQ) |
| $EFFC–$EFFD | 2 | STOP-Abfrage in dd_load/dd_save über den Kernal |
| $F0BB–$F0BC | 2 | Rest hinter txt_pal |
| $F0E0–$F0E2 | 3 | Rest der Kassettentexte (PLAY?/REC&PLAY?) |
| $F19F–$F1A4 | 6 | Rest hinter jd_loadadr2 |
| $F1AA–$F1AC | 3 | dd_rvsout_vec (Monitor) |
| $F206–$F20D | 8 | Rest hinter neuem Code |
| $F229–$F236 | 14 | Monitor (mon_cmds) |
| $F275–$F277 | 3 | Rest hinter neuem Code |
| $F2AA–$F2BD | 20 | Monitor (mon_rvsout) |
| $F484–$F494 | 17 | Rest hinter neuem Code |
| $F662–$F675 | 20 | Monitorbefehl G |
| $F731–$F735 | 5 | Rest hinter dec_tab_lo |
| $F765–$F769 | 5 | Rest hinter dd_fkey_init |
| $F88E–$F88F | 2 | Rest des alten Ausweichwegs |
| $FA6B–$FA6B | 1 | Rest hinter dd_ctrl_std |
| $FB91–$FBA0 | 16 | Kassettenreste udst/rd180, Monitor (mon_out_x, out_space) |
| $FCC1–$FCD0 | 16 | tote Kassettenroutinen tnif/tnof |
| $FE17–$FE17 | 1 | Rest hinter txt_ntsc (RS-232-Status in READST) |
| **gesamt** | **153** | |

Geändertes Verhalten:
- `SYS 0` und BRK gehen über den BRK-Vektor $0316, Standard ist der BASIC-Warmstart.
- CTRL + Reset/RESTORE hat keine Funktion mehr.
- Farben wie im Original-C64-ROM: Rahmen $0E, Hintergrund $06, Text $0E (Dolphin:
  $00, $00, $03), siehe [Personalisierung](#personalisierung). Auch die Texte des
  Einschaltbilds erscheinen in der Textfarbe: Neuer Steuercode $06 = Standard-Textfarbe
  (`dd_ctrl_std` $FA64, `dd_std_col` $F949) ersetzt im Bild die festen Cyan-Codes $9F.
- LISTN gibt CLK bei UNLISTEN wieder frei wie im Original.
- Parallel-LOAD/-SAVE (`dd_load`/`dd_save`) fragen die STOP-Taste nach jeder
  Seite mit `jsr stop` ab (abgebrochen wird nur bei `stkey` = $7F, wie beim
  seriellen Speichern). Das Original prüfte mit `bit stkey` nur Bit 7 und
  brach ab, sobald ein Programm mit eigenem IRQ `stkey` unter $80 ließ:
  Eye of the Beholder (EasyFlash) speicherte so nur eine leere 0/1-Block-Datei
  und lud nichts. Die zusätzliche Abfrage vor dem ersten Byte beim LOAD
  entfällt.
- Gerät 4 ist immer ein serieller Drucker, die Hardcopy (CTRL-*) geht dorthin.
- Der IRQ fragt die Datasettentaste nicht mehr ab und schaltet den
  Datasettenmotor nicht mehr (r6510 Bit 5 bleibt wie von IOINIT gesetzt).
  `key4` $EA61 springt direkt nach `kl2` $EA7B; $EA7E/$EA81 sind unverändert.
- READST ($FFB7 → `readss` $FE07) liefert immer den Status `status` ($90),
  auch bei Gerät 2 (kein RS-232-Status mehr). $FE07 bleibt Einsprung.
- `rd300` (aus SAVE) steht jetzt bei $FB88 statt $FB8E (davor tote
  Kassettenreste `jsr udst`/`rd180`).
- Verschoben wurden `dec_tab_hi` ($F187), `":*"` ($F227) und `dd_second_hook` (Code ab $F8DD).
- „LOADING“/„VERIFYING“ zeigen die Übertragungsart (nur im Direktmodus):

  | Übertragung | Anzeige |
  |---|---|
  | DolphinDos26 parallel, blockweise | `LOADING DD: $0801-$xxxx` |
  | Parallelkabel byteweise (`,8,2`, `$`) | `LOADING DD:` |
  | JiffyDOS-Schnellladen | `LOADING JF: $0801-$xxxx` |
  | JiffyDOS-Protokoll ohne Schnellladen (`,8,2`, `$`) | `LOADING JF:` |
  | normal seriell | `LOADING` |

  Texte `ms_jf`/`ms_dd`/`ms_dd_adr` ($F0D8–$F0E6, statt der Kassettentexte
  „PLAY?“/„REC&PLAY?“), Auswahl im Ausweichweg `dd_mode_msg` ($EA64).
Nebenprodukte: `build/kernal.lst` (Listing), `build/c64dd26.lbl` (Labels für den
VICE-Monitor), `build/c64dd26.map`.

## C64 II

Der C64 II (Kurzplatine) hat BASIC und Kernal in einem einzigen ROM-Baustein
(Original 251913). Dafür erzeugt `make builds` die Datei `C64IIDolphinDos26.bin`
(16 KB): bei Offset $0000 das unveränderte BASIC 901226-01, bei Offset $2000 der
Kernal. Für C64 mit getrennten BASIC- und Kernal-Bausteinen bleibt
`C64DolphinDos26.bin` die richtige Datei.

## Personalisierung

Die Farben stehen als einzelne Bytes im ROM und lassen sich ohne Assembler
ändern: Datei `C64DolphinDos26.bin` (8 KB, Adresse $E000 = Datei-Offset $0000)
kopieren, die Bytes mit einem Hex-Editor ändern und die Kopie als Kernal benutzen.
Der C64 prüft keine Prüfsumme des Kernals. Ab Werk gelten die Werte des
Original-C64-ROMs.

| Farbe | ROM-Adresse | Datei-Offset | Wert ab Werk |
|---|---|---|---|
| Rahmen | $ECD9 | $0CD9 | $0E (hellblau) |
| Hintergrund | $ECDA | $0CDA | $06 (blau) |
| Text (auch `READY.`, Cursor, CTRL-V) | $E535 | $0535 | $0E (hellblau) |

Farbwerte:

| Wert | Farbe | Wert | Farbe |
|---|---|---|---|
| $00 | schwarz | $08 | orange |
| $01 | weiß | $09 | braun |
| $02 | rot | $0A | hellrot |
| $03 | cyan | $0B | grau 1 |
| $04 | lila | $0C | grau 2 |
| $05 | grün | $0D | hellgrün |
| $06 | blau | $0E | hellblau |
| $07 | gelb | $0F | grau 3 |

Alle Texte des Einschaltbilds folgen der Textfarbe ($E535). Nur die Farbbalken
haben eigene Farben, als PETSCII-Steuercodes im Text:

| Balken | ROM-Adresse | Datei-Offset | Code ab Werk |
|---|---|---|---|
| 1 | $F001 | $1001 | $1C (rot) |
| 2 | $F02D | $102D | $81 (orange) |
| 3 | $F03F | $103F | $9E (gelb) |
| 4 | $F06B | $106B | $1E (grün) |
| 5 | $F079 | $1079 | $9A (hellblau) |
| 6 | $E473 | $0473 | $9C (lila) |

PETSCII-Steuercodes der Farben:

| Code | Farbe | Code | Farbe |
|---|---|---|---|
| $90 | schwarz | $81 | orange |
| $05 | weiß | $95 | braun |
| $1C | rot | $96 | hellrot |
| $9F | cyan | $97 | grau 1 |
| $9C | lila | $98 | grau 2 |
| $1E | grün | $99 | hellgrün |
| $1F | blau | $9A | hellblau |
| $9E | gelb | $9B | grau 3 |

Hinweise:
- Text- und Hintergrundfarbe nicht gleich wählen, sonst ist nichts mehr lesbar.
- Der Steuercode $06 (`PRINT CHR$(6);`) ist neu und stellt die Textfarbe aus $E535 ein.
  Das Einschaltbild benutzt ihn nach jedem Balken.
- Die Adressen gelten für diesen Stand des Kernals; bei späteren Fassungen vor
  dem Ändern das bisherige Byte vergleichen.
- Eine geänderte Datei hat eine andere Prüfsumme als die veröffentlichte.
- In `C64IIDolphinDos26.bin` steht der Kernal bei Offset $2000: Dort zu jedem
  Datei-Offset aus den Tabellen $2000 addieren (z. B. Rahmen $2CD9).

## Aufbau

| Datei | Bereich | Inhalt |
|---|---|---|
| `src/kernal.s` | – | Hauptdatei, Übersicht über alle Dolphin-Funktionen |
| `src/symbole.inc` | – | RAM/Zeropage/E/A-Symbole (CBM-Namen), Dolphin-Variablen |
| `src/e000_basic.s` | $E000–$E4FF | BASIC-Teil (EXP, RND, SYS, LOAD/SAVE, Init) |
| `src/e500_editor.s` | $E500–$ED08 | Bildschirm-Editor, Tastatur |
| `src/ed09_seriell.s` | $ED09–$EEBA | serieller IEC-Bus |
| `src/eebb_dd_lade.s` | $EEBB–$F0BC | Dolphin: Parallel-LOAD/-SAVE (Rest frei) |
| `src/f0bd_kanal.s` | $F0BD–$F49D | Meldungen, Kanäle, OPEN/CLOSE, F-Tasten-Texte |
| `src/f49e_load_save.s` | $F49E–$F72B | LOAD, SAVE, Uhr, Fehler, F-Tasten |
| `src/f72c_dd_haupt.s` | $F72C–$FCE1 | Dolphin: Paralleltreiber, BASIC-Erweiterungen, Floppybefehle |
| `src/fce2_init.s` | $FCE2–$FF7F | Reset, RAMTAS, NMI, IRQ, CTRL-Funktionen |
| `src/ff80_vektoren.s` | $FF80–$FFFF | Kernal-Sprungtabelle, Vektoren |

Konventionen:
- Labels und Symbole des Originals tragen die Namen der Commodore-Quellen
  (`../Referenzen/cbmsrc/KERNAL_C64_03`, `BASIC_C64`), kleingeschrieben.
- Von DolphinDOS geänderte oder neue Zeilen tragen `DD:` im Kommentar.
- Dolphin-Routinen: `dd_*` (allgemein), `mon_*` (Monitor), `par_*` (Parallelport),
  `cen_*` (Centronics), `fkey_*` (Funktionstasten). `l_xxxx` sind lokale
  Sprungziele (Adresse im Namen).
- Jedes Modul prüft seine Startadresse mit `.assert`.

## Werkzeuge (`tools/`)

Mit diesen Werkzeugen wurde die erste Disassemblierung erzeugt. Sie werden für
den Build **nicht** gebraucht, maßgeblich sind die Quellen in `src/`.

- `cbmalign.py` legt die CBM-Quellen auf das Original-Binär 901227-03 /
  901226-01 und gewinnt daraus Symbole, Labels und Originalkommentare je Adresse.
- `dis.py` disassembliert das Dolphin-ROM. Unveränderte Teile übernimmt es mit
  den CBM-Namen, den Dolphin-Code verfolgt es ab den Einsprüngen. Gesteuert wird
  es über `steuer.txt` (Einsprünge, Daten, Namen).
- `testbau.sh` erzeugt diese Erst-Disassemblierung neu in `build/gen/` und
  vergleicht sie mit dem ROM.

## Hinweise

- Getestet im Emulator VICE (GUI): mit DolphinDos26 (Multi-Speeder, parallel),
  DolphinDos26UL (C64U-Aufbau), JiffyDOS-1541 und Standard-1541 – LOAD, SAVE,
  VERIFY (auch `,8,1`, `,8,2`, `$`), Status (ST), IRQ/Tastatur, Einschaltbild
  PAL/NTSC. Der Kernal läuft auch auf echter Hardware (bestätigt vom Entwickler).
- Einige Original-Reste (Kassettenroutinen) sind nicht mehr erreichbar und als
  solche kommentiert.
- `stack_code` ($FB03) ist die Pause-Funktion CTRL-RETURN: „Programm anhalten,
  bis CTRL wieder losgelassen wird“ (DolphinDOS-3-Anleitung, Anhang D).
