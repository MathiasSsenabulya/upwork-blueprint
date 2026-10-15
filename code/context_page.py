#!/usr/bin/env python3
"""The member's one-page Upwork resume, built from their own file.

    python3 code/context_page.py [--open]

/about-me ends by reporting what it wrote. A report in a terminal scrolls away,
and the file it wrote is markdown with starter lines still in it. This renders
`context/me.md` as a resume: initials, name and headline on top, the member's own
totals as a row of large figures, selected results as cards, then experience
with services, tools, credentials and recommendations beside it. Only what a client would care about is on the sheet: internal limits
such as the smallest project or applications a day stay in the file, and what is
still open sits in a note under it.

An entry carries a label only when it was pulled from somewhere else (a file, an
email, the web) and the member has not confirmed it yet. What they said
themselves is simply theirs.

Output is `context/overview.html`, which is gitignored like everything else in
that folder. It is built from the files alone and reaches no service. The look
comes from `website/app/tokens.css`, the tokens every dashboard here shares. The
sheet prints as a clean A4 resume, without the note under it.
"""
import argparse
import html
import pathlib
import re
import sys
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
import context_check as cc  # noqa: E402

OUT = ROOT / 'context' / 'overview.html'
TOKENS = ROOT / 'website' / 'app' / 'tokens.css'
STARTER = 'not answered yet'
EMPTY = ('nothing recorded yet', 'not filled in yet', STARTER)
CLIP = 260       # characters of a long answer before it is cut at a word
JOBS = 5         # experience entries shown, the rest become "and N more"
RESULTS = 6      # results shown on the sheet
CREDENTIALS = 6  # credentials shown beside them
PILLS = 14       # tool names shown as pills
# The totals the proof interview asks for, and what each is called on the sheet.
FIGURES = (('Years of experience', 'years of experience'), ('Projects completed', 'projects completed'),
           ('Hours saved', 'hours saved for clients'), ('Money earned', 'earned or saved for clients'),
           ('People helped', 'people helped'))
NUMBER_WORDS = {word: number for number, word in enumerate(
    'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen '
    'sixteen seventeen eighteen nineteen twenty'.split(), start=1)}
# How /about-me writes the source of something the member said themselves. It needs no label.
OWN_WORDS = ('your answer', 'your own', 'you said', 'you told')
INTERNAL = ('Applications per day', 'Smallest project', 'What you do NOT', 'Hourly rate',
            'Maximum proposals', 'Lowest share', 'Industries', 'Proof to build', 'Risk reversal', 'Follow-up days', 'Unverified clients', 'Full-time roles',
            'Oldest posting', 'Lowest client rating', 'Standard proposal video', 'Clients folder', 'Days a week')

