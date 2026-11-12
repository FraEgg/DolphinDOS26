# MS-Tools

C64 programs (C64 mode, 6510; on the C128 after `GO 64`) for the 1541 Switchless
Multi-Speeder V3 with DolphinDos26, by Frank Eggen. Each tool loads like a
BASIC program and starts with `RUN`:

```
LOAD"MS-STATUS",8
RUN
```

Each tool carries the same identification, on `LIST` and after `RUN`:

```
10 REM MS-STATUS BUILD 1 / 2026
20 REM BY FRANK EGGEN
30 REM SWITCHLESS MULTI-SPEEDER V3
40 SYS2147
```

The build number is in `buildnr/<tool>.nr` and increases with every
successful assembly of the tool (source code, includes or shared
routines changed); the year is the year of the build.

## User interface

Tools with user controls use the shared PETSCII interface (`src/ui.s`,
`include/ui.inc`). All interface texts are in English (the comments in the
source code in German):

- Border and background red, text white, highlights yellow,
  secondary information light gray, success light green
- Line 0 title bar (white reverse): tool name on the left, build on the right;
  line 1 SWITCHLESS MULTI-SPEEDER V3 (yellow), line 2 BY FRANK EGGEN (gray),
  line 3 separator line; line 24 help line (white reverse)
- Menu: CRSR up/down selects (yellow reverse bar), RETURN confirms,
  RUN/STOP or `←` exits; with `ui_mlr`, CRSR left/right report a
  changed value (e.g. number of runs)
- On exit (`ui_exit`), border, background, text color and
  character set switching as before the program start (remembered by `ui_init`), then
  an empty screen in this text color

Routines: `ui_init`, `ui_exit`, `ui_puts` (text at `ui_row`/`ui_col` in
`ui_color`, `ui_rev`), `ui_clrrow`, `ui_help`, `ui_menu` (`ui_mtab`,
`ui_mcnt`, `ui_msel`), `ui_getkey`.

## Structure

| File | Contents |
|---|---|
| `ms-tools.d64` | disk "MS-TOOLS", ID 26 – `make` writes the tools here |
| `src/<tool>.s` | one tool (ca65): `.define TOOLNAME "NAME"`, `.include "tool.inc"`, then the entry point |
| `include/tool.inc` | BASIC header (REM lines + SYS, address calculated) and title text `ms_title` |
| `src/common.s` | shared routines for text output: `ms_header` (title + separator line), `print` |
| `src/drive.s`, `include/drive.inc` | drive routines: channel 15, command, `M-E` with parameters, `M-R` (both with retries), status message; addresses of the MS-Addon API |
| `src/ui.s`, `include/ui.inc`, `include/ui_def.inc` | PETSCII interface (see above) |
| `include/kernal.inc` | KERNAL entry points, zero page, PETSCII |
| `c64-prg.cfg` | ld65: load address $0801, BASIC header, then the tool's code, then common |
| `src/drv-<name>.s`, `drive.cfg` | drive programs (from $0400, at most 512 bytes), via `.incbin` in the tool, uploaded via M-W and started via M-E |
| `buildnr/<tool>.nr` | build number per tool |
| `tests/test_tools.py` | LOAD, LIST, RUN, interface, colors and exit of each tool in the patched VICE (GUI); different colors are set before each start, after exit border, background and text color must be the same again |
| `tests/test_memtest.py` | MS-MEMTEST: select drive 9 (missing), run without errors, run with a byte corrupted via the monitor, DolphinDOS afterwards |
| `tests/test_fastcopy.py [on/off] [40] [side2]` | MS-FASTCOPY: read and two copies, target D64 byte-identical to the source |
| `tests/test_fastcopy_reu.py [case]` | MS-FASTCOPY with REU: VIA1/PIA detection, copies byte-identical, 40 tracks, formatting, write protection, without REU/parallel |
| `tests/test_fastcopy_d64.py [case]` | MS-FASTCOPY: IMPORT/EXPORT D64 FILE with MS-RAM and REU, 35/40 tracks, file = disk, invalid files |
| `tests/test_fastcopy_fast.py [case]` | MS-FASTCOPY `TRANSFER: FAST`: VIA1, PIA, DD2, 40 tracks, unformatted, write protection |
| `tests/test_fastcopy_led.py` | MS-FASTCOPY: red LED while reading/writing, DIRECTORY with paging, missing drive |
| `tests/test_nibcopy.py` | MS-NIBCOPY: read/write via MS-RAM and REU, target bit-identical to source, TRACK INFO, presets (20 checks) |
| `tests/test_rs232.py` | MS-RS232: LIST header, install, send/receive via VICE's RS-232 emulation (TCP test server), floppy access with an open RS-232 file, unhook, rehook (8 checks) |
| `tests/test_import.py [name\|test] [reu]` | MS-NIBCOPY: IMPORT G64 FILE from drive 9, WRITE DISK, target = G64 file, for games start of the copy |
| `tests/test_nibcopy_index.py [1571\|cr\|1541] [off]` | MS-NIBCOPY: copy with index hole (1571, 1571CR in the C128DCR), same position of every track relative to the hole; 1541: matching payload without index |
| `tests/test_nibcopy_1571.py [1571\|cr]` | MS-NIBCOPY: commands of the 1571 payload (INDEX, READ/WRITE from the index) directly |
| `tests/test_nibcopy_dir.py` | MS-NIBCOPY: DIRECTORY, END TRACK after import, tracks in MS-RAM survive the directory |
| `tests/test_nibcopy_names.py [fill byte ...]` | MS-NIBCOPY: suggestion and input of drive and file name with pre-filled RAM |
| `tests/test_led.py` | MS-NIBCOPY: red LED on during reading, off afterwards |
| `tests/test_export.py [name\|test] [reu]` | MS-NIBCOPY: EXPORT G64 FILE to drive 9 (directory), file = source, for games from `../G64` start of the exported file |
| `tests/test_protected.py` etc. | MS-NIBCOPY with copy-protected G64 images (folder `../G64`), profiling (`profile_*.py`) |

