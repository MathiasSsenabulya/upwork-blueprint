#!/usr/bin/env python3
"""The member's Upwork profile draft as one page, built from profile.md.

    python3 code/profile_page.py [--open]

/profile writes profile.md, the paste-ready source. This renders it on the same
sheet as the resume (`context/overview.html`): the member's name and the title on
top, what shows in search as the quote, the client critic's choice and the counts
as the row of figures, the portfolio titles as cards, then the overview, the video
script, the employment history and the remaining fields, with the critic, the gate
and the skills beside them. What is still to decide sits in the note under it.

Everything a member pastes into Upwork copies with one click: the long texts have
a Copy button, and every other field is itself the button.

Output is `profile.html` beside profile.md, gitignored like it. It is built from
the files alone and reaches no service. The look is the stylesheet of
`code/context_page.py` on the tokens in `website/app/tokens.css`, so the two pages
cannot drift apart; only what a resume does not have is styled here.
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
import context_page as cp  # noqa: E402
import profile_checks as pc  # noqa: E402
import profile_draft as pd  # noqa: E402

SOURCE = ROOT / 'profile.md'
OUT = ROOT / 'profile.html'
# The sections that are instructions rather than fields, folded so the sheet stays a profile.
HOW = ('Paste order', 'Completeness', 'Reference averages')
PLACED = ('Your Upwork profile', 'Decide first', 'Title', 'Overview', 'Skills', 'Portfolio titles',
          'Video script', 'Profile fields', 'Client critic')

# Added to the resume's stylesheet: the copy affordance, the critic's marks and the folded notes.
CSS = """
  .copy { position: relative; font: inherit; color: inherit; letter-spacing: inherit; text-align: left;
          background: none; border: 0; padding: 0; margin: 0; border-radius: 6px; cursor: copy; }
  .copy:hover { background: var(--terracotta-soft); }
  .copy:focus-visible, h2 button:focus-visible { outline: 2px solid var(--terracotta-text); outline-offset: 2px; }
  .copy.copied::after { content: "Copied"; position: absolute; right: 0; top: -24px; padding: 4px 8px; border-radius: 6px;
                        background: var(--ink); color: var(--ivory); font: 500 11px/1 var(--sans);
                        letter-spacing: 0; text-transform: none; white-space: nowrap; }
  button.result { display: block; width: 100%; border: 1px solid var(--hairline-soft); padding: 18px 18px 18px 22px;
                  border-radius: 12px; background: var(--paper); }
  button.result.copied::after { top: 8px; right: 8px; }
  .pills li { padding: 0; } .pills .copy { padding: 4px 11px; border-radius: 999px; }
  .job p.org { font-size: 13.5px; color: var(--terracotta-text); }
  @media (min-width: 881px) { .results { grid-template-columns: repeat(2, 1fr); } }
  h2 button { order: 1; font: 500 12px/1 var(--sans); letter-spacing: 0; text-transform: none; padding: 7px 14px;
              border-radius: 999px; cursor: pointer; border: 1px solid var(--hairline-soft);
              background: var(--paper); color: var(--body); }
  h2 button:hover { background: var(--sand); color: var(--ink); }
  pre { margin: 0; white-space: pre-wrap; font: 15px/1.65 var(--sans); color: var(--ink); }
  .under { margin-top: 12px; padding-left: 46px; }
  .chip.go { background: var(--good-bg); color: var(--good-text); box-shadow: 0 0 0 1px var(--good-ring); }
  .chip.held { background: var(--bad-bg); color: var(--bad-text); box-shadow: 0 0 0 1px var(--bad-ring); }
  .chip.go i, .chip.held i { color: inherit; }
  .marks { margin-top: 14px; }
  .marks li { position: relative; padding: 10px 0 10px 24px; border-top: 1px solid var(--hairline); }
  .marks li::before { content: ""; position: absolute; left: 0; top: 15px; width: 12px; height: 12px; border-radius: 4px; }
  .marks .yes::before { background: var(--good); }
  .marks .no::before { background: var(--bad-bg); box-shadow: inset 0 0 0 1.5px var(--bad); }
  .marks b, .prose b, .note b { color: var(--ink); font-weight: 600; }
  .bench { margin-top: 12px; line-height: 1.9; }
  details { border-top: 1px solid var(--hairline); padding: 12px 0; } details:first-of-type { border-top: 0; padding-top: 0; }
  details summary { cursor: pointer; font-weight: 600; font-size: 14.5px; } details > div { margin-top: 10px; }
  .prose p, .prose li { font-size: 14.5px; color: var(--body); } .prose p { margin: 0 0 10px; }
  .prose ul, .prose ol { list-style: revert; padding-left: 20px; margin: 0 0 10px; } .prose li { margin-bottom: 5px; }
  .sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
  @media (max-width: 880px) { .under { padding-left: 34px; } }