# A resume on the house tokens: a parchment page, one ivory sheet, a serif for the
# name and headings, a small mono for section labels, terracotta for the rules.
CSS = """
  * { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { margin: 0; background: var(--canvas); color: var(--ink); font: 15px/1.6 var(--sans);
         -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
  .bar, .sheet, .note, .foot { max-width: 1000px; margin-left: auto; margin-right: auto; }
  .bar { display: flex; align-items: center; justify-content: space-between; padding: 36px 6px 18px; }
  .bar span { font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: .25em; color: var(--label); }
  .bar button { font: 500 13px/1 var(--sans); padding: 9px 18px; border-radius: 999px; cursor: pointer;
                border: 1px solid var(--hairline-soft); background: var(--ivory); color: var(--body); }
  .bar button:hover { background: var(--paper); color: var(--ink); }
  .bar button:focus-visible { outline: 2px solid var(--terracotta-text); outline-offset: 2px; }

  .sheet { position: relative; overflow: hidden; background: var(--ivory); border: 1px solid var(--hairline-soft);
           border-radius: 20px; box-shadow: 0 1px 2px rgba(20, 20, 19, .04), 0 24px 60px -30px rgba(20, 20, 19, .18);
           padding: 60px 64px 52px; }
  .sheet::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--terracotta); }
  .kicker, h2, .when, .tag, .figure span, .result .who, .chip i { font-family: var(--mono); text-transform: uppercase; font-weight: 400; font-style: normal; }

  .id { display: grid; grid-template-columns: auto 1fr; gap: 26px; align-items: center; }
  .monogram { width: 84px; height: 84px; border-radius: 50%; display: grid; place-items: center;
              background: var(--terracotta-soft); color: var(--terracotta-text);
              font: 500 30px/1 var(--display); letter-spacing: -.5px; box-shadow: inset 0 0 0 1px rgba(201, 100, 66, .22); }
  .kicker { font-size: 10.5px; letter-spacing: 2.2px; color: var(--terracotta-active); margin: 0 0 10px; }
  h1 { font: 500 clamp(38px, 5.4vw, 58px)/1 var(--display); letter-spacing: -1.6px; margin: 0; text-wrap: balance; }
  .headline { font-size: 19px; line-height: 1.4; color: var(--body); margin: 12px 0 0; max-width: 34em; text-wrap: balance; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 26px 0 0; padding: 0; list-style: none; }
  .chip { display: inline-flex; align-items: baseline; gap: 8px; padding: 6px 12px; border-radius: 8px;
          background: var(--paper); box-shadow: 0 0 0 1px var(--hairline-soft); font-size: 13px; font-weight: 600; color: var(--ink); }
  .chip i { font-size: 9.5px; letter-spacing: 1.4px; color: var(--label); }

  .summary { position: relative; margin: 40px 0 0; padding: 0 0 0 46px; max-width: 40em;
             font: 400 22px/1.45 var(--display); letter-spacing: -.2px; text-wrap: pretty; }
  .summary::before { content: "“"; position: absolute; left: -4px; top: -14px;
                     font: 500 76px/1 var(--display); color: var(--terracotta); }

  .figures { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin: 40px 0 0;
             border-top: 1px solid var(--hairline-soft); border-bottom: 1px solid var(--hairline-soft); }
  .figure { padding: 22px 22px 20px; border-left: 1px solid var(--hairline); }
  .figure:first-child { border-left: 0; padding-left: 0; }
  .figure strong { display: block; font: 500 42px/1 var(--display); letter-spacing: -1.4px; }
  .figure span { display: block; margin-top: 9px; font-size: 10px; letter-spacing: 1.5px; color: var(--label); line-height: 1.5; }

  section { padding: 40px 0 0; }
  h2 { margin: 0 0 18px; font-size: 11px; letter-spacing: 2.2px; color: var(--label);
       display: flex; align-items: center; gap: 12px; }
  h2::before { content: ""; width: 22px; height: 2px; background: var(--terracotta); }
  h2::after { content: ""; flex: 1; height: 1px; background: var(--hairline-soft); }
  p { margin: 0; }

  .results { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
  .result { position: relative; overflow: hidden; background: var(--paper); border: 1px solid var(--hairline-soft);
            border-radius: 12px; padding: 18px 18px 18px 22px; box-shadow: 0 2px 8px rgba(20, 20, 19, .03); }
  .result::before { content: ""; position: absolute; top: 0; bottom: 0; left: 0; width: 4px; background: var(--terracotta); }
  .result .who { display: block; font-size: 9.5px; letter-spacing: 1.4px; color: var(--terracotta-active); margin-bottom: 8px; line-height: 1.5; }
  .result strong { display: block; font: 500 19px/1.25 var(--display); letter-spacing: -.3px; text-wrap: balance; }
  .result p { margin-top: 9px; font-size: 13.5px; line-height: 1.55; color: var(--body); }
  small { display: block; margin-top: 8px; font-size: 12px; color: var(--label); }
  .tag { display: inline-block; font-size: 9px; letter-spacing: 1.2px; padding: 3px 7px; border-radius: 6px; margin: 0 0 8px;
         background: var(--warn-bg); color: var(--warn); border: 1px solid var(--warn-ring); }

  .cols { display: grid; grid-template-columns: 1.7fr 1fr; gap: 0 56px; }
  .job { display: grid; grid-template-columns: 128px 1fr; gap: 0 22px; padding: 18px 0; border-top: 1px solid var(--hairline); }
  .job:first-of-type { border-top: 0; padding-top: 2px; }
  .when { padding-top: 6px; font-size: 10px; letter-spacing: 1px; color: var(--label); line-height: 1.6; }
  .job strong { display: block; font: 500 19px/1.3 var(--display); letter-spacing: -.2px; }
  .org { margin: 2px 0 6px; font-size: 13.5px; font-weight: 600; color: var(--terracotta-text); }
  .job p:last-child, .side p, .side li { font-size: 14.5px; color: var(--body); }

  ul { margin: 0; padding: 0; list-style: none; }
  .list li { padding: 11px 0; border-top: 1px solid var(--hairline); }
  .list li:first-child { border-top: 0; padding-top: 0; }
  .list b { display: block; color: var(--ink); font-weight: 600; font-size: 14.5px; }
  .list li span { display: block; margin-top: 2px; font-size: 13px; line-height: 1.5; color: var(--body); }
  .pills { display: flex; flex-wrap: wrap; gap: 6px; }
  .pills li { padding: 4px 11px; border-radius: 999px; background: var(--sand); color: var(--body); font-size: 12.5px; font-weight: 500; }
  .quote { margin: 0 0 12px; padding: 18px 20px; border-radius: 12px; background: var(--terracotta-soft); }
  .quote p { font: italic 400 17px/1.45 var(--display); color: var(--ink); }
  .quote small { color: var(--terracotta-text); }
  .muted { color: var(--label); font-size: 14px; }

  .note { margin-top: 18px; padding: 20px 24px; border: 1px dashed var(--ring); border-radius: 12px;
          background-image: repeating-linear-gradient(45deg, transparent, transparent 6px, rgba(20, 20, 19, .035) 6px, rgba(20, 20, 19, .035) 7px); }
  .note h2 { color: var(--terracotta-text); margin-bottom: 10px; } .note h2::after { display: none; }
  .note ul { list-style: disc; padding-left: 18px; } .note li { margin-bottom: 4px; }
  .foot { padding: 18px 6px 56px; font-size: 13.5px; color: var(--label); }
  .foot code { font-family: var(--mono); background: var(--sand); padding: 1px 6px; border-radius: 5px; color: var(--ink); }

  @media (max-width: 880px) { .bar { padding: 20px 18px 12px; } .sheet { border-radius: 0; border-left: 0; border-right: 0; padding: 40px 22px 32px; }
                              .id { grid-template-columns: 1fr; gap: 16px; } .monogram { width: 60px; height: 60px; font-size: 22px; }
                              .cols, .results { grid-template-columns: 1fr; } .job { grid-template-columns: 1fr; }
                              .when { padding: 0 0 4px; } .summary { font-size: 19px; padding-left: 34px; }
                              .figure { padding-left: 16px; } .note { margin: 14px 14px 0; } .foot { padding: 16px 18px 40px; } }
  @media print { @page { size: A4; margin: 10mm; } body { background: none; font-size: 9.2px; line-height: 1.45; }
                 .bar, .note, .foot { display: none; }
                 .sheet { max-width: none; border: 0; border-radius: 0; box-shadow: none; padding: 12px 0 0; background: none; }
                 .id { gap: 14px; } .monogram { width: 46px; height: 46px; font-size: 17px; }
                 h1 { font-size: 28px; letter-spacing: -.8px; } .headline { font-size: 11.5px; margin-top: 5px; }
                 .kicker { font-size: 7px; margin-bottom: 5px; } .chips { margin-top: 10px; gap: 5px; }
                 .chip { font-size: 8px; padding: 3px 7px; } .chip i { font-size: 6px; }
                 .summary { font-size: 12.5px; margin-top: 16px; padding-left: 26px; } .summary::before { font-size: 40px; top: -7px; }
                 .figures { margin-top: 16px; } .figure { padding: 9px 12px 8px; } .figure strong { font-size: 21px; }
                 .figure span { font-size: 6.2px; margin-top: 4px; }
                 section { padding-top: 16px; } h2 { font-size: 7px; margin-bottom: 8px; }
                 .results { gap: 7px; } .result { padding: 9px 9px 9px 12px; break-inside: avoid; box-shadow: none; }
                 .result strong { font-size: 11px; } .result p { font-size: 8.3px; margin-top: 4px; } .result .who { font-size: 6px; margin-bottom: 4px; }
                 .cols { gap: 0 24px; } .job { grid-template-columns: 74px 1fr; gap: 0 10px; padding: 8px 0; break-inside: avoid; }
                 .job strong { font-size: 11.5px; } .org { font-size: 8.5px; margin-bottom: 3px; } .when { font-size: 6.2px; padding-top: 3px; }
                 .job p:last-child, .side p, .side li, .list b { font-size: 8.8px; } .list li span { font-size: 8px; } .list li { padding: 5px 0; }
                 .pills li { font-size: 7.5px; padding: 2px 6px; } .quote { padding: 9px 10px; } .quote p { font-size: 10px; }
                 small { font-size: 7px; } .tag { font-size: 6px; padding: 2px 4px; } }
"""


