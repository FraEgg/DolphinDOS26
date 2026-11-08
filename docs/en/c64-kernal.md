# C64DD26 – C64 kernal for DolphinDos26

Reconstructed ca65 source code, commented in German, of the C64 kernal
`Referenzen/1-C64_Dolphin_DOS_Silver.rom` (Dolphin DOS "Silver", $E000–$FFFF).
It is the basis for the further development of the C64 kernal into DolphinDos26
(counterpart to the floppy firmware in `../dd25`). It contains routines from a
JiffyDOS kernal, see
[Origin of the JiffyDOS routines and license](#origin-of-the-jiffydos-routines-and-license).

## Building

```
make            # build/c64dd26.bin + byte-by-byte comparison with ref/
make B=tmp/x    # different build directory
make builds     # additionally copy to ../Builds: C64DolphinDos26.bin and C64IIDolphinDos26.bin (with MD5)
```

Requires `ca65`/`ld65` (cc65). `make` compares the result with
`ref/1-C64_Dolphin_DOS_Silver.rom` and lists the differing addresses.
The tag `c64dd26-2026-10-30` is still byte-identical to the original
(MD5 `ab781ee4d19eb2e096b298317b2d0811`).

## DD26 changes

### JiffyDOS (full protocol, LOAD and SAVE)

This order applies to every transfer:
1. **DolphinDos26 parallel** (cable detected after the secondary address), as before.
2. **JiffyDOS**, if the device identifies itself as a JiffyDOS device during TALK/LISTEN
   (JiffyDOS 1541, SD2IEC …). All bytes then run in the Jiffy protocol:
   LOAD, SAVE, SEQ files, directory, status.
3. **Otherwise** normal serial.

On LOAD, a Jiffy device additionally switches to block-wise
fast loading (TALK with SA+1). This does not happen with secondary address 2
(`LOAD"x",8,2`), directory (`$`), load addresses below $0400 and in
Dolphin parallel operation. With `,8,2`, the bytes still run in the
Jiffy protocol.

The routines are taken instruction-identically from the JiffyDOS sd2iec kernal
(`../C64JiffySD2IEC`). `tools/vergleich_jiffy.py` checks this, along with the
page boundaries in the time-critical sections.

| Routine | Address | Purpose |
|---|---|---|
| bit loop | $ED62 | serial send with a call to `jd_detect` |
| `jd_detect` | $F1DF | detect a Jiffy device at the ATN command byte (r2d2 bit 6) |
| `jd_acptr`, `jd_getbyte` | $F409 | receive a byte in the Jiffy protocol (from `dd_acptr`) |
| `jd_ciout`, `jd_sendbyte`, `jd_nibtab` | $F8AF | send a byte (from LIST1 $ED19 and CIOUT $EDE7) |
| `jd_list2` | $F26C | LIST2: clear Jiffy flag |
| `jd_loadadr` (+`jd_loadadr2` $F0A7) | $E4E0 | switch to fast loading |
| `jd_retalk` | $FF61 | UNTALK/TALK/TKSA |
| `jd_load_chk`, `jd_fastload` | $F816 | selection, fast loader preamble |
| `jd_block`, `jd_fl_byte` | $F9C3 | fast loader (time-critical) |
| `jd_print_end` | $FEC2 | print end address |

To make room, dead cassette remnants were removed (FAH $F750, `cste1`/`cste2`
$F816, `tstop` $F8D0, `tnif`/`tnof` $FC93/$FCCA, `fpatch` $E4E0). Moved
were `dec_tab_lo` (now $F72C) and `dd_second_hook` (now $FC93).

Measurement in VICE, 16000 bytes:

| | JiffyDOS 1541 | Standard 1541 | DD26 parallel |
|---|---|---|---|
| LOAD | 6.7 s | 41.2 s | 2.1 s |
| LOAD `,8,2` | 15.8 s | – | – |
| SAVE | 19.1 s | 48.4 s | 4.6 s |

### Origin of the JiffyDOS routines and license

The JiffyDOS transfer routines in this kernal are not a new
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

The ROM file is `JiffyDOS-C64-sd2iec.rom` (MD5
`c9fe23f3273d9beef0bd4c39af86cce9`). The instruction-identical parts are:
bit loop, `jd_detect`, `jd_acptr`, `jd_getbyte`, `jd_sprites_off`, `jd_ciout_spr`, `jd_ciout_chk`,
`jd_sendbyte`, `jd_nibtab`, `jd_block`, `jd_fl_byte`, the preamble of
`jd_fastload` and `jd_retalk`. The remaining connecting routines (`jd_ciout`, `jd_list2`,
`jd_loadadr`, `jd_load_chk`, `jd_print_end`) are modeled on them.

Jim Brain gave his confirmation on request and recommended stating the origin
of the routines so that everyone can decide for themselves whether they need a
license.

The same ROM also served as the template for the SD2IEC F keys, the boot screen
and the PAL/NTSC detection (see below).

### SD2IEC F keys

Modeled on the JiffyDOS sd2iec kernal (on the former monitor keys):

| Key | Text | Effect |
|---|---|---|
| C=F3 | `@CD←` + RETURN | SD2IEC: one directory or disk image back |
| C=F5 | ` "CD/:` + RETURN | on a directory line: change to this directory/image |
| C=F7 | `LOAD` + Tab + `,8,1` | on a directory line: load this file (press RETURN yourself) |

Before each F key text, `dd_fkey_init` ($F750) checks whether the cursor line is a
directory line with quotation marks in column 6 (5-digit
block counts, e.g. on the SD2IEC). It then puts a space in front, so that
C=F5 and C=F7 line up exactly with the file name.

### Monitor and Centronics removed

New are a colored boot screen (bars, "**** COMMODORE 64 ****",
"DOLPHINDOS26/JIFFY/SD2IEC", "PAL SYSTEM" or "NTSC SYSTEM") and a PAL/NTSC detection
via the raster line. Both are modeled on the JiffyDOS sd2iec kernal
(`../C64JiffySD2IEC`): `dd_banner` $EFFE, `dd_palntsc` $F08E (from
PCINT), `words` $E460, `dd_banner_sys` $FEA3 with `txt_pal` $F0AF and
`txt_ntsc` $FE0A.

Between the color bar and "PAL/NTSC SYSTEM", with one blank line of spacing on each
side, is the notice "MULTISPEEDER BY FRANKEGGEN@EMDEN.NET" (`txt_ms` $E47E,
directly after `words`; in capitals in the uppercase character set).

```
       ▌ 38911 BASIC BYTES FREE      (letzter Balken)
     ▌
                                      (Leerzeile)
MULTISPEEDER BY FRANKEGGEN@EMDEN.NET
                                      (Leerzeile)
PAL SYSTEM
```

All other routines remain at their original address. The gaps are
marked with `FREI:` and the label `frei_xxxx` and filled with `$AA`.
`make && python3 -I tools/pruefe_frei.py` lists the free areas, checks the fill and shows all differences from the original outside the gaps.

| Range | Bytes | Previously |
|---|---|---|
| $E4A5–$E4AB | 7 | remainder after txt_ms |
| $EA79–$EA7A | 2 | remainder after dd_mode_msg (datasette check in the IRQ) |
| $EFFC–$EFFD | 2 | STOP check in dd_load/dd_save via the kernal |
| $F0BB–$F0BC | 2 | remainder after txt_pal |
| $F0E0–$F0E2 | 3 | remainder of the cassette texts (PLAY?/REC&PLAY?) |
| $F19F–$F1A4 | 6 | remainder after jd_loadadr2 |
| $F1AA–$F1AC | 3 | dd_rvsout_vec (monitor) |
| $F206–$F20D | 8 | remainder after new code |
| $F229–$F236 | 14 | monitor (mon_cmds) |
| $F275–$F277 | 3 | remainder after new code |
| $F2AA–$F2BD | 20 | monitor (mon_rvsout) |
| $F484–$F494 | 17 | remainder after new code |
| $F662–$F675 | 20 | monitor command G |
| $F731–$F735 | 5 | remainder after dec_tab_lo |
| $F765–$F769 | 5 | remainder after dd_fkey_init |
| $F88E–$F88F | 2 | remainder of the old detour |
| $FA6B–$FA6B | 1 | remainder after dd_ctrl_std |
| $FB91–$FBA0 | 16 | cassette remnants udst/rd180, monitor (mon_out_x, out_space) |
| $FCC1–$FCD0 | 16 | dead cassette routines tnif/tnof |
| $FE17–$FE17 | 1 | remainder after txt_ntsc (RS-232 status in READST) |
| **total** | **153** | |

Changed behavior:
- `SYS 0` and BRK go through the BRK vector $0316, the default is the BASIC warm start.
- CTRL + Reset/RESTORE no longer has any function.
- Colors as in the original C64 ROM: border $0E, background $06, text $0E (Dolphin:
  $00, $00, $03), see [Personalization](#personalization). The texts of the boot
  screen also appear in the text color: a new control code $06 = standard text color
  (`dd_ctrl_std` $FA64, `dd_std_col` $F949) replaces the fixed cyan codes $9F there.
- LISTN releases CLK again on UNLISTEN as in the original.
- Parallel LOAD/SAVE (`dd_load`/`dd_save`) check the STOP key after each
  page with `jsr stop` (aborting only when `stkey` = $7F, as with
  serial save). The original checked only bit 7 with `bit stkey` and
  aborted as soon as a program with its own IRQ left `stkey` below $80:
  Eye of the Beholder (EasyFlash) therefore saved only an empty 0/1 block file
  and loaded nothing. The additional check before the first byte on LOAD
  is dropped.
- Device 4 is always a serial printer, the hardcopy (CTRL-*) goes there.
- The IRQ no longer checks the datasette key and no longer switches the
  datasette motor (r6510 bit 5 stays as set by IOINIT).
  `key4` $EA61 jumps directly to `kl2` $EA7B; $EA7E/$EA81 are unchanged.
- READST ($FFB7 → `readss` $FE07) always returns the status `status` ($90),
  also for device 2 (no more RS-232 status). $FE07 remains an entry point.
- `rd300` (from SAVE) is now at $FB88 instead of $FB8E (before it, dead
  cassette remnants `jsr udst`/`rd180`).
- Moved were `dec_tab_hi` ($F187), `":*"` ($F227) and `dd_second_hook` (code from $F8DD).
- "LOADING"/"VERIFYING" show the transfer type (in direct mode only):

  | Transfer | Display |
  |---|---|
  | DolphinDos26 parallel, block-wise | `LOADING DD: $0801-$xxxx` |
  | parallel cable byte-wise (`,8,2`, `$`) | `LOADING DD:` |
  | JiffyDOS fast loading | `LOADING JF: $0801-$xxxx` |
  | JiffyDOS protocol without fast loading (`,8,2`, `$`) | `LOADING JF:` |
  | normal serial | `LOADING` |

  Texts `ms_jf`/`ms_dd`/`ms_dd_adr` ($F0D8–$F0E6, instead of the cassette texts
  "PLAY?"/"REC&PLAY?"), selection in the detour `dd_mode_msg` ($EA64).
By-products: `build/kernal.lst` (listing), `build/c64dd26.lbl` (labels for the
VICE monitor), `build/c64dd26.map`.

## C64 II

The C64 II (short board) has BASIC and kernal in a single ROM chip
(original 251913). For this, `make builds` creates the file `C64IIDolphinDos26.bin`
(16 KB): at offset $0000 the unchanged BASIC 901226-01, at offset $2000 the
kernal. For a C64 with separate BASIC and kernal chips,
`C64DolphinDos26.bin` remains the right file.

## Personalization

The colors are single bytes in the ROM and can be changed without an assembler:
copy the file `C64DolphinDos26.bin` (8 KB, address $E000 = file offset $0000),
change the bytes with a hex editor and use the copy as the kernal. The C64 does not
check a kernal checksum. The factory values are those of the original C64 ROM.

| Color | ROM address | File offset | Factory value |
|---|---|---|---|
| Border | $ECD9 | $0CD9 | $0E (light blue) |
| Background | $ECDA | $0CDA | $06 (blue) |
| Text (also boot screen, `READY.`, cursor, CTRL-V) | $E535 | $0535 | $0E (light blue) |

Color values:

| Value | Color | Value | Color |
|---|---|---|---|
| $00 | black | $08 | orange |
| $01 | white | $09 | brown |
| $02 | red | $0A | light red |
| $03 | cyan | $0B | grey 1 |
| $04 | purple | $0C | grey 2 |
| $05 | green | $0D | light green |
| $06 | blue | $0E | light blue |
| $07 | yellow | $0F | grey 3 |

All texts of the boot screen follow the text color ($E535). Only the color bars
have their own colors, as PETSCII control codes in the text:

| Bar | ROM address | File offset | Factory code |
|---|---|---|---|
| 1 | $F001 | $1001 | $1C (red) |
| 2 | $F02D | $102D | $81 (orange) |
| 3 | $F03F | $103F | $9E (yellow) |
| 4 | $F06B | $106B | $1E (green) |
| 5 | $F079 | $1079 | $9A (light blue) |
| 6 | $E473 | $0473 | $9C (purple) |

PETSCII control codes of the colors:

| Code | Color | Code | Color |
|---|---|---|---|
| $90 | black | $81 | orange |
| $05 | white | $95 | brown |
| $1C | red | $96 | light red |
| $9F | cyan | $97 | grey 1 |
| $9C | purple | $98 | grey 2 |
| $1E | green | $99 | light green |
| $1F | blue | $9A | light blue |
| $9E | yellow | $9B | grey 3 |

Notes:
- Do not choose the same text and background color, or nothing will be readable.
- The control code $06 (`PRINT CHR$(6);`) is new and selects the text color from $E535.
  The boot screen uses it after each bar.
- The addresses apply to this version of the kernal; with later versions compare the
  existing byte before changing it.
- A changed file has a different checksum from the published one.
- In `C64IIDolphinDos26.bin` the kernal is at offset $2000: add $2000 there to every
  file offset from the tables (e.g. border $2CD9).

## Structure

| File | Range | Contents |
|---|---|---|
| `src/kernal.s` | – | main file, overview of all Dolphin functions |
| `src/symbole.inc` | – | RAM/zero page/I/O symbols (CBM names), Dolphin variables |
| `src/e000_basic.s` | $E000–$E4FF | BASIC part (EXP, RND, SYS, LOAD/SAVE, init) |
| `src/e500_editor.s` | $E500–$ED08 | screen editor, keyboard |
| `src/ed09_seriell.s` | $ED09–$EEBA | serial IEC bus |
| `src/eebb_dd_lade.s` | $EEBB–$F0BC | Dolphin: parallel LOAD/SAVE (remainder free) |
| `src/f0bd_kanal.s` | $F0BD–$F49D | messages, channels, OPEN/CLOSE, F key texts |
| `src/f49e_load_save.s` | $F49E–$F72B | LOAD, SAVE, clock, errors, F keys |
| `src/f72c_dd_haupt.s` | $F72C–$FCE1 | Dolphin: parallel driver, BASIC extensions, floppy commands |
| `src/fce2_init.s` | $FCE2–$FF7F | reset, RAMTAS, NMI, IRQ, CTRL functions |
| `src/ff80_vektoren.s` | $FF80–$FFFF | kernal jump table, vectors |

Conventions:
- Labels and symbols of the original carry the names from the Commodore sources
  (`../Referenzen/cbmsrc/KERNAL_C64_03`, `BASIC_C64`), in lowercase.
- Lines changed or added by DolphinDOS carry `DD:` in the comment.
- Dolphin routines: `dd_*` (general), `mon_*` (monitor), `par_*` (parallel port),
  `cen_*` (Centronics), `fkey_*` (function keys). `l_xxxx` are local
  jump targets (address in the name).
- Each module checks its start address with `.assert`.

## Tools (`tools/`)

These tools were used to produce the first disassembly. They are **not** needed
for the build; the sources in `src/` are authoritative.

- `cbmalign.py` aligns the CBM sources with the original binary 901227-03 /
  901226-01 and derives symbols, labels and original comments per address from them.
- `dis.py` disassembles the Dolphin ROM. It takes over unchanged parts with
  the CBM names and traces the Dolphin code from the entry points. It is controlled
  via `steuer.txt` (entry points, data, names).
- `testbau.sh` regenerates this first disassembly in `build/gen/` and
  compares it with the ROM.

## Notes

- Tested in the VICE emulator (GUI): with DolphinDos26 (Multi-Speeder, parallel),
  DolphinDos26UL (C64U setup), JiffyDOS 1541 and standard 1541 – LOAD, SAVE,
  VERIFY (also `,8,1`, `,8,2`, `$`), status (ST), IRQ/keyboard, boot screen
  PAL/NTSC. The kernal also runs on real hardware (confirmed by the developer).
- Some original remnants (cassette routines) are no longer reachable and are
  commented as such.
- `stack_code` ($FB03) is the pause function CTRL-RETURN: "halt the program
  until CTRL is released again" (DolphinDOS 3 manual, Appendix D).
