#!/usr/bin/env python3
"""The one page a client reads after the call: eight short parts, each answering one question.

    python3 code/proposal_generate.py <job id> --file proposal.json
    python3 code/proposal_generate.py <job id> --file -        # JSON on stdin

Writes jobs/<id>/proposal.html from templates/proposal/template.html, then prints that
page to jobs/<id>/proposal.pdf with Chrome. The markdown proposal stays the thing the
member pastes into Upwork chat, and the PDF is the file they attach beside it. The
member delivers both themselves: nothing here hosts or sends them.

It is one page. A PDF that runs past it fails the run, and the fix is fewer words.

Every part the call did not settle is rendered as a visible "open" marker, never as a
zero and never as a rounded guess: a missing number is honest, an invented one is a claim
the first milestone exposes.

The JSON, all strings unless noted:

    member, client, title, date,
    video (object, optional: url, title, note, length),
    problem, deliverable, worth, timeline, cost, tools, proof, next_steps
        (each one line, or an object {line, items} with a short list under it),
    labels (object, optional, overrides a part's label or the "for" lead by key)
"""
import argparse
import datetime
import html
import json
import pathlib
import re
import subprocess
import sys
from pipeline import jobs_dir, shown

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'templates' / 'proposal' / 'template.html'
OPEN = '<span class="missing">open</span>'
# The anatomy in reading order: the key in the JSON, the label on the page, and beside
# it the question the client is already asking when they reach that part.
PARTS = (
    ('problem', 'The problem'),         # what is wrong?
    ('deliverable', 'What you get'),    # what do I get?
    ('worth', "What it's worth"),       # what is it worth?
    ('timeline', 'Timeline'),           # by when?
    ('cost', 'Cost'),                   # how much?
    ('tools', 'Tools'),                 # running on what?
    ('proof', 'Proof'),                 # why you?
    ('next_steps', 'Next steps'),       # what now?
)


def abort(message):
    print(f'ABORT: {message}', file=sys.stderr)
    raise SystemExit(1)


def esc(value):
    return html.escape(str(value), quote=True)


def value(raw):
    """A filled value, or the open marker when the call did not settle it."""
    text = str(raw or '').strip()
    return esc(text) if text else OPEN


def part(index: int, label: str, raw) -> str:
    """One of the eight parts: its label, the line that answers it, a short list at most."""
    line, items = (raw.get('line'), raw.get('items') or []) if isinstance(raw, dict) else (raw, [])
    if not isinstance(line, (str, type(None))) or not isinstance(items, list):
        abort(f'"{label}" takes one line of text, or an object with "line" and a list of "items".')
    listed = ('<ul class="items">' + ''.join(f'<li>{value(item)}</li>' for item in items) + '</ul>'
              if items else '')
    return (f'<section class="part"><p class="label"><span class="n">{index}</span>{esc(label)}</p>'
            f'<div><p class="line">{value(line)}</p>{listed}</div></section>')


def video(raw) -> str:
    """The optional walkthrough: one card linking the member's own recording, or nothing."""
    if not raw:
        return ''
    import application_check  # noqa: E402  (same folder, imported where it is used)
    raw = raw if isinstance(raw, dict) else {}
    href = str(raw.get('url') or '').strip()
    # Only a Loom or YouTube link is a video. Any other address on a page that goes to a
    # client before a contract is a way off Upwork.
    if not href.startswith('https://') or any(c.isspace() for c in href) \
            or not application_check.has_video(href):
        abort('video needs a "url" that is a Loom share link or a YouTube link. Leave the '
              'video out otherwise: the page works without it.')
    note, length = (str(raw.get(key) or '').strip() for key in ('note', 'length'))
    return (f'<a class="video" href="{esc(href)}"><i class="play"></i><span class="vtext">'
            f'<b>{value(raw.get("title"))}</b>' + (f'<span>{esc(note)}</span>' if note else '')
            + '</span>' + (f'<span class="vlen">{esc(length)}</span>' if length else '') + '</a>')