def esc(text):
    return html.escape(str(text), quote=False)


def sections(text):
    """Each `## heading` with the lines under it, in file order."""
    found, name, body = [], None, []
    for line in text.splitlines():
        if line.startswith('## '):
            if name:
                found.append((name, body))
            name, body = line[3:].strip(), []
        elif name is not None:
            body.append(line)
    if name:
        found.append((name, body))
    return found


def answers(me):
    """Every `**Label:** value` in the file as {label: value, or None when unanswered}."""
    found = {}
    for _, body in me.items():
        for line in body:
            match = re.match(r'^\*\*(.+?):\*\*\s*(.*)$', line.strip())
            if match:
                value = match.group(2).strip()
                found[match.group(1).strip()] = None if (not value or STARTER in value.lower()) else value
    return found


def pick(found, start):
    """The answer whose label begins with `start`; None when open or absent."""
    for label, value in found.items():
        if label.lower().startswith(start.lower()):
            return value
    return None


def clip(text, limit=CLIP):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].rstrip(',;:') + '…'


def short(label):
    """A label without its parenthesis: 'How settled ... (decided, leaning, open)' reads as a gap."""
    return re.sub(r'\s*\(.*?\)', '', label).strip()


def blank(text):
    return not text.strip() or any(mark in text.lower() for mark in EMPTY)


