# C1571DD26 – C1571DolphinDos26 for the 1571 (C128DCR, 1571 Multi-Speeder V3)

**C1571DolphinDos26** (`C1571_DOLPHINDOS26.bin`, 64 KB) is DolphinDos26 for
the internal 1571 of the C128DCR (1571CR) with the 1571 Multi-Speeder V3 (512 KB
RAM, 8 × 64 KB EPROM, PIA 6821). It replaces **bank 4** of the EPROM (EPROM
offset `$30000`, switched with `4@RNROM`), which previously held DolphinDos25
1571.

It is based on DolphinDOS 3 for the 1571 (bank 3 of the EPROM), plus the
MS-Addon of DolphinDos26 (1541) with the same commands and the same API,
extended for double-sided disks.

## Banks of the 1571 Multi-Speeder EPROM

`n@RNROM` (n = 1–8) selects EPROM bank n−1; the drive then restarts.

| Command | EPROM offset | Contents |
|---|---|---|
| `1@RNROM` | `$00000` | CBM DOS V3.1 1571CR (318047-01) |
| `2@RNROM` | `$10000` | CBM DOS V3.0 1571 |
| `3@RNROM` | `$20000` | DolphinDOS 3 1571 (original) |
| `4@RNROM` | `$30000` | **C1571DolphinDos26** (previously DolphinDos25 1571) |
| `5@RNROM` … `8@RNROM` | `$40000` … `$70000` | JiffyDOS 6.0 1571 |

Drive memory (address decoder ATF16V8 "V3_0PIA_1571", the same for all banks,
EPROM offset = CPU address):

| Range | Use |
|---|---|
| $0000–$1FFF | 1571 (RAM, VIA1 $1800, VIA2 $1C00) |
| $2000–$2FFF | 1571 (WD1770) |
| $3000–$3FFF | EPROM: MS-Addon, API from $3FFF downwards |
| $4000–$4FFF | 1571 (CIA or MOS5710) |
| $5000–$5FFF | PIA 6821 (parallel cable, RAM bank via PB0–PB5) |
| $6000–$7FFF | 8 KB window into the 512 KB SRAM |
| $8000–$FFFF | EPROM: DOS (DolphinDOS 3 1571 with DD26 changes) |

## Installation

1. Put `C1571_DOLPHINDOS26.bin` at offset `$30000` of the 512 KB image of the
   1571 Multi-Speeder EPROM (replaces bank 4), program a 29F040 (alternatively
   27C040 or SST39SF040) and fit it.
2. On the C128, fit the kernal **C128DolphinDos26** (C128 mode) and
   **C64IIDolphinDos26** for C64 mode. In the 8-bank EPROM of the kernal switcher
   (U32), only the upper half of each 64 KB bank is used: the C64 mode (BASIC +
   kernal, 16 KB like `C64IIDolphinDos26.bin`) at `$8000`–`$BFFF` and the C128
   kernal (16 KB, `C128DolphinDos26-DE.BIN`) at `$C000`–`$FFFF`; `$0000`–`$7FFF`
   stays free. The C128 BASIC is not in U32.
3. Switch with `4@RNROM`. The drive reports `73,DOLPHINDOS26 1571`.

## Functions

| Command | Effect |
|---|---|
| `CDR1` / `CDR2` | read disk (tracks 1–35, 40 automatically) into RAM slot 1 or 2 |
| `CDR1+` / `CDR2+` | always read 40 tracks (1541 mode only) |
| `CDW1` / `CDW2` | write RAM slot to disk |
| **`CDRD`** | read a **double-sided disk**: side 0 → slot 1, side 1 → slot 2 |
| **`CDWD`** | write both slots to a double-sided disk |
| `CDM1` / `CDM2` | RAM disk: drive 8 works from slot 1 or 2 |
| **`CDMD`** | **double-sided RAM disk**: drive 8 works from both slots (tracks 1–70) |
| `CDM0` | RAM disk off, back to the disk |

As on the 1541: track 18 in write-back during CDW, CDW without pre-reading the
target track, XQ/XZ (fast load/save) directly from/to the RAM disk, the RAM
disk survives a drive reset.

For CDRD/CDWD/CDMD the addon switches DolphinDOS to 1571 mode
(`$6005 = $12`: maxtrk 71, tracks 36–70 on the back side) and back afterwards –
this also works when the C128 is in C64 mode.

### MS-Addon-API (unchanged, compatible with the MS-Tools)

Jump table from $3FFF downwards as in DolphinDos26 1541 (version 1, 7 entries,
same addresses). Extension without new entries: **side 3 = double-sided**

- `E0 OPEN` side 3: session over both sides, `E1 TRACK` then tracks 1–70
  (36–70 → slot 2), `E2 CLOSE` sets both slots to 35 tracks
- `E6 SECTOR` side 3 with tracks 1–70

Until now side 3 was invalid (31 SYNTAX ERROR), old programs are not affected.
The MS-Tools run on the C128 in C64 mode (`GO 64`).

## Clock: 2 MHz, 1 MHz and `X-`

The 1571 can run at 1 MHz (like a 1541) or at 2 MHz (bit 5 of VIA1 port A).
The Commodore ROM uses 1 MHz in 1541 mode and 2 MHz only in 1571 mode (C128,
burst).