"""

# One handler for every copy: a field carries its own text, a Copy button names the block it copies.
SCRIPT = """
  var said = document.getElementById('said');
  function put(text, el) {
    var done = function () {
      said.textContent = 'Copied: ' + text.slice(0, 60);
      if (el.hasAttribute('data-say')) { el.textContent = 'Copied'; } else { el.classList.add('copied'); }
      setTimeout(function () {
        if (el.hasAttribute('data-say')) { el.textContent = el.getAttribute('data-say'); } else { el.classList.remove('copied'); }
      }, 1400);
    };
    var plain = function () {
      var area = document.createElement('textarea'); area.value = text; document.body.appendChild(area);
      area.select(); var copied = document.execCommand('copy'); area.remove(); if (copied) { done(); }
    };
    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(text).then(done, plain); return; }
    plain();
  }
  document.querySelectorAll('[data-text], [data-copy]').forEach(function (el) {
    el.addEventListener('click', function () {
      put(el.dataset.copy ? document.getElementById(el.dataset.copy).textContent : el.dataset.text, el);
    });
  });
"""

esc = cp.esc


def attr(text: str) -> str:
    """Text made safe inside a double-quoted attribute."""
    return html.escape(str(text), quote=True)


def inline(text: str) -> str:
    """Escaped text with `**bold**` kept, which is the only inline mark profile.md uses."""
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', esc(text))


def copy(text: str, classes: str = 'copy', inner: str = '') -> str:
    """A field the member pastes into Upwork: the text is the button, and a click copies it."""
    return (f'<button type="button" class="{classes}" data-text="{attr(text)}" title="Click to copy">'
            f'{inner or esc(text)}</button>')


def copy_button(label: str, target: str = '', text: str = '') -> str:
    """A labelled Copy button for a long block (by element id) or for a text of its own."""
    what = f'data-copy="{attr(target)}"' if target else f'data-text="{attr(text)}"'
    return f'<button type="button" {what} data-say="{attr(label)}">{esc(label)}</button>'


def block(title: str, inner: str, button: str = '') -> str:
    return f'<section><h2>{esc(title)}{button}</h2>{inner}</section>' if inner else ''


def sections(text: str) -> dict[str, list[str]]:
    """Each `#` or `##` heading with the lines under it, in file order."""
    found: dict[str, list[str]] = {}
    name = None
    for line in text.splitlines():
        match = re.match(r'^#{1,2} (.+)$', line)
        if match:
            name = match.group(1).strip()
            found[name] = []
        elif name is not None:
            found[name].append(line)
    return found


def render(lines: list[str]) -> str:
    """Paragraphs, bullet and numbered lists and fenced text, as the file wrote them."""
    out, buffer, kind, fenced = [], [], None, False

    def flush() -> None:
        nonlocal buffer, kind
        if buffer and kind in ('ul', 'ol'):
            out.append(f'<{kind}>' + ''.join(f'<li>{inline(item)}</li>' for item in buffer) + f'</{kind}>')
        elif buffer and kind == 'pre':
            out.append('<pre>' + esc('\n'.join(buffer)) + '</pre>')
        elif buffer:
            out.append('<p>' + inline(' '.join(buffer)) + '</p>')
        buffer, kind = [], None

    for line in lines:
        if line.startswith('```'):
            flush()
            fenced, kind = not fenced, ('pre' if not fenced else None)
            continue
        bullet = None if fenced else re.match(r'^(?:[-*]|(\d+)\.)\s+(.*)$', line)
        wanted = 'pre' if fenced else ('ol' if bullet and bullet.group(1) else 'ul' if bullet else 'p')
        if not fenced and (not line.strip() or line.startswith('> ') or wanted != kind):
            flush()
        if fenced or (line.strip() and not line.startswith('> ')):
            buffer.append(bullet.group(2) if bullet else line if fenced else line.strip())
            kind = wanted
    flush()
    return ''.join(out)


def field(lines: list[str], label: str) -> str:
    """The value after a `**Label:**` line in a section, or an empty string."""
    for line in lines:
        match = re.match(rf'^\*\*{re.escape(label)}[^:]*:\*\*\s*(.*)$', line.strip())
        if match:
            return match.group(1).strip()
    return ''


def critic_of(lines: list[str]) -> dict:
    """The client critic's verdict as /profile writes it under `## Client critic`."""
    grade = re.search(r'(\d+)\s*of\s*the\s*next\s*(\d+)', field(lines, 'Chosen over'))
    marks = [m.groups() for line in lines
             for m in [re.match(r'^-\s*\*\*(Yes|No)\s*·\s*(.+?)\*\*\s*(.*)$', line.strip())] if m]
    return {'grade': int(grade.group(1)) if grade else None, 'floor': int(grade.group(2)) if grade else 9,
            'peers': field(lines, 'Compared with'), 'why': field(lines, 'Would close the tab because'), 'marks': marks}