## Building

```
make          # build tools, pack, write to ms-tools.d64 (replace files of the same name)
make clean
```

The disk receives the versions packed with **Exomizer 3**
(`build/<name>.exo.prg`, `tools/exopack.py`). The BASIC header with name,
build and author stays unpacked at the front (LIST shows it as before), behind it
is the self-extracting file, assembled for exactly the address
the `SYS` points to (`exomizer3 sfx <einsprung> -n -Di_load_addr=… -Di_raw=1`;
`-n`: no border flicker, the tools remember the colors at startup).
After unpacking, it jumps to the tool's entry point. Exomizer 3.1
is built from `../Referenzen/krill-loader-v194/loader/tools/exomizer-3.1/src`
(`make`) and the program is placed in the path as `exomizer3`
(`make EXOMIZER=…` for a different location). Savings: MS-NIBCOPY 86 → 47,
MS-FASTCOPY 17 → 12, MS-MEMTEST 15 → 12 blocks.

New tool: create `src/<name>.s`, enter `<name>` in `TOOLS` in the Makefile,
add a test case in `tests/test_tools.py`.

## Tools

| Name | Function |
|---|---|
| `MS-STATUS` | show the drive's error channel, menu READ STATUS / QUIT (template for further tools) |
| `MS-MEMTEST` | RAM test of the 512 KB SRAM (64 banks): 4 patterns, 1-99 runs, display per bank |
| `MS-FASTCOPY` | disk copy via the 512 KB RAM (data copy like CDR/CDW), 35/40/AUTO tracks, verify on/off, CDR1/CDR2 and CDW1/CDW2, multiple copies |
| `MS-NIBCOPY` (BETA) | nibble copier modeled on nibtools: read and write tracks with bit accuracy (syncs, gaps, tracks 36–42, half tracks, weak bits), storage in Multi-Speeder RAM or in the REU; also runs with DolphinDos26UL (C64U), then only with REU |
| `MS-RS232` | RS-232 driver for device 2 on the user port (the DolphinDos26 kernal has no RS-232 routines): routines of the original kernal in RAM at $9800-$9FFF, OPEN 2,2,… as on the original C64 |

