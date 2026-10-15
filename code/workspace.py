#!/usr/bin/env python3
"""Copies missing starters and appends new empty fields to the member's me.md.

Every command runs this first. Everything it creates is gitignored, so it is
the member's alone: `git pull` updates the machinery and never touches their
files. Existing answers are never overwritten, so running it twice is safe.

    python3 code/workspace.py
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STARTERS = ROOT / 'starters'


def ensure(root=ROOT, starters=STARTERS):
    """Copies every starter whose target does not exist yet. Returns what it created."""
    created = []
    (root / 'data').mkdir(exist_ok=True)  # the live profile and job files land here
    for source in sorted(p for p in starters.rglob('*') if p.is_file()):
        relative = source.relative_to(starters)
        # Shipped tool knowledge stays current. A member's explicit local copy
        # takes precedence, but setup does not freeze one on their behalf.
        if relative.parts[:2] == ('context', 'tool-knowledge'):
            continue
        target = root / relative
        if target.exists():
            if relative == pathlib.Path('context/me.md'):
                text = target.read_text(encoding='utf-8')
                fields = re.findall(r'^\*\*([^\n]+?):\*\*[^\n]*',
                                    source.read_text(encoding='utf-8'), re.M)
                missing = [label for label in fields if not re.search(
                    rf'^\*\*{re.escape(label)}:\*\*', text, re.M | re.I)]
                if missing:
                    suffix = '\n\n## Setup fields\n\n' + '\n'.join(
                        f'**{label}:** not answered yet' for label in missing) + '\n'
                    with target.open('a', encoding='utf-8') as handle:
                        handle.write(suffix)
                    created.append(f'{relative} (new empty fields)')
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        created.append(str(relative))
    return created


def main():
    created = ensure()
    if created:
        for rel in created:
            print(f'created {rel}')
        print('\nThese files are yours and gitignored. `git pull` will never touch them.')
    else:
        print('Nothing to create, your files are in place.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