def entries(body):
    """Each `###` block as {title, text, source, pending}. Empty starter blocks are dropped.

    `pending` is true only for something pulled from elsewhere and not confirmed yet:
    an entry the member stated themselves is never marked, whatever an older file says.
    """
    found, title, lines = [], None, []
    for line in body + ['### ']:
        if line.startswith('### '):
            if title:
                text = [x.strip() for x in lines if x.strip()
                        and not x.strip().startswith(('- ', 'Transfers:')) and not re.match(r'^\*\*.+?:\*\*', x.strip())]
                bullets = {m.group(1).lower(): m.group(2).strip() for x in lines
                           for m in [re.match(r'^-\s*([^:]+):\s*(.*)$', x.strip())] if m}
                joined = ' '.join(text)
                source = bullets.get('source', '')
                if joined and not blank(joined):
                    found.append({'title': title, 'text': joined, 'source': source,
                                  'pending': ('pending' in bullets.get('status', '').lower()
                                              and not source.lower().startswith(OWN_WORDS))})
            title, lines = line[4:].strip(), []
        elif title is not None:
            lines.append(line)
    return found


def role_of(title):
    """'Role, Employer (March 2022 to now)' as (role, employer, when); missing parts come back empty."""
    match = re.match(r'^(.*?)\s*\(([^()]*\d{4}[^()]*)\)\s*$', title)
    name, when = (match.group(1), match.group(2)) if match else (title, '')
    role, _, employer = name.rpartition(', ')
    return (role, employer, when) if role else (name, '', when)


def tag_html(item):
    """The one label on the sheet: something pulled from elsewhere that nobody has confirmed yet."""
    return '<span class="tag">to confirm</span>' if item['pending'] else ''


def trail_html(item):
    """Where an unconfirmed entry came from. A confirmed one needs no footnote on a resume."""
    if not (item['pending'] and item['source']):
        return ''
    return f'<small>Pulled from {esc(clip(item["source"], 120))}</small>'


def job_html(item):
    """One role as a resume row: the years in a narrow column, the work beside them."""
    role, employer, when = role_of(item['title'])
    org = f'<p class="org">{esc(employer)}</p>' if employer else ''
    return (f'<div class="job"><span class="when">{esc(when)}</span>'
            f'<div><strong>{esc(role)}</strong>{org}<p>{esc(clip(item["text"], 340))}</p></div></div>')


def result_html(item):
    """A result as a card: who it was for above, what changed in large type, the detail below."""
    who, _, what = item['title'].partition(': ')
    who, what = (who, what[:1].upper() + what[1:]) if what else ('', who)
    return (f'<article class="result">{tag_html(item)}'
            + (f'<span class="who">{esc(who)}</span>' if who else '')
            + f'<strong>{esc(what)}</strong><p>{esc(clip(item["text"], 210))}</p>{trail_html(item)}</article>')