### MS-MEMTEST

The test program `src/drv-memtest.s` runs in the drive. One run: for each
pattern (`$55`, `$AA`, address = offset ⊕ page ⊕ bank, address inverted)
first fill banks 1-63, then check them all – this also reveals overlapping banks
or pages. Bank 0 (working RAM of DolphinDOS) is tested at the end in one
call and saved to bank 1 for this purpose. The remaining RAM contents
(CDR sides, RAM disk) are lost: the tool switches off the RAM disk
beforehand (`CDM0`).

Display: 8×8 banks (logical numbers 00-63), gray = pending, yellow reverse =
being tested, green = OK, black reverse = FAIL (persists across all runs),
plus the number of faulty bytes and the first error with bank, address, expected
and actual value. One run takes about 2 minutes.

Menu: START TEST, RUNS (1-99), DRIVE (8-11, preset to the drive
the tool was loaded from), QUIT; change values with cursor left/right or RETURN.
The drive routines come from `src/drive.s` (`M-E`/`M-R` are
retried up to three times on transfer errors).

### MS-FASTCOPY

> **Warning:** With `MS-RAM` storage, the tool overwrites the contents of the selected
> slot when reading and on D64 import, that is the CDR side and any RAM disk stored there.
> Save important data to disk first with `@CDW1` or `@CDW2`.

Minimum hardware requirements: C64 or C128 in C64 mode; for MS-RAM storage a 1541 with
Switchless Multi-Speeder V3 and DolphinDos26 or DolphinDos26DD2 (MS-Addon API); for REU storage
an active parallel cable, a DolphinDOS kernal (`C64DolphinDos26.bin` recommended) and an REU of
at least 256 KB (two slots from 512 KB). One of the two storage options (MS-RAM or REU) is
required; without it nothing is copied and only DIRECTORY remains.

Copies a disk in one pass via the Multi-Speeder's RAM,
track by track with display (data copy like `CDR`/`CDW`).
Uses the MS-Addon API of DolphinDos26 (jump table from `$3FFF`, see
`dd25/README.md`).

Two-column menu as in MS-NIBCOPY: `SETTINGS` on the left, `ACTIONS` on the right.
CRSR up/down moves through all items, CRSR left/right changes a setting or
jumps from right to left.

- Settings (CRSR left/right or RETURN):
  - `STORAGE` – `MS-RAM 1/2`: one of the two RAM halves of the Multi-Speeder
    (internally side 1/2 like `CDR1`/`CDR2`), `REU 1/2`: 256 KB each at the top end
    of the REU (1 slot from 256 KB, 2 from 512 KB); reading and writing always use
    the selected memory. The REU also works without a Multi-Speeder and without the
    API, but only with a parallel connection: the tool checks it at startup and on
    every drive change and shows `PARALLEL: PIA` or `PARALLEL: VIA1` (also on DolphinDos26DD2, whose
    PIA only switches the RAM banks, and on the original DolphinDOS 2.0 from bank 2, from Build 29); without it
    `NO PARALLEL`, and the REU is not offered. The sectors travel via
    `U1`/`U2` (slower than `MS-RAM`, which works only inside the drive). MS-NIBCOPY
    uses the REU from the bottom: with a small REU the data of the two tools can
    overwrite each other, which the tool does not always detect
  - `TRACKS: 35/40/AUTO` – AUTO checks track 36 like `CDR`
  - `TRANSFER: FAST/DOS` – applies to `STORAGE: REU` and to `COPY DISK` with `STORAGE: MS-RAM`
    (raw path, see below). With the REU, `FAST` (the default) is a separate drive
    code (`src/drv-fast.s`, one variant each for VIA1 and PIA): raw GCR at the pace of the
    disk over the cable, signalled by edges of the CLK line; the track is converted and
    checked on the C64, and generated completely anew when writing (track erased first).
    Screen off during the session. In VICE about 30 s reading, 44 s writing with verify
    for 35 tracks. `DOS` is the slower path via `U1`/`U2`
  - `VERIFY: ON/OFF` – XV for writing only
  - `DRIVE: 8-11` – preset to the drive the program was
    loaded from; on a change, the API is checked on the new drive
    ("DRIVE 09: NO MS-ADDON API" if it is missing)
