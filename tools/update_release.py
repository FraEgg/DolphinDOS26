#!/usr/bin/env python3
"""Refresh this release repository from the sibling development folders.

Run from anywhere:  python3 tools/update_release.py [--manuals-en DIR] [--check]

Copies the ROMs, the German manuals (all as PDF in manuals/) and the German notes
into this repository,
extracts the PRGs from the MS-Tools disk, copies that disk, writes CHECKSUMS.md5 and
CHECKSUMS.sha256, and reports what is out of date:

- a German note changed after its English translation was made (docs/en stale);
- an English manual is missing or older than the German one;
- the checksums printed in a manual differ from the ROMs being published.

The script exits with status 1 if anything is out of date, so a release is never
tagged with one language lagging behind. --check only reports and changes nothing.
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent


def find_root(start):
    """Project folder: the first parent with Builds and dd25 (the repository lives in
    Git/DolphinDOS26; this also works from a worktree below .claude/worktrees)."""
    for d in start.parents:
        if (d / 'Builds').is_dir() and (d / 'dd25').is_dir():
            return d
    return start.parent


ROOT = find_root(REPO)
# German development note -> name in docs/de and docs/en, with its git repository
NOTES = {
    'firmware-source-notes.md': ('dd25', 'README.md'),
    'c64-kernal.md': ('C64DD26', 'README.md'),
    'ms-tools.md': ('MS-Tools', 'README.md'),
    'c128-kernal.md': ('C128DD26', 'README.md'),
    'c1571-firmware.md': ('C1571DD26', 'README.md'),
}
ROMS = ['1541DolphinDos26.bin', 'C1541_DOLPHINDOS26UL.bin', 'C1541_DOLPHINDOS26DD2.bin',
        'C64DolphinDos26.bin', 'C64IIDolphinDos26.bin', 'C128DolphinDos26-US.BIN', 'C128DolphinDos26-DE.BIN',
        'C1571_DOLPHINDOS26.bin']
# Every manual goes to manuals/de and manuals/en as PDF (German from Builds,
# English from --manuals-en); new manuals are added here, never to docs/.
MANUALS = {'DolphinDos26_Handbuch.pdf': 'DolphinDos26_Manual.pdf',
           'DolphinDos26UL_Handbuch.pdf': 'DolphinDos26UL_Manual.pdf',
           'JiffyDOS_Handbuch.pdf': 'JiffyDOS_Manual.pdf',
           'MultiSpeederC128DCR-1571_Handbuch.pdf': 'MultiSpeederC128DCR-1571_Manual.pdf'}
# Manuals that state the MD5 checksums of the published ROMs
ROM_MANUALS = ('DolphinDos26_Handbuch.pdf', 'DolphinDos26_Manual.pdf',
               'DolphinDos26UL_Handbuch.pdf', 'DolphinDos26UL_Manual.pdf')
# Every tool on ms-tools.d64 is published; the disk is copied unchanged, so the MD5
# stated in the manuals applies to the published disk as well.
PRGS = ['ms-status', 'ms-memtest512', 'ms-fastcopy512', 'ms-nibcopy512', 'ms-rs232', 'ms-15seccopy']
STAMP = REPO / 'tools' / 'translated-from.json'


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def copy(src, dst, check, problems):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    if not src.exists():
        problems.append('missing source: %s' % src)
        return
    if check:
        if not dst.exists() or sha(src) != sha(dst):
            problems.append('out of date: %s' % dst.relative_to(REPO))
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(ROOT / repo), *args], text=True).strip()


def main():
    global ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument('--manuals-en', help='folder with the English PDFs (default: Builds)')
    ap.add_argument('--check', action='store_true', help='report only, change nothing')
    ap.add_argument('--stamp-translations', action='store_true',
                    help='record the current German notes as translated (after updating docs/en)')
    ap.add_argument('--root', default=str(ROOT), help='project folder with Builds, dd25, C64DD26, C128DD26, C1571DD26, MS-Tools')
    a = ap.parse_args()
    ROOT = pathlib.Path(a.root).resolve()
    BUILDS = ROOT / 'Builds'
    bad = []

    for r in ROMS:
        copy(BUILDS / r, REPO / 'rom' / r, a.check, bad)
    for de, en in MANUALS.items():
        copy(BUILDS / de, REPO / 'manuals' / 'de' / de, a.check, bad)
        src = pathlib.Path(a.manuals_en or BUILDS) / en
        copy(src, REPO / 'manuals' / 'en' / en, a.check, bad)
        if src.exists() and (BUILDS / de).exists() and src.stat().st_mtime < (BUILDS / de).stat().st_mtime:
            bad.append('English manual older than German one: %s' % en)

    d64 = ROOT / 'MS-Tools' / 'ms-tools.d64'
    copy(BUILDS / 'RS232DRV-9800.prg', REPO / 'ms-tools' / 'prg' / 'RS232DRV-9800.prg', a.check, bad)
    with tempfile.TemporaryDirectory() as t:
        for name in PRGS:
            out = pathlib.Path(t) / (name + '.prg')
            subprocess.run(['c1541', str(d64), '-read', name, str(out)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            copy(out, REPO / 'ms-tools' / 'prg' / (name.upper() + '.prg'), a.check, bad)
    copy(d64, REPO / 'ms-tools' / 'ms-tools.d64', a.check, bad)

    # MS-15SECCOPY is also published on its own disk from its own development folder
    b15 = ROOT / '15SecCopy' / 'neu' / 'build'
    copy(b15 / 'ms-15seccopy.d64', REPO / 'ms-tools' / 'ms-15seccopy.d64', a.check, bad)

    stamps = json.loads(STAMP.read_text()) if STAMP.exists() else {}
    for name, (repo, path) in NOTES.items():
        copy(ROOT / repo / path, REPO / 'docs' / 'de' / name, a.check, bad)
        now = sha(ROOT / repo / path)
        if a.stamp_translations:
            stamps[name] = now
        elif stamps.get(name) != now:
            bad.append('translation stale: docs/en/%s (German source %s/%s changed)' % (name, repo, path))
        if not (REPO / 'docs' / 'en' / name).exists():
            bad.append('missing translation: docs/en/%s' % name)
    if a.stamp_translations:
        STAMP.write_text(json.dumps(stamps, indent=2, sort_keys=True) + '\n')

    # Every manual must name the checksums of exactly the files published here.
    texts = {}
    for lang_dir in ('de', 'en'):
        for pdf in (REPO / 'manuals' / lang_dir).glob('*.pdf'):
            if pdf.name not in ROM_MANUALS:
                continue
            try:
                texts[pdf] = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
            except (OSError, subprocess.CalledProcessError) as e:
                bad.append('cannot read %s: %s' % (pdf.name, e))
    for pdf, txt in texts.items():
        flat = re.sub(r'\s+', '', txt)
        files = ['C64DolphinDos26.bin', 'C1541_DOLPHINDOS26UL.bin']
        if 'UL' not in pdf.name:
            files += ['1541DolphinDos26.bin', 'C64IIDolphinDos26.bin', 'C128DolphinDos26-US.BIN', 'C128DolphinDos26-DE.BIN',
                      'C1571_DOLPHINDOS26.bin']
        for f in [REPO / 'rom' / x for x in files]:
            # table cells wrap long checksums in the PDF text, so compare the first 16 digits
            if f.exists() and hashlib.md5(f.read_bytes()).hexdigest()[:16] not in flat:
                bad.append('%s does not state the MD5 of %s' % (pdf.name, f.name))

    if not a.check:
        files = sorted(p for d in ('rom', 'ms-tools', 'manuals') for p in (REPO / d).rglob('*') if p.is_file())
        for algo, out in (('md5', 'CHECKSUMS.md5'), ('sha256', 'CHECKSUMS.sha256')):
            lines = ['%s  %s' % (hashlib.new(algo, f.read_bytes()).hexdigest(), f.relative_to(REPO).as_posix())
                     for f in files]
            (REPO / out).write_text('\n'.join(lines) + '\n')

    for x in bad:
        print('PROBLEM:', x)
    print('%d problem(s)' % len(bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
