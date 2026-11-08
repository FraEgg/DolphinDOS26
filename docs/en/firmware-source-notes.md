# DolphinDos26 – Source code

Commented ca65 source code of DolphinDos26 for the 1541 Switchless
Multi-Speeder V3 DD3 (512 KB). DolphinDos26 is the further development of the
firmware `1541DolphinDos25.bin` (26 = year 2026). The unchanged DolphinDos25
state builds byte-identically to the original (tag `referenz-2026-10-27`).
Power-on message: `73, DOLPHINDOS26 1541`.

The firmware sits in the last 64 KB bank of the EPROM (bank 8, `8@RNROM`,
EPROM offset `$70000`). In the image, the offset corresponds to the CPU address.
The banks are counted from 1 here, as with `@RNROM` (bank 1 = CBM DOS at `$00000`,
bank 8 = DolphinDos26 at `$70000`); `tools/rom.py` and its output count from 0
internally and therefore call the same bank "bank 7".

## Building

    make            # builds build/dd26.bin and compares it with ref/1541DolphinDos25.bin
    make B=tmp/x    # into a different build directory

    make rom        # additionally the 512 KB EPROM image for the Multi-Speeder
    make builds     # build both and copy to ../Builds

`make rom` takes the reference EPROM
`ref/AM27C040-…+7DolphinDos25_v3.3.bin` (MD5
`86ca5649c56219aeeff1dc6b7768eb35`), keeps banks 1–7 unchanged and
replaces bank 8 (`$70000`) with the build. Result:
`build/AM27C040-…+7DolphinDos26_v3.3.bin`.

`make builds` places the finished ROMs in the project directory `../Builds`:
`1541DolphinDos26.bin` (64 KB, bank 8), the 512 KB EPROM image,
`C1541_DOLPHINDOS26UL.bin` and `C1541_DOLPHINDOS26DD2.bin` (see below). Existing files there are
overwritten (`make builds BUILDS=…` for a different target).

## DolphinDos26DD2 (Multi-Speeder V3 with SpeedDOS parallel cable)

`make dd2` builds `build/dd26dd2.bin`, `make builds` places it as
`C1541_DOLPHINDOS26DD2.bin` (64 KB) next to `C1541_DOLPHINDOS26UL.bin`. It
replaces `1541DolphinDos26.bin` as bank 8 of the Multi-Speeder EPROM (`$70000`).

- Parallel cable like DolphinDos26UL (SpeedDOS style, data `$1801`, handshake
  CB1/CA2; `-D DD26VIA`), so compatible with programs for this cable.
- All functions of `1541DolphinDos26.bin`: MS-Addon, `CDR`/`CDW`/`CDM`,
  MS-Addon API; XQ/XZ from the RAM disk also run over the cable.
- The PIA now only switches the RAM banks (port B). Every reset (including `UJ`)
  sets port A (`DDRA=0`) and CA2 (`CRA=4`) to input, so the lines may run
  1:1 parallel to the cable.
- Power-on message `73, DOLPHINDOS26  DD2` (same length as `1541`).
- Cold start like UL, but with the signature `$A5 $5A` in `$60ED` (`$60F0` is
  `ms_trks` here). `UJ` keeps settings and RAM disk.
- MS-NIBCOPY512 needs at least build 48. Older builds find the PIA and
  send there; on the DD2 ROM they report `NO ANSWER FROM DRIVE CODE`.

Test: `tests/test_dd2.py`.

## DolphinDos26UL (C64 Ultimate / simple DolphinDOS 3)

    make ul         # builds build/dd26ul.bin (32 KB, $8000-$FFFF)

`C1541_DOLPHINDOS26UL.bin` is the firmware for the disk drive in the
Commodore C64 Ultimate (C64U): 8 KB of additional RAM at `$6000–$7FFF` and a
**parallel cable on VIA1** (SpeedDOS style like DolphinDOS 2.0, data `$1801`,
handshake CB1/CA2), without 6821 PIA, without Multi-Speeder RAM banks and without
MS-Addon at `$3000–$3FFF`. The C64U does not emulate a DolphinDOS 3 cable (PIA at
`$5000`), only the VIA parallel cable. The C64U loads a 1541 ROM of
exactly 16 or 32 KB to `$8000–$FFFF`; this ROM is 32 KB.

- DOS and DolphinDOS come from the same sources as `1541DolphinDos26.bin`,
  assembled with `-D DD26UL -D DD26VIA`: power-on message `73, DOLPHINDOS26 C64U` and
  parallel routines for the VIA1 cable (cable detection, single bytes, XQ/XZ
  block transfer, port reset in reset and idle loop; taken from
  `../DolphinDos2`). Without `DD26VIA`, the PIA code is produced unchanged; the
  C64 side (kernal) is the same for both cables. Instead of the
  MS-Addon, `addon/ul.s` is linked from `$8000` (`dd26ul.cfg`): the
  original sequences for `setjob`, `format`, `job_write`, XQ/XZ as well as the
  fast routines from `addon/fast.s` (GCR decoding, buffer copy).