- Actions: `COPY DISK` (read, then write), `READ DISK`, `WRITE DISK`; after
  each write, `ANOTHER COPY?` asks – this produces any number of copies from
  one read
- `EXPORT D64 FILE` / `IMPORT D64 FILE`: write the contents of the memory as a D64
  file to a drive or load it from there, typically an SD2IEC. Dialogs as in
  MS-NIBCOPY (`EXPORT TO DRIVE: 09`, `FILE NAME:`, `.D64` is appended, an
  existing file is replaced on export). Import: 35 or 40 tracks, also with an
  error table (ignored), other sizes report `NOT A VALID D64 FILE`. With `MS-RAM`,
  its drive cannot be target or source; writing into the MS-RAM needs no new API
  (sector via `#0` to `$0300`, code in the `M-E` command copies it into the bank)
- `DIRECTORY` shows the directory of the disk in the selected drive
  (CRSR up/down: line, left/right: page, RETURN or `←`: back); also works
  without the MS-Addon API. Up to 160 lines; the last one (`BLOCKS FREE`)
  always stays visible
- The red LED is lit during the whole of reading and writing: the tool
  keeps a direct access channel (`#`) open during the session, because the
  DOS idle loop otherwise switches the LED off after each command;
  API OPEN/CLOSE switch it on themselves (code in the `M-E` command, no ROM change)
- If the target disk is not readable (read errors 20-29 on opening), the
  tool asks `NOT FORMATTED - FORMAT 35 TRACKS?` (or 40) and on
  RETURN formats with `N:` – name and ID from the BAM of the source in the RAM slot (API E6),
  so that the ID of the sector headers matches the copied BAM
- Grid of tracks 1–40: gray pending, yellow reverse current, green done,
  black reverse error; below it, the activity, the drive's message and the
  track count of the two RAM slots

**Raw path into the MS-RAM (`COPY DISK`, `STORAGE: MS-RAM`, `TRANSFER: FAST`):** Separate drive
code (`src/drv-fast.s` with `-D RAW`, one part at `$0300`, the rest at `$7000` in bank 0) reads
the tracks as raw GCR directly into the banks (slot 1: banks 1-31, slot 2: banks 32-62, marker in
bank 63, 25 sectors per bank) and writes them back from there, with its own check (four
parities) and verify in the drive. In VICE about 18 s reading, 30 s writing with verify for 35
tracks.

> **Warning:** After `COPY DISK` with the raw path, the slot holds **raw** data in RAM and is
> not converted back. `@CDW1`/`@CDW2` and the RAM disk `@CDM` would turn it into garbage. Inside
> the tool a raw slot is detected: `WRITE DISK` writes it correctly, `EXPORT D64 FILE` refuses it
> (`RAW COPY IN SLOT`), `READ DISK` and `IMPORT D64 FILE` make the slot normal again.

### MS-15SECCOPY

A new version of **15 Seconds Copy**, written by **Mike Pall** in 1986.
Thanks to Mike Pall for his pioneering work! Copies normally formatted disks as raw GCR over
the parallel cable, with track and sector grid and an interface after MS-FASTCOPY. On
`ms-tools.d64` and also on its own disk `ms-15seccopy.d64`, source in `15SecCopy/neu/`.

Minimum requirements:

