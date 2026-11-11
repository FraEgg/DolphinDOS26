# C128DD26 – C128 kernal for DolphinDos26

Reconstructed ca65 source code, commented in German, of the Dolphin DOS kernal
for the C128 (`Referenzen/kernal-dolphin128.rom`, 16 KB, $C000–$FFFF: screen
editor, Z80 part and kernal). It is the basis for the adaptation to
DolphinDos26, as with the C64 (`../C64DD26`).

## Building

```
make            # build/c128dd26.bin (US) + byte-by-byte comparison with ref/, build/c128dd26-de.bin (DE)
make de         # only the DE version (ca65 -D DIN), checks the DIN driver against 315078-03
make B=tmp/x    # other build folder
make builds     # both to ../Builds: C128DolphinDos26-US.BIN and C128DolphinDos26-DE.BIN (with MD5),
                # plus C128DCR_KERNAL_29F040-DE.BIN and -US.BIN for the kernal switcher (tools/u32_image.py)
make generiere  # regenerate src/ (overwrites src/!)
```

Needs `ca65`/`ld65` (cc65). The tag `c128dd26-2026-11-10` is byte-identical to
the original (MD5 `854901919a2446bccf68e8392325c021`). Since `cbm-fixes`, `make`
compares with `ref/kernal-dolphin128-05.bin` (original + Commodore fixes).

## DE and US version

Two kernals are built from the same source code:

| File | Market | Keyboard |
|---|---|---|
| `C128DolphinDos26-US.BIN` | international, USA | US editor 318020-05; CAPS LOCK as usual |
| `C128DolphinDos26-DE.BIN` | German-speaking countries | additionally the German keyboard driver from 315078-03: the CAPS LOCK key is the **ASCII/DIN key** (locked down = DIN with the German umlauts and the sharp s, swapped Y/Z and dead keys, up = ASCII); when switching, the character set is loaded into the 80-column RAM |

The driver (`src/c128dd/din_treiber.s`, 524 bytes) comes from `EDITOR_C128_DIN/german.src`. In the original it sits at $FC80; in DolphinDos26 that area holds the JiffyDOS routines. In the DE version it therefore sits in the gap after the wedge ($E7C5–$E9D0, tables on page $E8). As in the German editor it is hooked in at five places (`.ifdef DIN`): jump table `scnkey` ($C012), CINT (`nat_init`, table init via `ascii_din`/`nat_scnkey`), the key scan in the editor loop and `keychk` in ed3 (`nat_keychk`). `tools/din_vergleich.py` assembles the driver at $FC80 as a test and compares it byte by byte with 315078-03 (0 differences). Without `DIN` the ROM is byte-identical to the previous version (MD5 `859493314e98777a595d0f2a039e6800`).

To show the umlauts correctly, the German C128 needs its German character ROM (315079-01); with the US character set the US characters appear in their place. In VICE the ASCII/DIN key is on F12.

`make builds` uses `tools/u32_image.py` to build the two 512 KB images for the kernal switcher (U32) of the C128DCR as well, matching the banks of `C1571_C128DCR_29F040.BIN`. Only the upper half of each bank is used ($x8000 C64 BASIC, $xA000 C64 kernal, $xC000 C128 kernal):

| Bank | Drive | `C128DCR_KERNAL_29F040-DE.BIN` | `C128DCR_KERNAL_29F040-US.BIN` |
|---|---|---|---|
| 1, 2, 5–8 | CBM DOS 1571 | 901226-01, 901227-03, 315078-03 (German) | 901226-01, 901227-03, 318020-05 |
| 3 | DolphinDOS 3 | 901226-01, DolphinDOS 3.0 C64 kernal, Dolphin C128 kernal | same |
| 4 | DolphinDos26 | `C64IIDolphinDos26.bin`, `C128DolphinDos26-DE.BIN` | `C64IIDolphinDos26.bin`, `C128DolphinDos26-US.BIN` |

The source ROMs are in `ref/orig` (the DolphinDOS 3.0 C64 kernal comes from bank 3 of the earlier release). The original Dolphin C128 kernal has a US editor; there is no German version of it.

## How the source code is made

`tools/rekon.py` (taken over from `../JiffyDOS`) lays the Commodore sources from
`../Referenzen/cbmsrc` over the base ROM. Unchanged lines get the original names
and the translated original comments (`uebersetzung/*.tsv`). The Dolphin changes
are disassembled anew and marked `DD:`. Names and comments for the Dolphin code
are in `steuer/c128dd.txt`.

Sources used: `EDITOR_C128`, `KERNAL_C128_05`, `EDITOR_C128_DIN` (only for the
German keyboard driver).