def build_page(data: dict, lang: str = 'en') -> str:
    """The template with every marker filled. Aborts when the two have drifted apart."""
    if not TEMPLATE.is_file():
        abort(f'template missing: {TEMPLATE}')
    custom = data.get('labels') or {}
    if not isinstance(custom, dict):
        abort('"labels" is an object: a part key, or "for", and the text to show instead.')
    labels = {'for': 'Proposal for', **dict(PARTS), **{k: v for k, v in custom.items() if v}}
    today = datetime.date.today()
    fields = {
        '{{LANG}}': esc(lang),
        '{{DOC_TITLE}}': esc(str(data.get('title') or '').strip() or 'Proposal'),
        '{{TITLE}}': value(data.get('title')),
        '{{FOR}}': esc(labels['for']),
        '{{CLIENT}}': value(data.get('client')),
        # today is a fact, not a commitment: the day the page was prepared is true whether
        # or not the call settled anything, so this one keeps its default.
        '{{DATE}}': esc(str(data.get('date') or '').strip() or f'{today:%a %b} {today.day}'),
        '{{MEMBER}}': value(data.get('member')),
        '{{VIDEO}}': video(data.get('video')),
        '{{PARTS}}': '\n    '.join(part(index, labels[key], data.get(key))
                                   for index, (key, _) in enumerate(PARTS, 1)),
    }
    template = TEMPLATE.read_text(encoding='utf-8')
    marker = re.compile(r'\{\{[A-Z_]+\}\}')
    if set(marker.findall(template)) != set(fields):
        abort('the template and the field list hold different markers; the two drifted.')
    # One pass: a value that happens to read like a marker stays the text it is.
    return marker.sub(lambda found: fields[found.group(0)], template)


def pdf_complete(data: bytes) -> bool:
    """True for a PDF Chrome finished: the header at its start and the end marker at its end."""
    return data.startswith(b'%PDF-') and data.rstrip().endswith(b'%%EOF')


def pdf_pages(data: bytes) -> int:
    """The page count a finished PDF shows in plain sight. Zero when it shows none.

    A PDF that packs its page objects into compressed streams is still a finished PDF,
    so the count never decides whether the file is kept, only whether it is one page.
    """
    return len(re.findall(rb'/Type\s*/Page\b', data)) if pdf_complete(data) else 0


def write_pdf(page: pathlib.Path, out: pathlib.Path) -> str:
    """Prints the page to a PDF with Chrome. Returns '' when it worked, else the reason.

    The PDF is the file a client saves and forwards, so it is printed from the page the
    gate reads and cannot say anything else. An earlier PDF goes first: old terms beside
    a new page are worse than no PDF at all.
    """
    from proposal_illustrate import chrome_binary  # same folder, imported where it is used
    out.unlink(missing_ok=True)
    chrome = chrome_binary()
    if not chrome:
        return 'Chrome or Chromium is not installed. Set CHROME_BIN if it lives somewhere this cannot find.'
    try:
        # Both spellings of the switch: without it an older Chrome prints the file path
        # and the date into the margin of a document that goes to a client. No profile
        # folder either: with one, Chrome writes the file and then never exits.
        subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                        '--print-to-pdf-no-header', f'--print-to-pdf={out.resolve()}',
                        page.resolve().as_uri()], capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        pass  # the file decides below: a hung Chrome may still have finished it
    except OSError as error:
        return f'Chrome could not be started: {error}.'
    if not out.is_file() or not pdf_complete(out.read_bytes()):
        out.unlink(missing_ok=True)
        return 'Chrome did not finish the PDF.'
    return ''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('job_id')
    parser.add_argument('--file', required=True, help='JSON file, or - for stdin')
    parser.add_argument('--lang', default='en')
    args = parser.parse_args(argv)

    raw = sys.stdin.read() if args.file == '-' else pathlib.Path(args.file).read_text(encoding='utf-8')
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        abort(f'the proposal JSON does not parse: {error}')
    if not isinstance(data, dict):
        abort('the proposal JSON is one object with the fields this script lists.')

    page = build_page(data, args.lang)
    out = jobs_dir() / args.job_id / 'proposal.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    opens = page.count('class="missing"')
    print(f'{shown(out)} written, {opens} value(s) still open.')
    pdf = out.with_suffix('.pdf')
    problem = write_pdf(out, pdf)
    if problem:
        print(f'PDF not written: {problem} The page itself is complete: open it in a browser '
              'and print it to PDF.', file=sys.stderr)
        return 1
    count = pdf_pages(pdf.read_bytes())
    if count > 1:
        print(f'{shown(pdf)} runs to {count} pages. It is one page: cut words until it fits, '
              'then run this again.', file=sys.stderr)
        return 1
    print(f'{shown(pdf)} written{", 1 page" if count else ""}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