| Component | Minimum requirement |
|---|---|
| C64 | C64 or C128 in C64 mode, also C64U |
| REU (required) | at least 256 KB for 35 tracks, 512 KB for 40 tracks |
| Parallel cable (required) | on VIA1 of the 1541 (SpeedDOS cable) or on the PIA (DolphinDOS 3, Multi-Speeder); if there is no PIA at `$5000` (for example under DolphinDOS 2.0 on the Multi-Speeder), `PIA` is locked (`NO PIA AT $5000 IN THIS DRIVE ROM`); the program does not check whether a cable is connected |
| Drive | 1541 or 1571 as device 8; the original ROM is enough, DolphinDos26, Multi-Speeder and RAM expansion are not needed; for `BACKUP` and `VERIFY` the program sets a 1571 with DolphinDOS to 1 MHz with `X-` and back to 2 MHz with `X+` afterwards |
| C64 kernal | the original kernal is enough |

On real hardware (C64U, 1541, REU), `BACKUP` and `VERIFY` ran over all 683 blocks without errors,
on VIA1 under DolphinDOS 2.0 and on the PIA under DolphinDos26DD2; 35 tracks took at most 12 s
reading and 18 s writing. Source and target were the same disk.

> **Warning:** The program uses the REU as a buffer. Data stored there, including slots
> of MS-FASTCOPY and MS-NIBCOPY, may be overwritten.

### MS-NIBCOPY (BETA)

> **Warning:** With `MS-RAM` storage, the tool overwrites almost the entire RAM of the
> Multi-Speeder (banks 1-63) when reading and on G64 import, that is both CDR sides and any
> RAM disk. Save important data to disk first with `@CDW1` and `@CDW2`.

**BETA:** MS-NIBCOPY is in BETA and still under development. Functions and operation may
still change; it has only been partly tested on real hardware. The user interface shows
`MS-NIBCOPY BETA`.

On real hardware (C64U with a 1541, Multi-Speeder V3 with DolphinDos26DD2 on VIA1) it reads and
writes normal disks with MS-RAM and REU (35 tracks, verify on, files byte-identical afterwards).

Minimum hardware requirements: C64 or C128 in C64 mode; 1541 with Switchless Multi-Speeder V3
and DolphinDos26 or DolphinDos26DD2, 1571/1571CR (C128DCR) with Multi-Speeder and DolphinDos26 for the
1571, or DolphinDos26UL (C64U or DolphinDOS 2 hardware); active
parallel cable (PIA or VIA1); MS-RAM storage (Multi-Speeder only) or an REU large enough for the
end track (512 KB for 35-40 tracks, 1 MB or more for track 42 with half tracks). One of the two
storage options is required; with DolphinDos26UL only the REU, without it the tool shows
`NEED REU` and blocks reading and writing.
MS-NIBCOPY has not been tested with DolphinDOS 2.

**1571 and C128:** When connecting, the tool selects the drive payload by the power-on text in the
drive ROM (`…1571` at `$E5C4`): on the 1541 as before (PIA or VIA1 cable), on the 1571 the 1571
version (`src/drv-nib.s` with `-D D1571`: PIA only, side 0, 1 MHz for everything with byte ready,
2 MHz for the transfer). After the start both payloads are held in the RAM under the I/O area
(`$D000`). With the 1571 the tool uses the **index hole** (EDIT PRESET: `INDEX HOLE AUTO/OFF`,
byte 7 of the preset, 0 = AUTO): the payload detects it by the bit at `$2000` that changes with the
hole (WD1770 bit 1 on the 1571, MOS 5710 bit 6 on the 1571CR; `$D0` to the WD1770 only if nothing
changes without it), reads every track from the hole and writes it with a lead-in after the hole so
that it has the same position relative to the hole as on the original; the seam stays in a gap.
On the **C128** (in C64 mode, detected by `$D030`) the tool computes and transfers at 2 MHz;
during READ/WRITE the VIC screen is dark and shown briefly for each track. Measured (emulator,
tracks 1–35 with index hole): C128DCR read 115 s / write 134 s, C64 with 1571 138 s / 174 s.