Since JiffyDOS was added (branch `jiffy`), `src/` is authoritative and is
maintained by hand. `make generiere` would overwrite the DD26 changes and only
serves to retrace the reconstruction (tags `c128dd26-2026-11-10`,
`c128dd26-cbm-fixes-2026-11-10`).

## Structure of the Dolphin ROM

**Base:** US kernal 318020-05 (editor $C000–$DFFF unchanged). At $FC80–$FE7F it
holds the German keyboard driver with the DIN tables from kernal 315078-03
(`german.src`). `tools/mische_basis.py` builds the base
`ref/orig/kernal-318020-05+din.bin` from them. The entry points into the driver
(in the DIN editor at $C013, $C090, $C106 etc.) are **not** present, so the
driver is dead code.

**Commodore fixes:** Dolphin had removed all fixes of 318020-04/-05 (behaving
like 318020-03). Since branch `cbm-fixes`, `tools/cbm_fixes.py` puts them back
and produces `ref/kernal-dolphin128-05.bin`, from which the source code is made.
Numbers as in the release notes of 318020-05:

| No. | Fix | Location |
|---|---|---|
| 22 | CAPS LOCK gives a capital Q ($D1 instead of $51) | $FC22 |
| 24 | IOINIT presets the RS-232 registers (`ioinit_pat`); dropped together with RS-232 | ($E159 back to `sta speed`) |
| 25 | VDC PAL R0 = $7F (`vdc_patch`), R4 = $26 | $E191, $E337, $FC67 |
| 26 | INPUT# from the screen (`basin_patch`) | $EF19, $FC40 |
| 27 | OPEN RS-232 without a false error; dropped together with RS-232 | (free) |
| 28 | BOOT "file": start address to SAL/SAH (`load_patch`) | $FC4A, called from `dd_load` ($EC18) |
| 29 | DMA into all RAM banks (`dma_patch`, already at $CF80) | $FF50 |
| 37 | Kernal version $01 | $FF80 |

For no. 28, `dd_load` calls `load_patch` instead of `loding`, because Dolphin
uses the Commodore call at $F2CC for `dd_load`. The editor fixes (no. 23,
30–36) were already present in the Dolphin ROM.

Checked (Multi-Speeder with DolphinDos26, parallel cable): LOAD, VERIFY, BSAVE
and VERIFY as with the original; `BOOT"file"` now starts the program correctly
(the original jumps to a wrong address and ends up in a reset); $FF80 = $01.
No. 24 and 27 were dropped again when RS-232 was removed (see below).

**Dolphin code** (in place of the tape part):

| Area | File | Contents |
|---|---|---|
| $EA1C–$EA48 | `ea1c_dd_name.s` | Substitute name `":*"`, PETSCII→ASCII tables |
| $EAA1–$EC17 | `eaa1_dd_bus.s` | Secondary address + cable detection, send/receive a byte in parallel, Centronics |
| $EC18–$ED4F | `ec18_dd_lade.s` | Parallel LOAD/VERIFY ("XQ"), helper routines |
| $ED60–$EE50 | `ed51_dd_save.s` | Wait loops, address output, parallel SAVE ("XZ") |

Flag `dd_flags` = $DD0C (SDR of CIA 2; the C128 needs the SDR of CIA 1 for the
fast serial bus): b7 parallel cable active, b6 Centronics active, b1 printer
detected, b0 ASCII conversion (secondary address 7). At 2 MHz (`$D030` b0) the
wait times are twice as long.

Further changes: LOAD/VERIFY without a name loads `":*"` or compares `"*"`.
LOAD/SAVE to device 1 go to drive 8, OPEN to device 1 gives ILLEGAL DEVICE. The
message "PRESS RECORD & PLAY ON TAPE" is shortened to make room for " $"/"-$"
(display `LOADING  $bAAAA-$bAAAA`, b = bank). The wait time in `isoura` is
shortened ($64 instead of 184). The keyboard table holds $51 instead of $D1 at
$FC22.

## DD26: JiffyDOS

Every transfer follows this order:
1. **DolphinDos26 parallel** (cable detected after the secondary address), as before.
2. Under ATN (LISTEN, TALK, secondary address) serial, with **JiffyDOS detection**
   in the bit loop of `isour`.
3. **Burst drive** (1571, 1581): the Commodore fast mode, unchanged.
4. **JiffyDOS device** (JiffyDOS 1541/1571, SD2IEC …): all bytes in the JiffyDOS
   protocol – LOAD, SAVE, SEQ files, directory, status.
5. Otherwise normal serial.

On LOAD, a JiffyDOS device additionally switches to block-wise fast loading
(TALK with SA+1). This does not happen with secondary address 2
(`LOAD"x",8,2`), for the directory (`$`) and for load addresses below $0400.
Loading goes into any bank through a modified STASH RAM code (`BLOAD …,B1`,
`BOOT`). During fast loading the screen is briefly off (no bad lines).