def credential_html(item):
    return (f'<li>{tag_html(item)}<b>{esc(item["title"])}</b>'
            f'<span>{esc(clip(item["text"], 130))}</span>{trail_html(item)}</li>')


def block(title, inner):
    return f'<section><h2>{esc(title)}</h2>{inner}</section>' if inner else ''


def more(count, shown):
    return f'<p class="muted">and {count - shown} more in your file</p>' if count > shown else ''


def figure_of(label, value):
    """The number an interview answer leads with, or None when it gives none."""
    if not value or value.lower().startswith(('no ', 'none')):
        return None
    if label.startswith('Years'):
        match = re.search(r'\b(\d+|' + '|'.join(NUMBER_WORDS) + r')\b(?=\s+years?)', value, re.I)
        word = match.group(1).lower() if match else ''
        return str(NUMBER_WORDS.get(word, word)) if match else None
    match = re.search(r'\$?\d[\d,]*(?:\.\d+)?\+?', value)
    return match.group(0).rstrip(',.') if match else None


def figures_html(found):
    """The member's own totals from the proof interview, as the row of numbers a reader's eye lands on."""
    cells = []
    for label, caption in FIGURES:
        value = pick(found, label)
        figure = figure_of(label, value)
        if figure:
            note = ', your estimate' if 'estimate' in value.lower() else ''
            cells.append(f'<div class="figure"><strong>{esc(figure)}</strong><span>{esc(caption + note)}</span></div>')
    return f'<div class="figures">{"".join(cells)}</div>' if len(cells) >= 2 else ''


def pills_html(text):
    """Tool names as pills when the answer is a list of them, else the answer as written."""
    plain = re.sub(r'\([^)]*\)', '', text)
    names = [part.rpartition(':')[2].strip() for part in re.split(r'[,.;]', plain)]
    names = list(dict.fromkeys(name for name in names if 2 <= len(name) <= 36))
    if len(names) < 3:
        return f'<p>{esc(clip(text, 320))}</p>'
    extra = f'<li>+ {len(names) - PILLS} more</li>' if len(names) > PILLS else ''
    return '<ul class="pills">' + ''.join(f'<li>{esc(name)}</li>' for name in names[:PILLS]) + extra + '</ul>'


def header_html(found):
    """Initials, name, headline and the facts a client reads first."""
    name, _, place = (pick(found, 'Name and location') or '').partition(',')
    name = name.strip()
    headline = pick(found, 'The one thing') or pick(found, 'Profession')
    facts = (('Based in', place.strip()), ('Rate', pick(found, 'Hourly rate')),
             ('Job Success', pick(found, 'Job Success')), ('Hours', pick(found, 'Timezone')))
    chips = ''.join(f'<li class="chip"><i>{esc(label)}</i>{esc(clip(short(value).split(". ")[0], 60))}</li>'
                    for label, value in facts if value and not value.lower().startswith(('no ', 'none')))
    initials = ''.join(word[0] for word in name.split()[:2]).upper()
    strength = (pick(found, 'What you are good at') or '').strip('"“” ')
    return ('<header class="id">'
            + (f'<div class="monogram" aria-hidden="true">{esc(initials)}</div>' if initials else '<div></div>')
            + '<div><p class="kicker">Upwork resume</p>'
            f'<h1>{esc(name or "Your Upwork resume")}</h1>'
            + (f'<p class="headline">{esc(clip(headline))}</p>' if headline else
               '<p class="headline">What every command reads before it writes for you.</p>')
            + '</div></header>'
            + (f'<ul class="chips">{chips}</ul>' if chips else '')
            + (f'<p class="summary">{esc(clip(strength, 320))}</p>' if strength else ''))


def services_html(me, found):
    """The branches with their services when the file lists them, else the one-line answer."""
    rows = [m.groups() for line in me.get('What you do', [])
            for m in [re.match(r'^-\s*([^:]+):\s*(.+)$', line.strip())] if m]
    if rows:
        return '<ul class="list">' + ''.join(
            f'<li><b>{esc(name)}</b><span>{esc(clip(items))}</span></li>' for name, items in rows) + '</ul>'
    sells = pick(found, 'Services you sell')
    return f'<p>{esc(clip(sells))}</p>' if sells else ''