**C1571DolphinDos26 behaves like the original DolphinDOS 3 1571: the drive
always runs at 2 MHz**, even when the C128 is in C64 mode. DolphinDOS needs the
2 MHz for its track cache, which decodes the sectors while reading. The
MS-Addon also runs at 2 MHz. The parallel transfer uses a handshake and does
not depend on the clock.

Consequence for **fast loaders, copy programs and other 1541 floppy code**:
programs that load their own code into the drive (`M-E`, `B-E`, `U3`–`U8`, `&`)
and rely on exact timing there run twice as fast at 2 MHz and may then fail.
There are two ways around this:

| Way | Effect |
|---|---|
| **`@X-`** (or `OPEN1,8,15,"X-":CLOSE1`) | drive at **1 MHz**, DolphinDOS off (no track cache, no parallel and fast load functions, `X` status `R-:…:P-`); it behaves like a 1571 with Commodore ROM in 1541 mode. The setting is kept in the drive RAM and survives a drive reset. |
| **`@X+`** | back to **2 MHz** and DolphinDOS with all functions |
| **`1@RNROM`** | Commodore ROM 1571CR (1 MHz in 1541 mode) for programs that expect an unmodified drive; back with `4@RNROM` |

Recommendation: for games and programs with their own fast loader enter `@X-`
before loading; for copy-protected software that checks the original ROM,
`1@RNROM`.

## PAL and NTSC

The firmware does not depend on the video standard of the computer (the drive
has its own clock). The kernals C128DolphinDos26 and C64DolphinDos26 detect PAL
and NTSC themselves. Parallel transfer and JiffyDOS work in both standards, in
C128 and in C64 mode.

## Changes to DolphinDOS 3 1571 (`make vergleich` lists all bytes)

| Address | Original | DD26 |
|---|---|---|
| $C8C1 | duplct: 31 SYNTAX | `jmp ms_addon` (as DD25-1571) |
| $C8D5 | format: `jsr jformat` | `jsr ms_format` (RAM disk: clear slots) |
| $D580 | sjb1: `sta jobs,x / sta lstjob,x / rts` | `jmp ms_setjob` (RAM disk) |
| $BA20 | job_write: write-through track 18/53 | `jsr ms_wtchk` (write-back during CDW) |
| $F815 | xcmd_q fallback | `jmp ms_xq` (RAM disk block transfer) |
| $FC97 | xcmd_z: `jsr z_prepare` | `jmp ms_xz` |
| $AADD | ptch64 (seek job on track 53 without setjob) | `jmp ms_ptch64` (double-sided RAM disk) |
| $C000 | cchksm $84 | adjust byte of the ROM checksum, computed by `tools/pruefsumme.py` (the check at $EAE5, `bne perr2`, is enabled again) |
| $E5C1 | ".3" | "26" → `73,DOLPHINDOS26 1571` |

Differences from the 1541 that the addon takes into account: binary track
cache (sector status $10 = changed, $00 = valid), mode flag $6005 instead of
pota1 (hence `ms_save_r` is now $60E9), in 1541 mode DD3-1571 does not move the
head beyond `dd_maxtrk-1` (a probe on track 36 therefore reports 21 itself).

## Performance

Real time, 35-track disk or 30 KB file:

| | DolphinDos25 1571 | C1571DolphinDos26 |
|---|---|---|
| CDR1 | 20.8 s | 16.0 s |
| CDW1 | 42.6 s | 23.3 s |
| CDRD / CDWD (double-sided) | – | 40 s / 59 s |
| LOAD parallel (C128 / C64 mode) | 6.2 s | 6.3 s / 5.3 s |
| LOAD from the RAM disk | – | 3.8 s |

## Building

    make            # build the bank + list the differences to DD3-1571
    make bank       # build/dd26_1571.bin (64 KB)
    make rom        # build/C1571_AM27C040_DD26.bin (512 KB, bank 4 replaced)
    make builds     # bank as ../Builds/C1571_DOLPHINDOS26.bin (with MD5)

The reconstruction itself is byte-identical at tag `referenz-2026-11-10`
(`src/` must not be overwritten with `make generiere` since then).

## Tests (patched VICE with 1571 Multi-Speeder, GUI)

    tests/t1571.py  <eprom> 3     # C128 mode: LOAD, CDR1/CDW1, RAM disk, BSAVE
    tests/t_d71.py  <eprom> 3     # CDRD/CDWD, CDMD, API side 3 (NOAPI=1 shorter)
    tests/t_c64.py  <eprom> 3     # C64 mode (x128 -go64) with C64DolphinDos26
    tests/t_api.py  <eprom> 3     # API one by one (GO64=1 for C64 mode)
    tests/ms_tools_1571.py build/dd26_1571.bin test_fastcopy.py on
                                  # MS-Tools tests unchanged, x128 -go64 + 1571CR

The bank argument `3` of the test scripts is the VICE count from 0 (= `4@RNROM`).
x128 does not take `-kernal64` (it resets it when loading the C128 kernal);
the tests therefore create their own system folder (`-directory`) in which the
default name points to `C64DolphinDos26.bin`.