| File | Contents |
|---|---|
| `fc80_jiffy.s` ($FC80–$FEF3) | Detection, `jd_listen_init`, `jd_acptr`/`jd_getbyte`, `jd_ciout`/`jd_sendbyte`, `jd_fastload`, `jd_stash_init` (formerly the unused German keyboard driver) |
| `f265_load.s` ($F32F–$F382) | `jd_ladeadr_hi`, `jd_load_weiter`, `jd_stash_wieder` (formerly the unreachable rest of tape LOAD) |
| `e33b_serial.s` | Bit loop with detection, `untlk` ATN first, then CLK, `list1` with `jd_listen_init` |
| `eaa1_dd_bus.s`, `ec18_dd_lade.s` | Switches: `dd_ciout_seriell` → `jd_ciout`, `dd_acptr_seriell` → `jd_acptr`, `dd_load_seriell` → `jd_load_weiter` |

Times measured in the emulator (x128, 8 KB file, through a test script; only
comparable with each other):

| Drive | LOAD | VERIFY | BSAVE |
|---|---|---|---|
| Multi-Speeder DolphinDos26 parallel | 14.2 s | 11.2 s | 24.5 s (as without JiffyDOS) |
| JiffyDOS 1541 | 27.7 s | 24.5 s | 64.8 s |
| JiffyDOS 1541 with the original JiffyDOS C128 kernal | 29.3 s | 24.8 s | 65.3 s |
| Original 1571 (burst) | 27.6 s | 23.0 s | 100.5 s (as without JiffyDOS) |

Also checked: original 1541 serial (as without JiffyDOS), `BOOT"file"` with fast
loading, `BLOAD` into bank 1.

### Origin of the JiffyDOS routines and license

The JiffyDOS transfer routines are **not a new implementation**. They are
instruction-identical copies from the kernal ROM JiffyDOS C128
(`Referenzen/JiffyDOS_C128.bin`, MD5 `cbbd1bbcb5e4fd8046b6030ab71fc021`;
commented reconstruction in `../JiffyDOS/src/c128`): bit loop, `jd_erkennung`,
`jd_listen_init`, `jd_getbyte`, `jd_sendbyte`, `jd_nibtab`, `jd_spritesaus`,
`jd_fastload` with byte loop and STASH template. Only the switches and the
connections to the Dolphin code are new. The JiffyDOS drive firmware is not
included.

Jim Brain of RETRO Innovations allowed publishing the DolphinDos26 kernal on
GitHub on 2 November 2026 and recommended stating the origin of the routines. If
the transfer code is the same – as it is here – he believes the **end user**
would need a license.
**Please check for yourself whether you should buy a JiffyDOS license.**
<https://www.jiffydos.com>

## DD26: Boot screen and LOADING indicator

**Boot screen:** On the C128 the boot screen is printed by the BASIC ROM. Like
JiffyDOS, the kernal hooks into `phoenix` (BASIC calls it on a cold start right
after its message) and prints lines below it, centred for 40 and 80 columns
(`dd_einschalt`, `dd_einr`):

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

The last line reads "PAL SYSTEM" or "NTSC SYSTEM" depending on the system, as
with the C64 kernal. No detection of its own is needed: `ioinit` already
measures the raster line in the original kernal and stores the result in
`palnts` ($0A03).

**LOADING/VERIFYING** show the transfer type (only in direct mode), as on the C64:

| Transfer | Display |
|---|---|
| DolphinDos26 parallel, block-wise | `LOADING DD: $bAAAA-$bAAAA` (b = bank) |
| Parallel cable byte-wise (`,8,2`, `$`) | `LOADING DD:` |
| JiffyDOS fast loading | `LOADING JF: $bAAAA-$bAAAA` |
| JiffyDOS protocol without fast loading (`,8,2`, `$`) | `LOADING JF:` |
| normal serial / burst | `LOADING` |

The texts replace the tape messages in `f6b0_messages.s` (the offsets of all
other messages are unchanged; the file was rewritten by hand, because the
generated version had output `spmsg`/`msg`/`setnam`/`setlfs`/`setbnk` as data).
Selection in `dd_mode_msg`, addresses during fast loading through `jd_adr_aus`.

**OPEN to device 1:** Dolphin reports ILLEGAL DEVICE there, but left the entry
in the file table; a following `PRINT#1` ran into the tape code. `opn_illegal`
now removes the entry again (`?FILE NOT OPEN`).

Checked: boot screen in 40 and 80 columns, PAL and NTSC, all indicators with
Multi-Speeder parallel, JiffyDOS 1541 and original 1541, `OPEN1,1`/`PRINT#1`.

## DD26: @ wedge (DOS commands)

In direct mode, as with DolphinDOS 3 and the C64 kernal DolphinDos26:

