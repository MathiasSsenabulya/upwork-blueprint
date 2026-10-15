#!/usr/bin/env python3
"""The gate for profile.md, the draft /profile writes, checked before a member pastes it.

    python3 code/profile_draft.py check profile.md [--proof context/me.md]

It passes only when the draft clears the audit's mechanical checks, lands on
Upwork's form, and every number in it can be found
in the member's evidence sections. That last one is the point: a number nobody can
back up gets exposed on the first call.
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import profile_checks as pc  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import context_check
# Upwork cuts a title at 70 characters: a real profile's title came back from the
# connector cut off at exactly 70 (measured 12 September 2026).
TITLE_MAX = 70
# Upwork's overview field limit, as its form states it.
OVERVIEW_MAX = 5000
SKILLS_MAX = 20
# The three role models set a ceiling, not a target to hit: a draft may run up to 20 %
# over their average length and shorter is always fine.
CEILING = 1.2
# Checks that read fields a draft does not contain.
NOT_FOR_DRAFTS = {'certificates', 'rate_set', 'complete'}
# Plain copy converts: pages at a grade 5 to 7 reading level convert at about twice
# the rate of professional-level writing (references/persuasion.md, section 5), so the
# overview stays under grade 7 and inside the length its five parts need.
GRADE_MAX = 7.0
OVERVIEW_WORDS = 220
# The shortest recorded risk reversal that counts as a guarantee sentence.
PROMISE_WORDS = 6


def syllables(word):
    """Close enough for a reading grade: vowel groups, less a silent final e."""
    word = word.lower()
    groups = len(re.findall(r'[aeiouy]+', word))
    if groups > 1 and word.endswith('e') and not word.endswith(('le', 'ee')):
        groups -= 1
    return max(1, groups)


def reading_grade(text, known=()):
    """The Flesch-Kincaid grade of a text, with each line and sentence counted once.

    Figures are left out, and a word from the member's own skills list counts as one
    syllable: a tool name the client typed into the search box is their vocabulary,
    not a hard word, and without this every profile naming Google Analytics fails.
    """
    known = {w.lower() for name in known for w in re.findall(r"[A-Za-z']+", name)}
    text = re.sub(r'[$€£]?\d[\d.,]*%?', ' ', text)
    sentences = [s for s in re.split(r'[.!?:]+|\n+', text) if re.search(r'[A-Za-z]', s)]
    words = re.findall(r"[A-Za-z']+", text)
    if not sentences or not words:
        return 0.0
    total = sum(1 if w.lower() in known else syllables(w) for w in words)
    return 0.39 * len(words) / len(sentences) + 11.8 * total / len(words) - 15.59


def section(text, name):
    m = re.search(rf'^## {re.escape(name)}\b[^\n]*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return m.group(1) if m else ''


def fenced(block):
    m = re.search(r'```[a-z]*\n(.*?)\n```', block, re.S)
    return m.group(1).strip() if m else ''


def items(block):
    return [re.sub(r'\s*\(was:.*\)\s*$', '', l[2:].strip())
            for l in block.splitlines() if l.startswith('- ')]


def reference_averages(text):
    """`- overview: 1850` lines under `## Reference averages`, in characters. Empty without the section."""
    found = {}
    for line in section(text, 'Reference averages').splitlines():
        m = re.match(r'-\s*(title|overview)\s*:\s*(\d+)', line.strip(), re.I)
        if m:
            found[m.group(1).lower()] = int(m.group(2))
    return found


def parse(text):
    portfolio = items(section(text, 'Portfolio titles'))
    return {
        'averages': reference_averages(text),
        'name': '', 'title': fenced(section(text, 'Title')),
        'overview': fenced(section(text, 'Overview')), 'rate': None,
        'video': (fenced(section(text, 'Video script')) or section(text, 'Video script')).strip(),
        'skills': items(section(text, 'Skills')), 'employment': [], 'education': [],
        'languages': [], 'aggregates': {}, 'portfolio': portfolio or None, 'certificates': None,
    }


def recorded_promise(me_text: str | None = None) -> str:
    """The member's own risk reversal, when it carries a figure ("a 2x return or you do not pay").

    That figure is a promise they picked in /profile, not a result to prove, so the
    number check takes the recorded sentence out first. Only that sentence, word for
    word: the same figure anywhere else in a draft still needs its evidence.
    """
    if me_text is None:
        me_text = context_check.ME.read_text(encoding='utf-8') if context_check.ME.is_file() else ''
    promise = context_check.field(me_text, 'Risk reversal you offer') or ''
    # A sentence, not a bare figure: "100%" alone would wave through every 100% in a draft.
    whole = len(promise.split()) >= PROMISE_WORDS
    return promise if whole and pc.RESULT_NUMBER.search(promise) else ''


def unproven_numbers(draft, proof_text, promise=None):
    """Every result number in title, overview and portfolio titles the evidence lacks."""
    missing = set()
    promise = recorded_promise() if promise is None else promise
    proof_text = context_check.usable_proof(proof_text)
    proven = {re.search(r'\d[\d.,]*', match.group(0)).group(0).rstrip('.,')
              for match in pc.RESULT_NUMBER.finditer(proof_text)}
    for text in [draft['title'], draft['overview'], draft.get('video', '')] + (draft['portfolio'] or []):
        if promise:
            # Once, and with a space, so the cut cannot join two figures into a new one.
            text = text.replace(promise, ' ', 1)
        for m in pc.RESULT_NUMBER.finditer(text):
            core = re.search(r'\d[\d.,]*', m.group(0)).group(0).rstrip('.,')
            if core not in proven:
                missing.add(m.group(0).strip())
    return sorted(missing)


def problems(draft, proof_text, promise=None):
    found = []
    if not draft['title']:
        found.append('no title in a fenced block under "## Title"')
    if not draft['overview']:
        found.append('no overview in a fenced block under "## Overview"')
    if found:
        return found

    skip = set(NOT_FOR_DRAFTS)
    # Portfolio count and numbers are a live-profile recommendation. The draft only
    # retitles projects, so it never fails on them.
    skip |= {'portfolio'}
    # A first profile has no verified result, and the command tells it to lead with
    # the offer and the background instead of a number. Demanding a number anyway
    # left exactly one way out, inventing one, which the next check would catch and
    # the client would not. Only a verified result number switches these checks
    # on; pending entries and bare certificate years cannot supply a result.
    verified = context_check.verified_proof(proof_text)
    if not pc.RESULT_NUMBER.search(verified):
        skip |= {'opening_has_number', 'results_with_numbers'}
    # Three result lines are a recommendation. A member with fewer verified results
    # than that cannot be failed for it, so the check applies only from three.
    elif len(pc.RESULT_NUMBER.findall(verified)) < 3:
        skip |= {'results_with_numbers'}
    for r in pc.run_checks(draft):
        if r['id'] not in skip and not r['passed']:
            found.append(f'{r["label"]}: {r["detail"]}')

    if len(draft['title']) > TITLE_MAX:
        found.append(f'title is {len(draft["title"])} characters, Upwork cuts at {TITLE_MAX}')
    if len(draft['overview']) > OVERVIEW_MAX:
        found.append(f'overview is {len(draft["overview"])} characters, the field holds {OVERVIEW_MAX}')
    if len(draft['skills']) > SKILLS_MAX:
        found.append(f'{len(draft["skills"])} skills, Upwork takes {SKILLS_MAX}')
    for field, average in draft.get('averages', {}).items():
        if average and len(draft[field]) > average * CEILING:
            found.append(f'{field} is {len(draft[field])} characters, the role models average {average}: '
                         f'stay under {round(average * CEILING)}')
    if re.search(r'\*\*|^#', draft['overview'], re.M):
        found.append('overview uses markdown, which Upwork shows as raw symbols')
    grade = reading_grade(draft['overview'], draft['skills'])
    if grade >= GRADE_MAX:
        found.append(f'overview reads at grade {grade:.1f}: get it under {GRADE_MAX:g} with shorter '
                     'sentences and plainer words')
    words = len(draft['overview'].split())
    if words > OVERVIEW_WORDS:
        found.append(f'overview is {words} words: its five parts fit in {OVERVIEW_WORDS}, and shorter is better')
    for field in ('title', 'overview', 'video'):
        if chr(0x2014) in draft[field]:  # the em-dash, written so this file carries none
            found.append(f'{field} has an em-dash')

    for n in unproven_numbers(draft, proof_text, promise):
        found.append(f'"{n}" is not in the evidence sections of context/me.md: prove it there or cut it')

    return found


def cmd_check(args):
    draft = parse(pathlib.Path(args.file).read_text(encoding='utf-8'))
    proof = pathlib.Path(args.proof)
    me_text = proof.read_text(encoding='utf-8') if proof.is_file() else ''
    # Only the evidence sections. Handed the whole file, every number in it would
    # count as a source, and an hourly rate of 40 would prove a claim of 40%.
    proof_text = context_check.proof_only(me_text)
    promise = recorded_promise(me_text)
    if args.only == 'video':
        # The script generator writes only `## Video script`, so a missing title and
        # overview are not problems here: the numbers and the em-dash are what is checked.
        found = []
        if not draft['video']:
            found.append('no "## Video script" section')
        else:
            if chr(0x2014) in draft['video']:
                found.append('video script has an em-dash')
            for n in unproven_numbers(dict(draft, title='', overview='', portfolio=None), proof_text, promise):
                found.append(f'"{n}" is not in the evidence sections of context/me.md: prove it there or cut it')
        for f in found:
            print(f'FAIL  {f}')
        print(f'\n{"PASS" if not found else f"{len(found)} problem(s)."}  video script {len(draft["video"].split())} words')
        return 1 if found else 0
    found = problems(draft, proof_text, promise)
    for f in found:
        print(f'FAIL  {f}')
    print(f'\n{"PASS" if not found else f"{len(found)} problem(s)."}  '
          f'title {len(draft["title"])} characters, overview {len(draft["overview"].split())} words '
          f'at reading grade {reading_grade(draft["overview"], draft["skills"]):.1f}, '
          f'{len(draft["skills"])} skills')
    return 1 if found else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('check')
    p.add_argument('file')
    p.add_argument('--proof', default=str(ROOT / 'context' / 'me.md'))
    p.add_argument('--only', choices=('video',), help='check only the video script, for /profile video')
    p.set_defaults(func=cmd_check)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