Nibble copier modeled on nibtools
(github.com/rittwage/nibtools), ported to the C64. A payload
(`src/drv-nib.s`, 1280 bytes, `$0300–$07FF`, and thus full; variables in the command buffer
`$0200`) is loaded via M-W to `$0300` and started via M-E; it
talks to the C64 over the parallel cable (`src/nibdrv.s`). The payload detects
by itself at startup which cable is in the drive: if there is a 6821 PIA at `$5000`
(Multi-Speeder or DolphinDOS 3 cable; checked via the
DDRA/ORA switching with CRA bit 2), it works via the PIA, otherwise via
the SpeedDOS cable on VIA1 (`$1801`, CB1/CA2) like DolphinDos26UL on the C64
Ultimate. The firmware DolphinDos26DD2 (last character of the power-on message
`$E5C7` = `$B2`) also uses the VIA1 cable; its PIA only switches the RAM banks,
and MS-RAM stays available as storage. The C64 side is the same for both cables. In VIA operation, the
payload checks DATA while waiting only about once per second, because every read of
`$1800` clears the CB1 flag. The evaluation runs on the C64: density (`scan_track`),
cycle and alignment (`src/nibana.s`), write buffer (`src/nibwr.s`),
weak bits (`src/nibweak.s`), REU (`src/reu.s`).

Why slower than nibtools on a PC with an XUM1541: a full track takes about 1.5 s when
reading (VICE, `tests/profile_nibcopy.py`): 220 ms reading, 363 ms transfer, about 850 ms
evaluation on the 6510. nibtools computes the same steps on the PC and has verify off by
default when writing (`track_match = 0`); here VERIFY is on by default. The drive itself
makes no big difference: on a 1541, nibtools also fetches the raw data over a parallel
cable, 8 KB per track.

- Two-column main menu: on the left SETTINGS – PRESET (STANDARD / EXTENDED /
  CUSTOM 1-3), END TRACK, HALFTRACKS, EDIT PRESET (tracks, half tracks,
  ALIGNMENT, DENSITY, RETRIES, VERIFY, SAVE PRESETS as `MS-NIBCOPY.CFG`),
  DRIVE 8-11, STORAGE; on the right ACTIONS – COPY DISK, READ DISK, WRITE DISK
  (then ANOTHER COPY?), IMPORT G64 FILE, EXPORT G64 FILE, TRACK INFO, DIRECTORY, QUIT.
  CRSR up/down moves through all items, CRSR left/right changes a
  setting or jumps from the right column to the left
- During reading and writing, the drive's red LED is lit (payload:
  with the motor; afterwards the DOS sets it again itself)
- DIRECTORY: directory of the selected drive as in MS-FASTCOPY
  (CRSR up/down: line, left/right: page; RETURN or `_`: back). The tracks in
  memory are kept; the payload is reloaded afterwards, because the DOS buffers
  are where it sits
- STORAGE: MS-RAM (track t -> bank t, half tracks banks 43-62) or REU
  (8 KB per slot, size is detected; in the drive, bank 63 serves as a buffer)
- Writing: measure write protection, rotation speed and capacity per density, then
  track by track with verify (up to 3 attempts)
- EXPORT G64 FILE: write the storage (MS-RAM or REU) as a G64 file to a
  different drive, e.g. an SD2IEC. Prompts `EXPORT TO DRIVE:`
  (CRSR left/right 8-11, RETURN; the device is checked; with MS-RAM,
  the read drive is locked because it supplies the data) and
  `FILE NAME:` (up to 12 characters, `.G64` is appended, a file of the same name
  is replaced). Each half track aligned as when writing, syncs
  lengthened; track length = capacity of the density at 300 rpm (longer
  tracks: their length), weak bits as `$00`; G64 with 84 slots of 7928
  bytes (about 300 KB). With MS-RAM, the tool briefly opens a
  payload session per track so that the serial bus is free for the target.
- IMPORT G64 FILE: load a G64 file from a drive (`IMPORT FROM DRIVE:`,
  `FILE NAME:`) into the storage, then WRITE DISK. Per half track:
  data to TBUF, repeated up to 8192 bytes, detect killer tracks/tracks without sync,
  evaluate like a read; if the length found does not match the file,
  the track applies from its start. The bytes are written unchanged
  (only syncs of at least two `$FF` are adjusted), short syncs
  and weak bits are also preserved. The tracks in the file must be in
  ascending order (VICE, nibtools, EXPORT G64 FILE). Afterwards
  END TRACK shows the last track of the file (value of the current preset,
  so it also applies to the next read; saved only with SAVE PRESETS).
