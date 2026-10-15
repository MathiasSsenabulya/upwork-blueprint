#!/usr/bin/env python3
"""One split test at a time on the step that leaks, called at about 80% sure.

/analytics finds the leak and names the fix. When the fix is a piece of writing or a
script, this tests it against what the member does now: A is today's way, B is the
fix. The command writing that piece asks for the variant, the lead is tagged, and the
pipeline already records what happened next. Nothing here sends anything.

    python3 code/split_test.py new <stage> --a "<what A does>" --b "<what B does>" [--mover "<title>"]
    python3 code/split_test.py assign <job id> --stage <stage>
    python3 code/split_test.py status
    python3 code/split_test.py ship <A|B>
    python3 code/split_test.py stop --reason "<why>"
    python3 code/split_test.py list

Stages and what counts as a win for a lead in the test:

    profile      the application got a reply within 7 days (before and after the change)
    proposal     the application got a reply within 7 days
    messages     the conversation booked a call within 14 days
    call         the call led to an offer or a win within 14 days
    after-call   the post-call proposal or pre-hire piece was won within 21 days
    close        the deal was won within 21 days

A profile cannot run two versions at once, so a profile test compares the 28 days
of applications before the change (A) with everything sent after it (B).

The test is the top mover's change: /analytics names the 1 to 3 changes that matter most, and
`diagnosis.py save` starts the test on the one that carries it. A messages test can also be a
follow-up rhythm (`--a-days 3,7 --b-days 1,2,3,4,5`): the pipeline then schedules each quiet
lead's follow-ups by its side, so the rhythm is followed without anyone remembering it.

What was actually sent is checked, not just what was drafted. `--b-checks` names what the
new way always has (for a proposal: question, offer, video, no_filler, own_words; for a
reply: question, call_times). A lead on B whose sent copy lacks one of them, or a lead on A
whose sent copy has them all, was sent differently: it is left out of the result and
counted, so an edit before sending never muddies the call. A call test reads the same from
each call's grade, where Claude noted from the transcript which way the call actually went.

The call is Bayesian: each side's win rate gets a Beta(1 + wins, 1 + losses), and
status prints how likely B is to beat A. At 80% or more with five finished leads a
side, B ships; at 20% or less, A stays. 80% right and moving beats 95% and stalled.
"""
import argparse
import datetime
import json
import math
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import application_check as letters  # noqa: E402
import pipeline  # noqa: E402

# stage: (the event that starts the clock, the events that count as a win, days allowed)
STAGES = {
    'profile': ('applied', ('replied', 'call', 'offer', 'won'), 7),
    'proposal': ('applied', ('replied', 'call', 'offer', 'won'), 7),
    'messages': ('assigned', ('call', 'offer', 'won'), 14),
    'call': ('assigned', ('offer', 'won'), 14),
    'after-call': ('assigned', ('won',), 21),
    'close': ('assigned', ('won',), 21),
}
WIN_WORDS = {'profile': 'got a reply', 'proposal': 'got a reply', 'messages': 'booked a call',
             'call': 'reached an offer', 'after-call': 'won', 'close': 'won'}
SHIP_AT = 0.80
KEEP_AT = 0.20
MIN_DONE = 5
PROFILE_BEFORE_DAYS = 28
# Where each event's time lives on a lead. A later stage implies the earlier one.
EVENT_FIELDS = {
    'applied': ('applied_at',),
    'replied': ('replied_at', 'first_client_message_at'),
    'call': ('call_booked_at', 'call_scheduled_at', 'call_held_at'),
    'offer': ('offered_at', 'offer_at'),
    'won': ('won_at',),
}


TIME = re.compile(r'\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b|\b\d{1,2}:\d{2}\b', re.I)


def card(text):
    return ' '.join(re.findall(r"\b[\w'$%+-]+\b", text)[:letters.CARD_WORDS]).lower()


# What code can see in a sent copy, per stage: the marks of the new way.
FEATURES = {
    'proposal': {
        'question': lambda job, text: '?' in text,
        'offer': lambda job, text: bool(letters.OFFER.search(text) or any(r in text.lower() for r in letters.RISK)),
        'video': lambda job, text: bool(letters.has_video(text)),
        'no_filler': lambda job, text: not any(re.search(p, card(text)) for p in letters.FILLER_OPENERS),
        'own_words': lambda job, text: any(w in card(text) for w in re.findall(r"[\w']+", str(job.get('title', '')).lower()) if len(w) > 3),
    },
    'messages': {
        'question': lambda job, text: '?' in text,
        'call_times': lambda job, text: len(TIME.findall(text)) >= 2,
    },
}