- Not included: `CDR`/`CDW`/`CDM` (→ `31 SYNTAX ERROR`), RAM disk,
  MS-Addon API (MS-Tools do not run with it).
- Cold start: if the signature `$A5 $5A` is missing at `$60F0`, `$6000–$60FF`
  are cleared (all switches on, track count automatic) and 35 tracks are set.
  On the C64U, the drive RAM is not cleared after power-on (e.g.
  `$12` at `$6003` would switch off parallel operation). A drive reset
  (`UJ`) keeps the settings.
- Test in VICE (without Multi-Speeder, standard parallel cable): `-dos1541
  build/dd26ul.bin -drive8ram6000 -parallel8 1`, automated:
  `tests/test_ul.py` (`MS_PORT` = different monitor port for parallel
  VICE runs).

Requires cc65 (ca65/ld65) and Python 3 (only for the comparison).

## Structure

| File | Range | Contents |
|---|---|---|
| `addon/addon.s` | `$3000–$3BFF` | MS-Addon: `CDR`/`CDW` (disk ↔ 512 KB RAM), RAM disk `CDM`, XQ/XZ from RAM |
| `addon/addon.s` | `$3FC0–$3FFF` | MS-Addon API: jump table from `$3FFF` downwards (see below) |
| `dolphin/dolphin_a.s` | `$A000–$AFFF` | DolphinDOS: jump table, track cache, jobs, parallel transfer, X commands |
| `dolphin/dolphin_b.s` | `$B000–$BFFF` | GCR tables (generated by macro), lock/unlock messages, stpout hook |
| `dos/*.s` | `$C000–$FFFF` | CBM DOS 901229-05 (mist64/dos1541) with the DD25 patches, marked with `; DD25:` |
| `dos/dd25ext.s` | – | constants for entry points into DolphinDOS/Addon, PIA, DD variables `$6000+` |
| `include/dos05.inc` | – | DOS symbols for the separate translation units |
| `dd25.cfg` | – | linker configuration (64 KB bank) |
| `tools/vergleich.py` | – | byte-by-byte comparison with the reference |
| `tools/rom.py` | – | inserts a bank into the 512 KB reference EPROM |
| `addon/fast.s` | – | fast GCR decoding/buffer copy (included by `addon.s` and `ul.s`) |
| `addon/ul.s` | `$8000–$82FF` | DolphinDos26UL only: replacement for the MS-Addon, cold start presets |
| `dd26ul.cfg` | – | linker configuration DolphinDos26UL (32 KB) |

The original English Commodore comments are retained. All
DD25 changes and the new code are commented in German. Uncertain
interpretations are marked with "(vermutlich)" ("presumably").

## Notes

- DolphinDOS uses illegal NMOS 6502 opcodes (`.setcpu "6502X"`).
- RAM banks: the bank number is written to DDRB (`$5002`) when CRB bit 2 = 0.
  Because of the pull-ups on PB0–5: logical bank n = physical
  bank 63−n. Logical bank 0 is the working RAM of DolphinDOS.
- There are no longer any ROM checksums: DD25 does not evaluate them on reset.

## MS-Addon API (for C64 programs)

Fixed entry points at the end of the Addon area, from `$3FFF` downwards. The
addresses stay the same even when the Addon's code changes; new
entry points are added at the bottom (E7 = `$3FE4` …). A later
version (e.g. for the 1571) provides the same table.

| Address | Contents |
|---|---|
| `$3FFF` | API version (1) |
| `$3FFE` | number of entry points (7) |
| `$3FFC` | signature `"MS"` |
| `$3FF9` | E0 `OPEN` (side 1/2, direction 0 = read / 1 = write, verify 0 = off / 1 = on / 2 = XV as configured). Writing a 40-track side: the target is checked as with `CDW` (`66`, `21`, `29`) |
| `$3FF6` | E1 `TRACK` (track 1–40): read or write one track, RAM location as with `CDR1`/`CDR2` |
| `$3FF3` | E2 `CLOSE` (track count 35/40, remembered on read for `CDW` and `INFO`; on write, the last track is written back) |
| `$3FF0` | E3 `PROBE` (track): seek job, `00` = header with the disk's ID found, different ID: `29` |
| `$3FED` | E4 `INFO`: message `00, OK,t1,t2` = track count of side 1 and 2 |
| `$3FEA` | E5 `ABORT`: clean up after an error (discard cache, XR/XV/write-back as before `OPEN`) |
| `$3FE7` | E6 `SECTOR` (side 1/2, track, sector): copy a sector from RAM to the DOS buffer `$0300`, then read it via `M-R` (e.g. BAM 18/0 for disk name and ID) |

Call: `"M-E" <lo> <hi> <p1> <p2> <p3>` on channel 15, the parameters are
at `cmdbuf+5` onwards. As with every command, the result is in the error channel
(`00, OK,00,00` or e.g. `23,READ ERROR,17,05`). Programs first check
the signature and version via `M-R` from `$3FFC`. Example: MS-FASTCOPY512.