| Input | Effect |
|---|---|
| `@` | Read and print the error channel of the default device |
| `@command` | Send a command through channel 15, then the status (e.g. `@I`, `@S:FILE`, `@CD←`, `@CD:FOLDER`, `@N:NAME,ID`) |
| `@$`, `@$:PATTERN` | Show the directory without overwriting the BASIC program (STOP aborts) |
| `@8` … `@11` | Select the default device (8 after power-on), also used by `LOAD`/`SAVE` without a device number |
| `"command"…` | like `@command` (for C=F5 on a directory line) |

`dd_wedge_init` hooks into the BASIC vector `icrnch` ($0304) on a BASIC cold
start (from `dd_einschalt`); the old vector is kept in `dd_crnch`, so the wedge
does not depend on the BASIC version. If an entered line starts with `@`,
`dd_wedge` executes the command and empties the line. To do so, the wedge maps
in the I/O like BASIC does (`put_io_in_map`). Without a device,
`?DEVICE NOT PRESENT ERROR` appears. The STOP+RESTORE warm start leaves the
vector in place. RAM: `dd_defdev` $0A10, `dd_crnch` $0A11/$0A12 (former RS-232
registers).

## DD26: Function keys as with the C64 kernal

The function keys are assigned as with the C64 kernal DolphinDos26, so nothing
has to be relearned when switching between C64 and C128 mode. F2/F4/F6/F8 with
SHIFT, the C= level has texts of its own (on the C128, C= and SHIFT otherwise
give the same code).

| Key | Text | | Key | Text |
|---|---|---|---|---|
| F1 | CLR, `LIST` | | F2 | `RUN:` |
| F3 | CLR, `RUN` | | F4 | `VERIFY` (without a name: `*`) |
| F5 | `LOAD` (without a name: `:*`) | | F6 | `SAVE"@:` |
| F7 | CLR, `@$` (directory) | | F8 | `@X` (X status of the drive) |
| C=F1 | `OPEN4,4:CMD4:LIST` | | C=F3 | `@CD←` + RETURN (SD2IEC: back) |
| C=F5 | `  "CD:` + RETURN (on a directory line: into it) | | C=F7 | ` LOAD` + 3×TAB + `:` (on a directory line: load it, press RETURN yourself) |

SHIFT+RUN/STOP and HELP keep the C128 assignment. F1–F8 are in `pkytbl` ($CEA8)
and can be reassigned with `KEY`; the C= texts are fixed in ROM
(`dd_cfk_texte`, editor patch area $CF19). `dopfky_patch` detects C=
(`shflag` bit 1) with F1/F3/F5/F7 and sets the flag `dd_fk_flag` ($0A13);
`lp2` fetches the characters through `dd_fk_zeichen` from `pkybuf` or from ROM.

On a directory line, C=F5 gives `  "CD:NAME"  DIR`; the @ wedge executes lines
that start with a quote as a drive command (text between the first and the last
quote, inner quotes are dropped). This makes C=F5 and C=F7 fit five-digit block
counts too, without the special check of the C64 kernal. `LOAD`/`SAVE` without
a device number use the device selected with `@n` (otherwise 8); `LOAD"name"`
loads to the start of BASIC as usual on the C128 (SA 0).

Checked: F1, SHIFT+F3, F7, F8 (X status from the DolphinDos26 drive), C=F1, C=F3,
C=F5 and C=F7 on a directory line (loads the file), `KEY` listing.
Note for the VICE emulator: there, C= is on the PC's Tab key.

## DD26: Tape and RS-232 removed

To make room for the wedge, the remaining tape code and the RS-232 routines
(user port) were removed; all other routines stay at their addresses. OPEN to
device 1 or 2 reports ILLEGAL DEVICE, so do CHKIN/CHKOUT/BASIN/BSOUT/GETIN for
these devices, CLOSE only removes the table entry. LOAD and SAVE to device 1
(without a device number) go to the device selected with `@n` (otherwise 8).
`cmpste`/`incsal` (SAVE) and the cassette key check in the IRQ stay. Programs
with their own RS-232 driver are not affected; `OPEN …,2` through the kernal no
longer exists.

## Free space for DD26

About 1170 bytes (filled with $FF, the DD26 gaps are marked `frei_…`):
$E7C5–$EA1B (599, after the wedge; in the DE version the DIN driver uses 524 of them, $E9D1–$EA1B stays free), $EE51–$EEB6 (102), $F06B–$F0CA (96),
$EA4B–$EAA0 (86), $EF27–$EF5B (53), $F1A1–$F1CE (46), $CF9E–$CFBF (34, editor),
$EF8E–$EFAA (29), $CEEA–$CEFF (22, after the function key table),
$EF67–$EF78 (18), $FC55–$FC66 (18) and smaller remainders of 7 to 12 bytes.