def critic_html(critic: dict) -> str:
    if critic['grade'] is None:
        return ('<p class="muted">Not judged yet. /profile has a fresh reader choose between this draft '
                'and nine like it before anything goes live.</p>')
    facts = (('Compared with', critic['peers']), ('Would close the tab because', critic['why']))
    said = ''.join(f'<li><b>{esc(label)}</b><span>{inline(value)}</span></li>' for label, value in facts if value)
    marks = ''.join(f'<li class="{answer.lower()}"><b>{esc(question)}</b> {inline(reason)}</li>'
                    for answer, question, reason in sorted(critic['marks'], key=lambda m: m[0] != 'No'))
    return f'<ul class="list">{said}</ul><ul class="marks">{marks}</ul>'


def verdict(critic: dict, failures: list[str]) -> tuple[str, str]:
    """Whether this draft may go live, as (chip class, one line) with the first thing in its way."""
    graded = critic['grade'] is not None
    if graded and critic['grade'] >= critic['floor'] and not failures:
        return 'go', 'Ready to go live'
    reason = (f'the gate found {len(failures)} problem{"" if len(failures) == 1 else "s"}' if failures
              else f'beats {critic["grade"]} of {critic["floor"]} rival profiles, one still wins' if graded
              else 'no client critic has judged it yet')
    return 'held', f'Held · {reason}'