def open_html(found, unconfirmed):
    """What the sheet is still missing: unanswered lines, then anything waiting for a yes."""
    gaps = [short(label) for label, value in found.items() if value is None and not label.startswith(INTERNAL)]
    lines = [f'<li>{esc(gap)}</li>' for gap in gaps[:8]]
    if len(gaps) > 8:
        lines.append(f'<li>and {len(gaps) - 8} more</li>')
    if unconfirmed:
        lines.append(f'<li>{unconfirmed} {"entry" if unconfirmed == 1 else "entries"} pulled from your files, '
                     'marked "to confirm" until you say they are right</li>')
    return f'<div class="note"><h2>Not on your resume yet</h2><ul>{"".join(lines)}</ul></div>' if lines else ''


def build(me_text, proof_text):
    me = dict(sections(me_text))
    found = answers(me)
    proof = dict(sections(proof_text))
    jobs = entries(me.get('Your background', []))
    results, creds, reviews = (entries(proof.get(name, [])) for name in ('Results', 'Credentials', 'Reviews'))

    experience = ''.join(job_html(j) for j in jobs[:JOBS]) + more(len(jobs), JOBS) or \
        '<p class="muted">Still open. /about-me fills this from your CV and your answers.</p>'
    selected = ('<div class="results">' + ''.join(result_html(r) for r in results[:RESULTS]) + '</div>'
                + more(len(results), RESULTS)) if results else \
        '<p class="muted">Nothing yet. The first delivered job fills this.</p>'
    tools = pick(found, 'Tools and systems')
    schooling = pick(found, 'Education')
    quotes = ''.join(f'<figure class="quote"><p>{esc(clip(r["text"], 220))}</p><small>{esc(r["title"])}</small></figure>'
                     for r in reviews)
    credentials = ('<ul class="list">' + ''.join(credential_html(c) for c in creds[:CREDENTIALS]) + '</ul>'
                   + more(len(creds), CREDENTIALS)) if creds else ''
    unconfirmed = sum(1 for item in results + creds + reviews if item['pending'])
    title = (pick(found, 'Name and location') or 'Your Upwork resume').partition(',')[0]

    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(title)} · Upwork resume</title>\n<style>' + tokens() + CSS + '</style>\n</head>\n<body>\n'
            '<div class="bar"><span>Upwork resume</span>'
            '<button type="button" onclick="window.print()">Print or save as PDF</button></div>\n'
            '<main class="sheet">\n' + header_html(found) + figures_html(found) + '\n'
            + block('Selected results', selected) +
            '\n<div class="cols">\n<div>\n'
            + block('Experience', experience) +
            '\n</div>\n<div class="side">\n'
            + block('Services', services_html(me, found))
            + block('Tools', pills_html(tools) if tools else '')
            + block('Credentials', credentials)
            + block('Education and languages', f'<p>{esc(clip(schooling, 320))}</p>' if schooling else '')
            + block('Recommendations', quotes) +
            '\n</div>\n</div>\n</main>\n'
            + open_html(found, unconfirmed) +
            '\n<p class="foot">Next: <code>/profile</code> writes your Upwork profile from this. '
            'Built from context/me.md on this machine; rebuild it with '
            '<code>python3 code/context_page.py --open</code>.</p>\n'
            '</body>\n</html>\n')


def tokens():
    """The shared tokens, inlined so the page opens from disk with no other file."""
    if not TOKENS.is_file():
        raise SystemExit(f'{TOKENS.relative_to(ROOT)} is missing: the page takes its look from it.')
    return TOKENS.read_text(encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--open', action='store_true', help='open it in the browser')
    args = parser.parse_args(argv)
    if not cc.ME.is_file():
        print(f'{cc.ME} is missing. Run python3 code/workspace.py')
        return 1
    me_text = cc.ME.read_text(encoding='utf-8')
    proof_text = cc.proof_only(me_text)
    open_points = len(cc.check_me(me_text) + cc.check_proof(proof_text))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(me_text, proof_text), encoding='utf-8')
    print(f'{OUT.relative_to(ROOT)} written, {open_points} open')
    if args.open:
        webbrowser.open(OUT.as_uri())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