def sent_text(job, unit, stage):
    """What the member actually sent for this lead, or None while it is not sent or not saved."""
    folder = pipeline.jobs_dir() / str(job['id'])
    if stage == 'proposal':
        path = folder / 'application.sent.md'
        return path.read_text(encoding='utf-8') if path.is_file() else None
    if stage == 'messages':
        try:
            thread = json.loads((folder / 'thread.json').read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return None
        start = parse(unit.get('at'))
        mine = [m.get('text', '') for m in thread.get('messages') or []
                if m.get('from') == 'me' and (not start or (parse(m.get('at')) or start) >= start)]
        return '\n'.join(mine) if mine else None
    return None


def sent_as(job, unit, test):
    """'followed', 'changed', or None when nothing can be checked yet."""
    if test['stage'] == 'call':
        try:
            went = json.loads((pipeline.jobs_dir() / str(job['id']) / 'call-grade.json').read_text(encoding='utf-8')).get('followed')
        except (OSError, json.JSONDecodeError, AttributeError):
            return None
        return None if went not in ('A', 'B') else 'followed' if went == unit['variant'] else 'changed'
    checks = test.get('b_checks') or []
    rules = FEATURES.get(test['stage'], {})
    text = sent_text(job, unit, test['stage']) if checks else None
    if text is None:
        return None
    has_all = all(rules[name](job, text) for name in checks if name in rules)
    return 'followed' if has_all == (unit['variant'] == 'B') else 'changed'


def tests_path():
    return pipeline.data_dir() / 'split-tests.json'


def load_tests():
    try:
        value = json.loads(tests_path().read_text(encoding='utf-8'))
    except FileNotFoundError:
        return []
    except (OSError, json.JSONDecodeError) as problem:
        pipeline.abort(f'split-tests.json cannot be read: {problem}')
    return value.get('tests', []) if isinstance(value, dict) else []


def save_tests(tests):
    path = tests_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps({'tests': tests}, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def running(tests):
    return next((test for test in tests if test.get('status') == 'running'), None)


def parse(value):
    if not value:
        return None
    try:
        stamp = datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=datetime.timezone.utc)


def when(job, name):
    """The earliest time a lead reached this event, from its own field or its stage history."""
    times = [parse(job.get(field)) for field in EVENT_FIELDS.get(name, ())]
    times += [parse(entry.get('at')) for entry in job.get('history') or []
              if isinstance(entry, dict) and entry.get('status') == name]
    times = [t for t in times if t]
    return min(times) if times else None


def outcome(job, start, stage, now):
    """'win', 'loss' or None while the lead still has time."""
    _, wins, days = STAGES[stage]
    deadline = start + datetime.timedelta(days=days)
    reached = [t for t in (when(job, name) for name in wins) if t and t >= start]
    if reached and min(reached) <= deadline:
        return 'win'
    if now >= deadline or job.get('status') == 'lost':
        return 'loss'
    return None


def units(test, jobs, now):
    """Every lead in the test with its variant and result, None for still waiting."""
    by_id = {str(job['id']): job for job in jobs}
    stage = test['stage']
    rows = []
    if stage == 'profile':
        switch = parse(test['started_at'])
        earliest = switch - datetime.timedelta(days=PROFILE_BEFORE_DAYS)
        for job in jobs:
            applied = when(job, 'applied')
            if job.get('imported') or not applied or applied < earliest:
                continue
            rows.append({'job_id': str(job['id']), 'variant': 'A' if applied < switch else 'B',
                         'result': outcome(job, applied, stage, now)})
        return rows
    for unit in test.get('units', []):
        job = by_id.get(unit['job_id'])
        if not job:
            continue
        start = when(job, 'applied') if STAGES[stage][0] == 'applied' else parse(unit['at'])
        # A proposal that was never sent is not in the test.
        if not start or job.get('status') == 'skipped' and STAGES[stage][0] == 'applied':
            continue
        rows.append({'job_id': unit['job_id'], 'variant': unit['variant'],
                     'result': outcome(job, start, stage, now), 'sent_as': sent_as(job, unit, test)})
    return rows


def log_beta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def chance_b_beats_a(wins_a, losses_a, wins_b, losses_b):
    """P(rate B > rate A) under Beta(1 + wins, 1 + losses) on each side, exact."""
    a1, b1, a2, b2 = 1 + wins_a, 1 + losses_a, 1 + wins_b, 1 + losses_b
    total = 0.0
    for i in range(a2):
        total += math.exp(log_beta(a1 + i, b1 + b2) - math.log(b2 + i)
                          - log_beta(1 + i, b2) - log_beta(a1, b1))
    return min(1.0, max(0.0, total))


def summary(test, jobs, now):
    rows = units(test, jobs, now)
    changed = sum(row.get('sent_as') == 'changed' for row in rows)
    # A lead sent differently from its side says nothing about either side: it is left out.
    rows = [row for row in rows if row.get('sent_as') != 'changed']
    sides = {}
    for variant in ('A', 'B'):
        mine = [row for row in rows if row['variant'] == variant]
        sides[variant] = {'leads': len(mine),
                          'wins': sum(row['result'] == 'win' for row in mine),
                          'done': sum(row['result'] is not None for row in mine)}
    a, b = sides['A'], sides['B']
    chance = chance_b_beats_a(a['wins'], a['done'] - a['wins'], b['wins'], b['done'] - b['wins'])
    enough = min(a['done'], b['done']) >= MIN_DONE
    call = 'ship B' if enough and chance >= SHIP_AT else 'keep A' if enough and chance <= KEEP_AT else 'keep going'
    return {'sides': sides, 'chance_b': chance, 'call': call, 'changed': changed}


def print_status(test, jobs, now):
    result = summary(test, jobs, now)
    word = WIN_WORDS[test['stage']]
    print(f"Split test on {test['stage']}, started {test['started_at'][:10]}")
    for variant in ('A', 'B'):
        side = result['sides'][variant]
        waiting = side['leads'] - side['done']
        tail = f', {waiting} still waiting' if waiting else ''
        print(f"  {variant}: {test[variant.lower()]}")
        print(f"     {side['wins']} of {side['done']} {word}{tail}")
    if result['changed']:
        print(f"  {result['changed']} sent differently from their side, so they are left out.")
    if not any(result['sides'][v]['done'] for v in ('A', 'B')):
        print(f'  Nothing has finished yet. Each new lead gets A or B, and B ships once it is {round(100 * SHIP_AT)}% likely to win.')
        return result
    print(f"  B is {round(100 * result['chance_b'])}% likely to beat A.")
    short = [v for v in ('A', 'B') if result['sides'][v]['done'] < MIN_DONE]
    if result['call'] == 'keep going' and short:
        print(f"  Call: keep going. {' and '.join(short)} need {MIN_DONE} finished leads each before a call.")
    elif result['call'] == 'keep going':
        print('  Call: keep going. Neither side is ahead enough yet.')
    else:
        print(f"  Call: {result['call']}. Run: python3 code/split_test.py ship {result['call'][-1]}")
    return result


def rhythm(value):
    """'1, 2, 3' as rising whole days, or None when there is no rhythm."""
    days = [int(n) for n in re.findall(r'\d+', str(value or ''))]
    if not days:
        return None
    if days[0] < 1 or any(a >= b for a, b in zip(days, days[1:])) or len(days) > 14:
        pipeline.abort(f'follow-up days must rise from day 1 or later: {value}')
    return days


def start(stage, a, b, checks=(), days=None, mover=None):
    """Start the one test. Aborts when another is running or the parts do not fit the stage."""
    if stage not in STAGES:
        pipeline.abort('stage is one of: ' + ', '.join(STAGES))
    tests = load_tests()
    live = running(tests)
    if live:
        pipeline.abort(f"a {live['stage']} test is already running; ship or stop it first. One test at a time keeps the result clean.")
    if not str(a or '').strip() or not str(b or '').strip():
        pipeline.abort('both A and B need a one-line description.')
    checks = [c for c in checks if c]
    unknown = [c for c in checks if c not in FEATURES.get(stage, {})]
    if unknown:
        pipeline.abort(f"b checks for {stage} can be: " + (', '.join(FEATURES.get(stage, {})) or 'none, this stage is checked by Claude'))
    if days and (stage != 'messages' or not days.get('A') or not days.get('B')):
        pipeline.abort('follow-up days are for a messages test, and need both sides.')
    now = pipeline.now_iso()
    test = {'id': f"{stage}-{now[:10]}", 'stage': stage, 'a': ' '.join(str(a).split())[:300],
            'b': ' '.join(str(b).split())[:300], 'b_checks': checks, 'started_at': now, 'status': 'running', 'units': []}
    if days:
        test['days'] = {'A': days['A'], 'B': days['B']}
    if mover:
        test['mover'] = ' '.join(str(mover).split())[:200]
    tests.append(test)
    save_tests(tests)
    return test


def cmd_new(args):
    days = {'A': rhythm(args.a_days), 'B': rhythm(args.b_days)} if args.a_days or args.b_days else None
    test = start(args.stage, args.a, args.b, [c.strip() for c in (args.b_checks or '').split(',')], days, args.mover)
    print(f"Split test started on {args.stage}.")
    print(f"  A: {test['a']}")
    print(f"  B: {test['b']}")
    if args.stage == 'profile':
        print('  Change the profile to B now. Applications from here on are B; the 28 days before are A.')


def take(tests, test, job_id):
    """The lead's side, giving it one when it has none: the side with fewer leads goes next."""
    unit = next((u for u in test['units'] if u['job_id'] == job_id), None)
    if not unit:
        counts = {v: sum(u['variant'] == v for u in test['units']) for v in ('A', 'B')}
        unit = {'job_id': job_id, 'variant': 'A' if counts['A'] <= counts['B'] else 'B', 'at': pipeline.now_iso()}
        test['units'].append(unit)
        save_tests(tests)
    return unit


def days_for(job_id):
    """The follow-up days for a quiet lead while a rhythm test runs, or None to use the member's own."""
    tests = load_tests()
    test = running(tests)
    if not test or test['stage'] != 'messages' or not test.get('days'):
        return None
    return tuple(test['days'][take(tests, test, str(job_id))['variant']])


def cmd_assign(args):
    tests = load_tests()
    test = running(tests)
    if not test or test['stage'] != args.stage or args.stage == 'profile':
        print(f'No split test running for {args.stage}.')
        return
    job_id = str(args.job_id)
    if not any(str(job['id']) == job_id for job in pipeline.load()):
        pipeline.abort(f'{job_id} is not in the pipeline.')
    unit = take(tests, test, job_id)
    print(f"Variant {unit['variant']}: {test[unit['variant'].lower()]}")


def cmd_status(args):
    tests = load_tests()
    test = running(tests)
    if not test:
        print('No split test running.')
        return
    print_status(test, pipeline.load(), datetime.datetime.now(datetime.timezone.utc))


def finish(status, winner=None, reason=None):
    tests = load_tests()
    test = running(tests)
    if not test:
        pipeline.abort('no split test is running.')
    test.update(status=status, ended_at=pipeline.now_iso())
    if winner:
        test['winner'] = winner
    if reason:
        test['reason'] = ' '.join(reason.split())[:300]
    save_tests(tests)
    return test


def cmd_ship(args):
    test = finish('shipped', winner=args.variant)
    print(f"{args.variant} wins the {test['stage']} test: {test[args.variant.lower()]}")
    print("Write it into context/me.md under ## Split test winners, so every command uses it from now on.")


def cmd_stop(args):
    test = finish('stopped', reason=args.reason)
    print(f"The {test['stage']} test is stopped. Nothing changes in how you work.")


def cmd_list(args):
    tests = load_tests()
    if not tests:
        print('No split tests yet.')
        return
    for test in tests:
        end = f" · {test['status']} {test.get('ended_at', '')[:10]}" if test['status'] != 'running' else ' · running'
        winner = f" · winner {test['winner']}" if test.get('winner') else ''
        print(f"{test['started_at'][:10]} {test['stage']}{end}{winner}")
        print(f"  A: {test['a']}")
        print(f"  B: {test['b']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('new', help='Start the test on the leaking step.')
    p.add_argument('stage', choices=tuple(STAGES))
    p.add_argument('--a', required=True, help="What the member does now.")
    p.add_argument('--b', required=True, help='The fix being tested.')
    p.add_argument('--b-checks', help='What every sent copy on B has, comma-separated (see FEATURES).')
    p.add_argument('--a-days', help='A messages test of follow-up rhythm: the days A follows up, "3,7".')
    p.add_argument('--b-days', help='The days B follows up, "1,2,3,4,5".')
    p.add_argument('--mover', help='The top mover this test is for, as /analytics named it.')
    p.set_defaults(func=cmd_new)
    p = sub.add_parser('assign', help='Which variant this lead gets; tags it once.')
    p.add_argument('job_id')
    p.add_argument('--stage', required=True, choices=tuple(STAGES))
    p.set_defaults(func=cmd_assign)
    p = sub.add_parser('status', help='Counts, the chance B beats A, and the call.')
    p.set_defaults(func=cmd_status)
    p = sub.add_parser('ship', help='End the test with a winner.')
    p.add_argument('variant', choices=('A', 'B'))
    p.set_defaults(func=cmd_ship)
    p = sub.add_parser('stop', help='End the test with no winner.')
    p.add_argument('--reason', required=True)
    p.set_defaults(func=cmd_stop)
    p = sub.add_parser('list', help='Every test, running and finished.')
    p.set_defaults(func=cmd_list)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