def profile_fields(lines: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """`## Profile fields` as the employment lines and the `**Label:** value` fields."""
    jobs: list[str] = []
    labelled: list[tuple[str, str]] = []
    in_jobs = False
    for line in (raw.strip() for raw in lines):
        match = re.match(r'^\*\*(.+?):\*\*\s*(.+)$', line)
        if match:
            labelled.append((match.group(1), match.group(2)))
            in_jobs = False
        elif line.startswith('**Employment'):
            in_jobs = True
        elif in_jobs and line.startswith('- '):
            jobs.append(line[2:].strip())
    return jobs, labelled


def job_html(line: str) -> str:
    """One employment line as a resume row, the role and the employer each a field to copy."""
    parts = line.split(', ')
    if len(parts) < 3:
        return f'<div class="job"><span class="when"></span><div><strong>{copy(line)}</strong></div></div>'
    role, employer, when = ', '.join(parts[:-2]), parts[-2], parts[-1]
    return (f'<div class="job"><span class="when">{esc(when)}</span>'
            f'<div><strong>{copy(role)}</strong><p class="org">{copy(employer)}</p></div></div>')


def portfolio_html(titles: list[str]) -> str:
    """Each portfolio title as a result card: who it was for above, what changed in large type."""
    cards = []
    for title in titles:
        who, _, what = title.partition(': ')
        who, what = (who, what[:1].upper() + what[1:]) if what else ('', who)
        inner = (f'<span class="who">{esc(who)}</span>' if who else '') + f'<strong>{esc(what)}</strong>'
        cards.append(copy(title, 'result copy', inner))
    return '<div class="results">' + ''.join(cards) + '</div>' if cards else ''


def skills_html(skills: list[str], lines: list[str]) -> str:
    """The skills as pills, then the bench of names to swap in, each one a field to copy."""
    if not skills:
        return ''
    bench = next((line.partition(':')[2] for line in lines if line.strip().lower().startswith('bench')), '')
    names = [name.strip(' .') for name in bench.split(',') if name.strip(' .')]
    spare = '<p class="muted bench">Bench: ' + ' · '.join(copy(name) for name in names) + '</p>' if names else ''
    return '<ul class="pills">' + ''.join(f'<li>{copy(skill)}</li>' for skill in skills) + '</ul>' + spare


def opening_of(overview: str) -> tuple[str, bool]:
    """What search shows of an overview, and whether more follows.

    Cut at the last sentence that ends inside the opening; when none ends in its
    second half, at the last whole word.
    """
    if len(overview) <= pc.OPENING:
        return ' '.join(overview.split()), False
    shown = overview[:pc.OPENING + 1]
    ends = [match.end() for match in re.finditer(r'[.!?](?=\s)', shown)]
    whole = shown[:ends[-1]] if ends and ends[-1] > pc.OPENING // 2 else shown[:pc.OPENING].rsplit(' ', 1)[0]
    return ' '.join(whole.split()), True


def header_html(name: str, title: str, chips: str, opening: str, cut: bool) -> str:
    """Initials, name and title as on the resume, then what a client sees before clicking."""
    initials = ''.join(word[0] for word in name.split()[:2]).upper()
    return ('<header class="id">'
            + (f'<div class="monogram" aria-hidden="true">{esc(initials)}</div>' if initials else '<div></div>')
            + '<div><p class="kicker">Upwork profile · draft</p>'
            f'<h1>{esc(name or "Your Upwork profile")}</h1>'
            f'<p class="headline">{copy(title) if title else "No title yet"}</p></div></header>'
            + f'<ul class="chips">{chips}</ul>'
            + (f'<p class="summary">{esc(opening)}{" …" if cut else ""}</p>'
               '<small class="under">What shows in search before a client clicks. '
               'Click any field on this page to copy it.</small>' if opening else ''))


def figures_html(critic: dict, draft: dict) -> str:
    """The critic's choice and the counts the gate measures, as the resume's row of figures."""
    overview = draft['overview']
    cells = [(f'{critic["grade"]} of {critic["floor"]}', 'rival profiles this one beats')] if critic['grade'] is not None else []
    cells += [(str(len(overview.split())), f'words in the overview, {pd.OVERVIEW_WORDS} at most'),
              (f'{pd.reading_grade(overview, draft["skills"]):.1f}', f'reading grade, under {pd.GRADE_MAX:g}'),
              (str(len(draft['skills'])), f'skills of {pd.SKILLS_MAX}'),
              (str(len(draft['title'])), f'title characters of {pd.TITLE_MAX}')]
    return '<div class="figures">' + ''.join(
        f'<div class="figure"><strong>{esc(big)}</strong><span>{esc(small)}</span></div>' for big, small in cells) + '</div>'


def gate_html(failures: list[str]) -> str:
    if not failures:
        return "<p>Passed: Upwork's limits, the reading grade, the length and every number against your evidence.</p>"
    return '<ul class="list">' + ''.join(
        f'<li><span class="tag">fix</span><span>{esc(failure)}</span></li>' for failure in failures) + '</ul>'


def how_html(found: dict[str, list[str]]) -> str:
    """The instructions, closed by default so the sheet stays a profile and not a manual."""
    names = list(HOW) + [name for name in found if name not in PLACED + HOW]
    return ''.join(f'<details><summary>{esc(name)}</summary><div class="prose">{render(found[name])}</div></details>'
                   for name in names if any(line.strip() for line in found.get(name, [])))


def build(text: str, me_text: str) -> str:
    found = sections(text)
    draft = pd.parse(text)
    failures = (pd.problems(draft, cc.proof_only(me_text), pd.recorded_promise(me_text))
                if draft['title'] and draft['overview'] else ['no title or overview in a fenced block yet'])
    critic = critic_of(found.get('Client critic', []))
    jobs, labelled = profile_fields(found.get('Profile fields', []))
    values = dict(labelled)
    name = (cp.pick(cp.answers(dict(cp.sections(me_text))), 'Name and location') or '').partition(',')[0].strip()
    overview, video = draft['overview'], draft['video']
    opening, cut = opening_of(overview)
    rate = re.search(r'\$\s?(\d+(?:[.,]\d+)*)', values.get('Hourly rate', ''))
    state, line = verdict(critic, failures)
    hours = values.get('Availability', '').rstrip('.')
    chips = (f'<li class="chip {state}"><i>Verdict</i>{esc(line)}</li>'
             + (f'<li class="chip"><i>Rate</i>{copy(rate.group(1), inner=esc(rate.group(0) + " an hour"))}</li>' if rate else '')
             + (f'<li class="chip"><i>Hours</i>{copy(hours)}</li>' if hours else ''))
    fields = '<ul class="list">' + ''.join(
        f'<li><b>{esc(label)}</b><span>{copy(value)}</span></li>' for label, value in labelled) + '</ul>' if labelled else ''
    stamp = next((entry.strip() for entry in found.get('Your Upwork profile', []) if entry.strip()), '')

    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{esc(name or "Your")} · Upwork profile</title>\n<style>' + cp.tokens() + cp.CSS + CSS + '</style>\n</head>\n<body>\n'
            '<div class="bar"><span>Upwork profile</span>'
            + (copy_button('Copy overview', target='overview') if overview else '') + '</div>\n'
            '<main class="sheet">\n' + header_html(name, draft['title'], chips, opening, cut)
            + figures_html(critic, draft) + '\n'
            + block('Portfolio titles', portfolio_html(draft['portfolio'] or [])) +
            '\n<div class="cols">\n<div>\n'
            + block('Overview', f'<pre id="overview">{esc(overview)}</pre>' if overview else '',
                    copy_button('Copy', target='overview'))
            + block('Video script', f'<pre id="video">{esc(video)}</pre>' if video else '', copy_button('Copy', target='video'))
            + block('Employment history', ''.join(job_html(job) for job in jobs))
            + block('Profile fields', fields)
            + block('How to put it on Upwork', how_html(found)) +
            '\n</div>\n<div class="side">\n'
            + block('Client critic', critic_html(critic)) + block('The gate', gate_html(failures))
            + block('Skills', skills_html(draft['skills'], found.get('Skills', [])),
                    copy_button('Copy all', text=', '.join(draft['skills']))) +
            '\n</div>\n</div>\n</main>\n'
            + (f'<div class="note"><h2>Decide first</h2>{render(found["Decide first"])}</div>'
               if any(entry.strip() for entry in found.get('Decide first', [])) else '') +
            f'\n<p class="foot">{esc(stamp)}{". " if stamp else ""}Built from profile.md on this machine; rebuild it with '
            '<code>python3 code/profile_page.py --open</code>.</p>\n'
            '<p class="sr" id="said" aria-live="polite"></p>\n<script>' + SCRIPT + '</script>\n</body>\n</html>\n')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--open', action='store_true', help='open it in the browser')
    args = parser.parse_args(argv)
    if not SOURCE.is_file():
        print(f'{SOURCE.name} is missing. /profile writes it.')
        return 1
    me_text = cc.ME.read_text(encoding='utf-8') if cc.ME.is_file() else ''
    OUT.write_text(build(SOURCE.read_text(encoding='utf-8'), me_text), encoding='utf-8')
    print(f'{OUT.name} written')
    if args.open:
        webbrowser.open(OUT.as_uri())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