- Memory: program $0801-$5FFF, CODE2 (import, export, menu) is loaded
  behind it and copied to $A000 at startup (BASIC ROM off,
  on again at exit); the waiting half track is under the KERNAL
  at $E000 (access without interrupts)
- **DolphinDos26UL (C64U, without Multi-Speeder):** on connecting, the
  tool reads via M-R the text of the power-on message in the drive ROM (`$E5B8`,
  "OLPHINDOS26 C64U"). Detected: display `READY - DRIVE 08 (C64U)`, STORAGE
  fixed to REU; without REU `NONE (NEED REU)`, reading/writing are rejected with
  `C64U FIRMWARE: STORAGE NEEDS A REU`. Track buffers are then the
  8 KB of drive RAM at `$6000`; after each session the tool itself resets the
  drive with `UJ` (DolphinDos26UL restores its
  default settings in the process). Transfer via the C64U's VIA1 cable.
- Tests (VICE, GUI): `tests/test_nibcopy.py` (Multi-Speeder, PIA) and
  `tests/test_nibcopy_ul.py` (DolphinDos26UL, standard parallel cable on VIA1
  without PIA, REU; `UL_ROM`, `MS_PORT`).

### MS-RS232

The DolphinDos26 kernal – like the DolphinDOS kernal before it – has no
RS-232 routines; their space ($EEBB-$F0BC, NMI part, OPEN) is needed for
parallel LOAD/SAVE and JiffyDOS (together around 1000 bytes, only
167 are free in the kernal). MS-RS232 brings them back as a RAM driver:

- `src/rs232drv.s`, linked for `$9800` (`rs232drv.cfg`), via `.incbin`
  in the tool: send, receive, NMI and OPEN instruction-identical from the CBM sources
  `KERNAL_C64_03` (rs232trans/rcvr/inout/nmi, open, channelio, irqfile)
- Memory `$9800-$9FFF`: code up to `$9DFF`, receive buffer `$9E00`,
  send buffer `$9F00`; the end of BASIC memory is lowered to `$9800`
- Hooked into the kernal vectors NMINV, IOPEN, ICLOSE, ICHKIN, ICKOUT,
  IBASIN, IBSOUT, IGETIN, ILOAD, ISAVE: the driver handles device 2, everything
  else is passed on to the kernal; before accesses to other devices, the
  RS-232 NMIs are paused (RSP232 as in the original before serial accesses) – floppy and
  Dolphin parallel cable (FLAG on CIA 2) are not disturbed
- Own variables instead of the original addresses ($A7-$AB, $B4-$B6, $BD,
  $F7-$FA, $0293-$029E), because the DolphinDos26 kernal uses those itself;
  only ENABL ($02A1) remains (the kernal's NMI end at $FEB6)
- Status: READST in the DolphinDos26 kernal always returns ST ($90); the
  RS-232 status is copied to ST after each character and cleared
- Bug fix compared with the original: when reception is switched on
  (CHKIN), a start bit is expected (RINONE); in the original, the first
  character afterwards was often read shifted by one bit (in the VICE test: "?ORLD"
  instead of "WORLD")
- `SYS 38912` hooks it in again (e.g. after RUN/STOP-RESTORE), `SYS 38915`
  unhooks it and sets the end of memory back to `$A000`; if the driver is
  already hooked in, MS-RS232 does not copy it again
- Example: `OPEN 2,2,0,CHR$(8)` = 1200 baud 8N1 (`CHR$(6)` 300,
  `CHR$(10)` 2400), `PRINT#2,A$`, `GET#2,A$`, `CLOSE 2`
- RS-232 and the Dolphin parallel cable share the user port; on hooking in, the
  driver checks whether the kernal's NMI handling is at
  `$FE56`/`$FEB6` (original kernal and DolphinDos26)
