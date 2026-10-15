#!/usr/bin/env python3
"""Every stage checked, the few things that matter most named, all from the member's own data.

Four stages, one per arrow of the funnel: Proposals, Messaging, Calls, Offers. Each stage has
a few sections, one thing each, and every item in a section says how the member is doing.

Where the numbers come from, so nothing is a guess:
    code     counted from the pipeline, the sent letters, the threads and the call transcripts
    calls    each call graded once from its transcript, saved beside it (jobs/<id>/call-grade.json)
             and added up here across every call in the window; a call is regraded only if its
             transcript changed
    claude   read from the member's own material (profile, photo, portfolio, the proposal video)
A section's rating comes from its items, never typed in: anything missing is holding them back.

Each stage opens on its movers: the 1 to 3 changes that get 90% of that stage's result, each
audited against the member's own data. A stage can also carry a coach's note.

One mover of the stuck stage carries the split test, and saving starts it: the change that matters
most is the change that gets tested. While a test runs, it stays on its stage until shipped or stopped.

    python3 code/diagnosis.py facts            every stage, measured items filled in, calls still to grade
    python3 code/diagnosis.py media            download the profile photo and portfolio images to look at
    python3 code/diagnosis.py save --file -    validate the movers, notes, judged items and call grades
    python3 code/diagnosis.py show             what was saved this week
"""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analytics  # noqa: E402
import application_check as letters  # noqa: E402
import leak  # noqa: E402
import pipeline  # noqa: E402
import split_test  # noqa: E402

STATUSES = ('ok', 'missing', 'weak', 'optional', 'unknown')
LETTERS_READ = 12
WINDOW_DAYS = 28
GIGRADAR = 'GigRadar, 134k proposals'
UPWORK = 'Upwork help center'
COURSE = 'Course method'
NOT_CHECKED = 'Not checked this week.'

AREAS = ('replies', 'conversations', 'calls', 'closing')
TITLES = {'replies': 'Proposals', 'conversations': 'Messaging', 'calls': 'Calls', 'closing': 'Offers'}
AREA_OF = {'weekly_volume': 'replies', 'job_fit': 'replies', 'speed_10min': 'replies', 'reply_rate': 'replies',
           'first_reply': 'conversations', 'follow_ups_on_time': 'conversations', 'reply_to_call': 'conversations',
           'invite_to_call': 'conversations', 'booked_to_held': 'conversations', 'held_to_proposal': 'calls',
           'proposal_on_time': 'calls', 'proposal_to_won': 'closing', 'offer_to_contract': 'closing'}

# (section key, name, [(item key, name, what good looks like, source, where the answer comes from)])
SECTIONS = {
    'replies': [
        ('volume', 'Proposals sent', [
            ('goal', 'Your daily goal', 'Your own goal, every working day.', 'Your goal', 'code'),
            ('missed', 'Days with none', 'No working day without proposals.', 'Your goal', 'code')]),
        ('speed', 'Speed to lead', [
            ('fast', 'Sent within 10 minutes', 'Sent in 3 to 4 minutes: 11.9% replies. At 30 to 45 minutes: 5.3%.', GIGRADAR, 'code')]),
        ('jobs', 'Which jobs you bid on', [
            ('crowd', 'Crowded jobs', 'Quieter jobs against crowded ones, in your own replies.', 'Your data', 'code'),
            ('mix', 'One kind of job', 'One offer, so your proof fits every proposal.', 'Your data', 'code'),
            ('budget', 'Your bid against their budget', 'Inside the budget the client posted.', 'Your data', 'code'),
            ('clients', 'Clients who hire', 'Payment verified, and has hired or spent before.', UPWORK, 'code')]),
        ('proposal', 'Your proposal', [
            ('opener', 'First two lines', 'About their job, no "Hi, I\'m". It is all the client sees in the list.', COURSE, 'code'),
            ('personal', 'Personal to them', 'Their job in the first lines.', COURSE, 'code'),
            ('result', 'A result with a number', 'What changed for a client like them, in a number.', COURSE, 'code'),
            ('offer', 'Offer and guarantee', '"My goal is to get you X in Y, or Z", in one line.', COURSE, 'code'),
            ('question', 'Ends with a question', 'A question about their job: 479% more replies than a pitch.', GIGRADAR, 'code'),
            ('proof', 'Social proof', 'A named client or a case like theirs.', COURSE, 'claude')]),
        ('proposal_video', 'Your proposal video', [
            ('sent', 'A Loom with every proposal', 'One short video per job, about their job.', COURSE, 'code'),
            ('opens', 'First 10 seconds about them', 'Their problem first, from the transcript.', COURSE, 'claude'),
            ('screen', 'Their site on screen', 'Their own site or account, seen in the screenshots.', COURSE, 'claude'),
            ('energy', 'Smiling and eye contact', 'Warm and awake in the screenshots.', COURSE, 'claude')]),
        ('profile', 'Your profile', [
            ('seen', 'What clients see before opening', 'Clients open most proposals on quieter jobs.', UPWORK, 'code'),
            ('photo', 'Photo', 'A clear, friendly face: looked at, not assumed.', UPWORK, 'claude'),
            ('bio_video', 'Bio video', 'Required: a short video on the profile.', COURSE, 'claude'),
            ('title', 'Title', 'Names the result for the client you want, not job labels.', 'Top-earner profiles', 'claude'),
            ('bio', 'Bio', 'Their result first, then proof, then the offer.', 'Top-earner bio formula', 'claude'),
            ('portfolio', 'Portfolio', 'Pieces that match your jobs, with images or video.', 'Top-earner profiles', 'claude')]),
    ],
    'conversations': [
        ('answer', 'How fast you answer', [
            ('median', 'Typical first answer', 'Within 5 minutes, in working hours.', 'Course target', 'code')]),
        ('replies', 'Your replies', [
            ('grade', 'Easy to read', 'Grade 7 reading level or under.', 'Flesch-Kincaid grade', 'code'),
            ('asks_call', 'Asks for a call', 'Every thread asks for a short call: a time, or a link to book one.', COURSE, 'code'),
            ('wrote_back', 'Clients who answered', 'Most clients write back or book the call.', 'Your data', 'code')]),
        ('follow_ups', 'Follow-ups and show-ups', [
            ('on_time', 'Follow-ups on day 3 and 7', 'Day 3 and day 7 of silence, then stop.', COURSE, 'code'),
            ('held', 'Booked calls that happened', 'Nine in ten booked calls happen.', 'Course target', 'code')]),
    ],
    'calls': [
        ('on_call', 'On the call', [
            ('rapport', 'Connection', 'Small talk, their goal, a warm moment before your pitch.', COURSE, 'calls'),
            ('qualify', 'Budget and timeline asked', 'Both asked before your price.', COURSE, 'calls'),
            ('clear', 'Crystal clear what you deliver', 'By the end they can say back what they get.', COURSE, 'calls'),
            ('price', 'Price said', 'A number or a range, out loud.', COURSE, 'calls'),
            ('objections', 'Objections handled', 'Every worry answered before you hang up.', COURSE, 'calls'),
            ('next', 'Next call booked, with homework', 'In the calendar, and what each of you brings to it.', COURSE, 'calls')]),
        ('talk', 'Talk time and length', [
            ('talk_time', 'Who did the talking', 'The client talks at least half the time.', 'Gong Labs, 25,000+ sales calls', 'code'),
            ('length', 'Call length', '30 minutes or more.', COURSE, 'code')]),
        ('after', 'After the call', [
            ('fast', 'Offer within 30 minutes', 'A decision-ready offer within 30 minutes of the call.', 'Course target', 'code')]),
    ],
    'closing': [
        ('offers', 'Your offers', [
            ('closed', 'Offers that closed', 'At least one in five offers closes.', 'Course target', 'code'),
            ('questions', 'Clear on its own', 'No "what is included?" questions once it lands.', 'Your threads', 'code'),
            ('followed', 'Followed up', 'A message on day 3 and day 7 while they decide.', COURSE, 'code')]),
    ],
}
CALL_ITEMS = tuple(key for _, _, items in SECTIONS['calls'] for key, *_, how in items if how == 'calls')


def item(key, status, note):
    return {'key': key, 'status': status, 'note': note}


def share_status(k, n, good=0.8, fair=0.5):
    return 'unknown' if not n else 'ok' if k / n >= good else 'weak' if k / n >= fair else 'missing'


def window_start(now):
    return now - datetime.timedelta(days=WINDOW_DAYS)


def parse(value):
    try:
        stamp = datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=datetime.timezone.utc)


# ---------------------------------------------------------------- proposals

def measured_replies(jobs, now):
    f = leak.facts(jobs, now=now)
    s, o = f['sent'], f['opened']
    finished = o['finished']
    out = {key: {} for key, _, _ in SECTIONS['replies']}
    out['volume']['goal'] = item('goal', 'ok' if s['sent'] >= 0.9 * s['goal'] else 'missing',
                                 f"{s['sent']} sent against a goal of {s['goal']}, last {s['working_days']} working days.")
    out['volume']['missed'] = item('missed', 'ok' if not s['days_with_none'] else 'missing',
                                   f"{s['days_with_none']} of {s['working_days']} working days had none.")
    fast = next((r for r in f['speed'] if r['band'] == '<10m'), {'sent': 0, 'replied': 0})
    known = sum(r['sent'] for r in f['speed'] if r['band'] != 'unknown')
    out['speed']['fast'] = (item('fast', 'ok' if fast['sent'] >= 0.8 * known else 'missing',
                                 f"{fast['sent']} of {known} within 10 minutes; {fast['replied']} of your {o['replied']} replies came from those.")
                            if known else item('fast', 'unknown', 'No posting times saved yet.'))
    crowd = {r['band']: r for r in f['crowd']}
    busy = [crowd[b] for b in ('15-50', '50+') if b in crowd]
    calm = [crowd[b] for b in ('<5', '5-15') if b in crowd]
    busy_n, busy_r = sum(r['sent'] for r in busy), sum(r['replied'] for r in busy)
    calm_n, calm_r = sum(r['sent'] for r in calm), sum(r['replied'] for r in calm)
    if busy_n + calm_n:
        bad = busy_n >= 10 and busy_n >= 0.25 * finished and (busy_r / busy_n if busy_n else 0) < (calm_r / calm_n if calm_n else 0) / 2
        out['jobs']['crowd'] = item('crowd', 'missing' if bad else 'ok',
                                    f"{busy_n} of {finished} went to jobs with 15+ proposals: {busy_r} replies. Quieter jobs: {calm_r} of {calm_n}." if busy_n
                                    else f"None of {finished} went to jobs with 15+ proposals.")
    else:
        out['jobs']['crowd'] = item('crowd', 'unknown', 'How crowded each job was is not saved yet.')
    top = f['mix']['tracks'][0] if f['mix']['tracks'] else None
    out['jobs']['mix'] = (item('mix', 'ok' if f['mix']['top_share'] >= 70 else 'weak', f"{f['mix']['top_share']}% came from one search: {top['track']}.")
                          if top else item('mix', 'unknown', 'No searches saved yet.'))
    out['jobs'].update(measured_clients(jobs, now))
    if finished and o['open_unknown'] < 0.5 * (finished - o['replied']):
        seen = finished - o['never_opened'] - o['open_unknown']
        calm_seen = sum(r.get('opened', 0) for r in calm)
        good = (calm_n and calm_seen >= 0.7 * calm_n) or seen >= 0.5 * (finished - o['open_unknown'])
        note = f"{seen} of {finished} opened." + (f" Quieter jobs: {calm_seen} of {calm_n}." if calm_n and busy_n else '')
        out['profile']['seen'] = item('seen', 'ok' if good else 'missing', note)
    else:
        out['profile']['seen'] = item('seen', 'unknown', 'Whether clients opened your proposals is not saved yet.')
    out['proposal'].update(measured_letters(jobs))
    sent = sent_letters(jobs)
    if sent:
        with_video = sum(bool(letters.has_video(text)) for _, text in sent)
        out['proposal_video']['sent'] = item('sent', share_status(with_video, len(sent)), f"{with_video} of your last {len(sent)} proposals had a video.")
        if not with_video:
            # No proposal video to watch: the count says it all, and nothing else is judged.
            out['proposal_video'].update({k: item(k, 'unknown', NOT_CHECKED) for k in ('opens', 'screen', 'energy')})
    return out


def measured_clients(jobs, now):
    rows = leak.finished_group(jobs, now)
    facts = lambda job: job.get('application_facts') or {}
    out = {}
    known = [(job, ok) for job, ok in rows if facts(job).get('bid_band') in ('below', 'within', 'above')]
    if len(known) >= 10:
        inside = [(job, ok) for job, ok in known if facts(job)['bid_band'] == 'within']
        over = [(job, ok) for job, ok in known if facts(job)['bid_band'] == 'above']
        note = f"{len(inside)} of {len(known)} bids inside their budget: {sum(ok for _, ok in inside)} replies."
        if over:
            note += f" Over budget: {sum(ok for _, ok in over)} of {len(over)}."
        out['budget'] = item('budget', 'ok' if len(inside) >= 0.7 * len(known) else 'weak', note)
    else:
        out['budget'] = item('budget', 'unknown', 'Your bids and their budgets are not saved yet.')
    hires = lambda job: facts(job).get('payment_verified') is True and facts(job).get('client_spent_band') not in ('0', 'unknown', None)
    known = [(job, ok) for job, ok in rows if facts(job).get('payment_verified') in (True, False)]
    if len(known) >= 10:
        good = [(job, ok) for job, ok in known if hires(job)]
        rest = [(job, ok) for job, ok in known if not hires(job)]
        note = f"{len(good)} of {len(known)} to verified clients who have spent: {sum(ok for _, ok in good)} replies."
        if rest:
            note += f" The others: {sum(ok for _, ok in rest)} of {len(rest)}."
        out['clients'] = item('clients', 'ok' if len(good) >= 0.7 * len(known) else 'weak', note)
    else:
        out['clients'] = item('clients', 'unknown', 'Client payment and spend are not saved yet.')
    return out


def sent_letters(jobs):
    rows = []
    for job in jobs:
        path = pipeline.jobs_dir() / str(job['id']) / 'application.sent.md'
        if path.is_file() and job.get('applied_at'):
            rows.append((job, path.read_text(encoding='utf-8')))
    rows.sort(key=lambda row: str(row[0].get('applied_at')), reverse=True)
    return rows[:LETTERS_READ]


RESULT = re.compile(r'\d+(?:\.\d+)?\s?%|\$\s?\d|\b\d+x\b|\bfrom \d+ to \d+\b', re.I)


def measured_letters(jobs):
    sent = sent_letters(jobs)
    if not sent:
        return {}
    n = len(sent)
    def count(test):
        return sum(1 for job, text in sent if test(job, letters.letter_body(letters.split_letter(text)[0])))
    def card(body):
        return ' '.join(re.findall(r"\b[\w'$%+-]+\b", body)[:letters.CARD_WORDS]).lower()
    trade = set(re.findall(r"[\w']+", analytics.sections().get('What you do', '').lower()))
    filler = count(lambda job, body: any(re.search(p, card(body)) for p in letters.FILLER_OPENERS))
    own = count(lambda job, body: any(w in card(body) for w in re.findall(r"[\w']+", str(job.get('title', '')).lower())
                                      if len(w) > 3 and w not in trade))
    result = count(lambda job, body: bool(RESULT.search(body)))
    offer = count(lambda job, body: bool(letters.OFFER.search(body) or any(r in body.lower() for r in letters.RISK)))
    question = count(lambda job, body: '?' in body)
    return {
        'opener': item('opener', share_status(n - filler, n), f"{n - filler} of your last {n} open without filler such as \"Hi, I'm\"."),
        'personal': item('personal', share_status(own, n), f"{own} of {n} name their job in the first lines."),
        'result': item('result', share_status(result, n), f"{result} of {n} give a result with a number."),
        'offer': item('offer', share_status(offer, n), f"{offer} of {n} make an offer with a guarantee."),
        'question': item('question', share_status(question, n), f"{question} of {n} ask the client a question."),
    }


# ---------------------------------------------------------------- messaging

TIME = re.compile(r'\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b|\b\d{1,2}:\d{2}\b', re.I)
CALL_WORDS = re.compile(r'\b(call|chat|meet|meeting|zoom|book|calendar)\b', re.I)


def syllables(word):
    word = word.lower()
    groups = re.findall(r'[aeiouy]+', word)
    count = len(groups) - (1 if word.endswith('e') and len(groups) > 1 else 0)
    return max(1, count)


def reading_grade(text):
    """Flesch-Kincaid grade level: the school year a reader needs."""
    words = re.findall(r"[A-Za-z']+", text)
    sentences = max(1, len(re.findall(r'[.!?]+(?:\s|$)', text)))
    if not words:
        return None
    return 0.39 * len(words) / sentences + 11.8 * sum(map(syllables, words)) / len(words) - 15.59


def threads(jobs):
    for job in jobs:
        try:
            thread = json.loads((pipeline.jobs_dir() / str(job['id']) / 'thread.json').read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        messages = sorted((m for m in thread.get('messages') or [] if isinstance(m, dict) and parse(m.get('at'))),
                          key=lambda m: parse(m['at']))
        if messages:
            yield job, messages


def booked(job):
    return bool(job.get('call_booked_at') or job.get('call_held_at') or job.get('status') in ('call', 'offer', 'won'))


def plain_minutes(minutes):
    return f'{minutes:g} minutes' if minutes < 90 else f'about {round(minutes / 60):g} hours'


def measured_messaging(jobs, snapshot, now):
    kpis = snapshot.get('kpis', {})
    out = {'answer': {}, 'replies': {}, 'follow_ups': {}}
    minutes = (kpis.get('first_reply') or {}).get('value')
    out['answer']['median'] = item('median', 'unknown' if not analytics.number(minutes) else 'ok' if minutes <= 5 else 'weak' if minutes <= 15 else 'missing',
                                   f"Typically {plain_minutes(minutes)}." if analytics.number(minutes) else 'No answer times saved yet.')
    start = window_start(now)
    mine, asked, answered, replied_threads = [], 0, 0, 0
    for job, messages in threads(jobs):
        if not any(m.get('from') == 'client' and parse(m['at']) >= start for m in messages):
            continue
        own = [m for m in messages if m.get('from') == 'me']
        if not own:
            continue
        replied_threads += 1
        mine += [m.get('text', '') for m in own]
        # A call ask names the call, or offers two times to pick from.
        if any(CALL_WORDS.search(m.get('text', '')) and ('?' in m.get('text', '') or TIME.search(m.get('text', '')))
               or len(TIME.findall(m.get('text', ''))) >= 2 for m in own):
            asked += 1
        first = parse(own[0]['at'])
        # A client who wrote back, or booked the call, answered well; one who went quiet did not.
        if any(m.get('from') == 'client' and parse(m['at']) > first for m in messages) or booked(job):
            answered += 1
    # Graded as one text, so a two-word "Sounds good" cannot drag the grade below zero.
    said = [t.strip() for t in mine if t.strip()]
    grade = reading_grade(' '.join(t if t[-1] in '.!?' else t + '.' for t in said)) if said else None
    if grade is not None:
        grade = max(1, grade)
        out['replies']['grade'] = item('grade', 'ok' if grade <= 7 else 'weak' if grade <= 9 else 'missing',
                                       f"Your messages read at grade {grade:.0f}, across {len(said)} messages.")
    else:
        out['replies']['grade'] = item('grade', 'unknown', 'No messages of yours saved yet.')
    out['replies']['asks_call'] = (item('asks_call', share_status(asked, replied_threads), f"{asked} of {replied_threads} threads asked for a call.")
                                   if replied_threads else item('asks_call', 'unknown', 'No threads saved yet.'))
    out['replies']['wrote_back'] = (item('wrote_back', share_status(answered, replied_threads, 0.6, 0.3), f"{answered} of {replied_threads} clients wrote back or booked a call after your reply.")
                                    if replied_threads else item('wrote_back', 'unknown', 'No threads saved yet.'))
    k, n = (kpis.get('follow_ups_on_time') or {}).get('k'), (kpis.get('follow_ups_on_time') or {}).get('n')
    out['follow_ups']['on_time'] = item('on_time', share_status(k, n, 0.9), f"{k} of {n} follow-ups went out on their day." if n else 'None were due yet.')
    k, n = (kpis.get('booked_to_held') or {}).get('k'), (kpis.get('booked_to_held') or {}).get('n')
    out['follow_ups']['held'] = item('held', share_status(k, n, 0.9, 0.7), f"{k} of {n} booked calls happened." if n else 'No booked calls came due yet.')
    return out


# ---------------------------------------------------------------- calls

STAMP = re.compile(r'^\s*([^:\[]{1,80}?):\s*\[(\d{1,2}):(\d{2})(?::(\d{2}))?\]')


WORDS_PER_SECOND = 2.0   # 120 words a minute, a slow talker: a turn never runs longer than its words need
PAUSE_S = 5


def talk_time(text):
    """Seconds each side spoke, from the transcript's timestamps. A turn runs to the next one, but
    never longer than its words take to say, so a silence, a screen share or the last "thanks" before
    the call ends is not counted as talking."""
    member = re.search(r'^Member:\s*(.+)$', text, re.M)
    duration = re.search(r'^Duration:\s*(\d+(?:\.\d+)?)', text, re.M)
    turns = []
    for line in text.splitlines():
        m = STAMP.match(line)
        if m:
            parts = [int(x) for x in m.groups()[1:] if x is not None]
            seconds = parts[0] * 3600 + parts[1] * 60 + parts[2] if len(parts) == 3 else parts[0] * 60 + parts[1]
            turns.append((m.group(1).strip(), seconds, len(line[m.end():].split())))
    if not member or len(turns) < 2:
        return None
    end = float(duration.group(1)) if duration else turns[-1][1] + turns[-1][2] / WORDS_PER_SECOND + PAUSE_S
    spoke = {'member': 0.0, 'client': 0.0}
    for (name, start, words), nxt in zip(turns, turns[1:] + [(None, end, 0)]):
        side = 'member' if name.casefold() == member.group(1).strip().casefold() else 'client'
        spoke[side] += max(0, min(nxt[1], end, start + words / WORDS_PER_SECOND + PAUSE_S) - start)
    total = spoke['member'] + spoke['client']
    return {'member_share': spoke['member'] / total if total else None, 'length_s': end}


def held_calls(jobs, now):
    start = window_start(now)
    for job in jobs:
        held = parse(job.get('call_held_at'))
        path = pipeline.jobs_dir() / str(job['id']) / 'call.md'
        if held and held >= start and path.is_file():
            yield job, path


def grade_path(job):
    return pipeline.jobs_dir() / str(job['id']) / 'call-grade.json'


def transcript_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def saved_grades(jobs, now):
    """Every held call in the window with its saved grade, and the ones still to grade."""
    graded, todo = [], []
    for job, path in held_calls(jobs, now):
        try:
            grade = json.loads(grade_path(job).read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            grade = None
        if grade and grade.get('transcript_sha') == transcript_sha(path):
            graded.append(dict(grade, job_id=str(job['id']), title=job.get('title', ''), date=str(job.get('call_held_at'))[:10]))
        else:
            todo.append({'job_id': str(job['id']), 'title': job.get('title', ''), 'transcript': str(path)})
    return graded, todo


def call_gap(jobs, now):
    """Why the calls cannot be read yet, in one line, or None when every held call has a transcript."""
    start = window_start(now)
    held = [job for job in jobs if (parse(job.get('call_held_at')) or start - datetime.timedelta(days=1)) >= start]
    bare = [job for job in held if not (pipeline.jobs_dir() / str(job['id']) / 'call.md').is_file()]
    if not held:
        return f'No calls held in the last {WINDOW_DAYS} days.'
    if len(bare) == len(held):
        return f"No transcript saved for your {len(held)} call{'s' if len(held) != 1 else ''} yet. Fireflies saves them."
    return None


def measured_calls(jobs, snapshot, now):
    out = {'on_call': {}, 'talk': {}, 'after': {}}
    graded, todo = saved_grades(jobs, now)
    gap = call_gap(jobs, now) or (f"{len(todo)} call{'s' if len(todo) != 1 else ''} still to grade." if todo and not graded else None)
    if gap:
        out['on_call'] = {key: item(key, 'unknown', gap) for key in CALL_ITEMS}
        out['talk'] = {key: item(key, 'unknown', call_gap(jobs, now) or gap) for key in ('talk_time', 'length')}
    if graded:
        n = len(graded)
        for key in CALL_ITEMS:
            ok = sum(g['checks'][key]['status'] == 'ok' for g in graded)
            miss = next((g['checks'][key].get('quote') for g in graded if g['checks'][key]['status'] != 'ok' and g['checks'][key].get('quote')), '')
            out['on_call'][key] = item(key, share_status(ok, n), f"{ok} of {n} calls." + (f' On one: "{miss}"' if miss and ok < n else ''))
    stats = [s for s in (talk_time(path.read_text(encoding='utf-8')) for _, path in held_calls(jobs, now)) if s and s['member_share'] is not None]
    if stats:
        share = round(100 * sum(s['member_share'] for s in stats) / len(stats))
        minutes = round(sum(s['length_s'] for s in stats) / len(stats) / 60)
        out['talk']['talk_time'] = item('talk_time', 'ok' if share <= 50 else 'weak' if share <= 60 else 'missing',
                                        f"You talked {share}% of the time, across {len(stats)} calls.")
        out['talk']['length'] = item('length', 'ok' if minutes >= 30 else 'weak' if minutes >= 20 else 'missing',
                                     f"Your calls run {minutes} minutes on average.")
    row = (snapshot.get('kpis') or {}).get('proposal_on_time') or {}
    k, n = row.get('k'), row.get('n')
    out['after']['fast'] = item('fast', share_status(k, n, 0.9), f"{k} of {n} calls got their offer within 30 minutes." if n else 'No calls needed an offer yet.')
    return out


# ---------------------------------------------------------------- offers

def measured_offers(jobs, snapshot, now):
    five = {s['key']: s['count'] for s in (snapshot.get('funnel_five') or {}).get('steps', [])}
    offer, deal = five.get('offer', 0), five.get('deal', 0)
    out = {'offers': {'closed': item('closed', 'unknown' if not offer else 'ok' if deal / offer >= 0.2 else 'missing',
                                     f"{deal} of {offer} offers closed." if offer else 'No offers decided yet.')}}
    unclear, followed, with_thread, open_ones = 0, 0, 0, 0
    for job, messages in threads(jobs):
        sent = parse(job.get('proposal_sent_at'))
        if not sent or sent < window_start(now):
            continue
        after = [m for m in messages if parse(m['at']) > sent]
        with_thread += 1
        unclear += any(m.get('from') == 'client' and '?' in m.get('text', '') for m in after)
        if not job.get('won_at') and now - sent > datetime.timedelta(days=3):
            open_ones += 1
            followed += any(m.get('from') == 'me' and parse(m['at']) > sent + datetime.timedelta(days=1) for m in after)
    if with_thread:
        out['offers']['questions'] = item('questions', share_status(with_thread - unclear, with_thread),
                                          f"{unclear} of {with_thread} offers got questions back about what it includes or costs.")
    if open_ones:
        out['offers']['followed'] = item('followed', share_status(followed, open_ones), f"{followed} of {open_ones} open offers got a follow-up.")
    return out


# ---------------------------------------------------------------- facts, save, show

def latest_snapshot():
    snapshot = analytics.last()
    if not isinstance(snapshot, dict) or not snapshot.get('verdict'):
        pipeline.abort('no weekly review is saved yet. Run /analytics first.')
    return snapshot


def facts(now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    snapshot = latest_snapshot()
    stuck = AREA_OF.get(snapshot['verdict'].get('kpi'))
    if not stuck:
        pipeline.abort('this week has no focus step yet.')
    jobs = pipeline.load()
    measured = {'replies': measured_replies(jobs, now), 'conversations': measured_messaging(jobs, snapshot, now),
                'calls': measured_calls(jobs, snapshot, now), 'closing': measured_offers(jobs, snapshot, now)}
    areas = {}
    for area in AREAS:
        sections = []
        for key, name, items in SECTIONS[area]:
            rows = []
            for item_key, item_name, standard, source, how in items:
                found = measured[area].get(key, {}).get(item_key)
                rows.append(dict(key=item_key, name=item_name, standard=standard, source=source, how=how,
                                 status=found['status'] if found else None, note=found['note'] if found else None))
            sections.append({'key': key, 'name': name, 'items': rows})
        areas[area] = {'title': TITLES[area], 'sections': sections}
    graded, todo = saved_grades(jobs, now)
    live = split_test.running(split_test.load_tests())
    test = {k: live.get(k) for k in ('id', 'stage', 'a', 'b', 'started_at', 'mover')} if live else None
    calls_in_test = [u['job_id'] for u in live['units']] if live and live['stage'] == 'call' else []
    return {'week': snapshot['week'], 'stuck': stuck, 'areas': areas, 'calls_to_grade': todo, 'calls_graded': len(graded),
            'test': test, 'calls_in_test': calls_in_test}


def rating(items):
    shown = [i for i in items if i['note'] != NOT_CHECKED]
    if any(i['status'] == 'missing' for i in shown): return 'holding_back'
    if any(i['status'] == 'weak' for i in shown): return 'weak'
    if any(i['status'] == 'ok' for i in shown): return 'fine'
    return 'unknown'


def need(condition, message):
    if not condition:
        pipeline.abort(message)


def lines(value, name, low, high, size):
    need(isinstance(value, list) and low <= len(value) <= high, f'{name}: {low} to {high} entries.')
    return [' '.join(str(v).split())[:size] for v in value]


def save_grades(given, jobs, now):
    """Write each graded call beside its transcript, tied to the transcript it was graded from.
    A call in a running call test also says which way it actually went, A or B."""
    by_id = {str(job['id']): job for job in jobs}
    held = {str(job['id']): path for job, path in held_calls(jobs, now)}
    live = split_test.running(split_test.load_tests())
    in_test = {u['job_id'] for u in live['units']} if live and live['stage'] == 'call' else set()
    for call in given:
        jid = str((call or {}).get('job_id'))
        need(jid in held, f'calls: {jid} is not a call held in the last {WINDOW_DAYS} days with a saved transcript.')
        checks = call.get('checks') or {}
        need(set(checks) == set(CALL_ITEMS), f'calls.{jid}: grade every item: ' + ', '.join(CALL_ITEMS))
        for key, value in checks.items():
            need(isinstance(value, dict) and value.get('status') in ('ok', 'weak', 'missing'), f'calls.{jid}.{key}: status is ok, weak or missing.')
        better = ' '.join(str(call.get('better') or '').split())
        need(better, f'calls.{jid}: say in one line how this call could have gone better.')
        record = {'graded_at': pipeline.now_iso(), 'transcript_sha': transcript_sha(held[jid]), 'better': better[:300],
                  'checks': {k: {'status': v['status'], 'quote': ' '.join(str(v.get('quote') or '').split())[:200]} for k, v in checks.items()}}
        if jid in in_test:
            need(call.get('followed') in ('A', 'B'), f'calls.{jid}: this call is in the call test; from the transcript, did it go the A way or the B way?')
            record['followed'] = call['followed']
        grade_path(by_id[jid]).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')


NUMBER = re.compile(r'\d+(?:[.,]\d+)?')
CASES = re.compile(r'\bof (?:your )?(?:last )?(\d+)\b')
MIN_CASES = 3


def audit_mover(i, m, clean, index, label='movers', area=None):
    """A mover is real only when the member's own data shows the problem: it cites measured items that
    are missing or weak, across enough cases, and every number in its why comes from those items.
    A gap against a standard alone (how a profile looks) stays in the checks; it is not a mover."""
    name = f'{label}[{i}] "{clean["title"]}"'
    paths = m.get('evidence')
    need(isinstance(paths, list) and paths, f'{name}: evidence, the items that prove it, as "area.section.item" from facts.')
    need(not area or all(str(path).startswith(area + '.') for path in paths), f'{name}: evidence comes from this stage, {area}.')
    cited = []
    for path in paths:
        found = index.get(str(path))
        need(found and found['note'] != NOT_CHECKED, f'{name}: {path} is not a checked item.')
        need(found['status'] in ('missing', 'weak'), f'{name}: {path} is {found["status"]}. A mover fixes something missing or weak.')
        cited.append(found)
    data = [c for c in cited if c['how'] in ('code', 'calls')]
    need(data, f'{name}: nothing measured backs it. A gap against a standard alone stays in the checks; it is not a mover.')
    sizes = [int(n) for c in data for n in CASES.findall(c['note'])]
    need(not sizes or max(sizes) >= MIN_CASES, f'{name}: {max(sizes or [0])} cases is too few to call it real. It needs {MIN_CASES} or more.')
    known = set(NUMBER.findall(' '.join(c['note'] for c in cited)))
    invented = [n for n in NUMBER.findall(clean['why']) if n not in known]
    need(not invented, f'{name}: {", ".join(invented)} in why is not in the cited items. Every number comes from their data.')
    return [{'path': str(path), 'name': c['name'], 'source': c['source']} for path, c in zip(paths, cited)]


def stage_movers(area, given, built, index, stuck):
    """The 1 to 3 changes that get 90% of this stage's result, each audited. Needed on the stuck stage,
    and on calls once enough calls are graded to show a problem; any other stage may name its own."""
    raw = given.get('movers') or []
    need(isinstance(raw, list) and len(raw) <= 3, f'{area}.movers: 1 to 3.')
    graded = [i for s in built['sections'] for i in s['items'] if i['how'] == 'calls' and i['status'] in ('missing', 'weak')]
    sizes = [int(n) for i in graded for n in CASES.findall(i['note'])]
    needed = area == stuck or (area == 'calls' and graded and max(sizes or [0]) >= MIN_CASES)
    need(raw or not needed, f'{area}.movers: the 1 to 3 changes that get 90% of the result on {TITLES[area]}, each with its evidence.')
    out = []
    for i, m in enumerate(raw):
        need(isinstance(m, dict) and all(str(m.get(k) or '').strip() for k in ('title', 'why', 'do')),
             f'{area}.movers[{i}]: a title, why (the data behind it) and do (the change).')
        clean = {k: ' '.join(str(m[k]).split())[:400] for k in ('title', 'why', 'do')}
        if m.get('habit') is True:
            clean['habit'] = True
        clean['evidence'] = audit_mover(i, m, clean, index, f'{area}.movers', area)
        out.append(clean)
    return out


TEST_STAGES = {'replies': ('profile', 'proposal'), 'conversations': ('messages',), 'calls': ('call', 'after-call'), 'closing': ('close',)}


def shown_test(test):
    return {'stage': test['stage'], 'a': test['a'], 'b': test['b'], 'since': str(test.get('started_at') or '')[:10]}


def mover_test(payload, areas, stuck, live):
    """Hang the split test on a mover. A running test stays on the first mover of its stage; otherwise
    exactly one mover of the stuck stage names a new test, which save starts, unless every one of them
    is a habit. Returns the new test to start, or None."""
    raw = {a: (payload['areas'].get(a) or {}).get('movers') or [] for a in AREAS}
    named = [(a, i) for a in AREAS for i, m in enumerate(raw[a]) if isinstance(m, dict) and m.get('test')]
    if live:
        area = next(a for a, stages in TEST_STAGES.items() if live['stage'] in stages)
        need(not named, f"a {live['stage']} test is already running; leave test out, it stays on its mover.")
        need(areas[area]['movers'], f"the {live['stage']} test is still running but {TITLES[area]} has no movers. "
                                    'Ship or stop it first: python3 code/split_test.py status')
        areas[area]['movers'][0]['test'] = shown_test(live)
        return None
    if not named and all(m.get('habit') for m in areas[stuck]['movers']):
        return None
    need(len(named) == 1 and named[0][0] == stuck,
         f'one mover of the stuck stage, {TITLES[stuck]}, carries the split test: "test": {{"stage", "a" (what they do now), '
         '"b" (the whole change)}. Give it to the biggest one that can be tested. Only when every one is a habit '
         '("habit": true: volume, speed, a required bio video) is there no test.')
    area, i = named[0]
    test = raw[area][i]['test']
    label = f'{area}.movers[{i}].test'
    stages = TEST_STAGES[area]
    need(isinstance(test, dict) and test.get('stage') in stages, f'{label}.stage for {TITLES[area]}: ' + ', '.join(stages))
    need(str(test.get('a') or '').strip() and str(test.get('b') or '').strip(), f'{label}: a (what they do now) and b (the change), one line each.')
    checks = test.get('b_checks') or []
    need(isinstance(checks, list) and all(c in split_test.FEATURES.get(test['stage'], {}) for c in checks),
         f'{label}.b_checks for {test["stage"]}: ' + (', '.join(split_test.FEATURES.get(test['stage'], {})) or 'none'))
    days = test.get('days')
    if days is not None:
        need(test['stage'] == 'messages' and isinstance(days, dict) and days.get('A') and days.get('B'),
             f'{label}.days: {{"A": [3, 7], "B": [1, 2, 3, 4, 5]}}, for a messages test only.')
        days = {side: split_test.rhythm(','.join(str(d) for d in days[side])) for side in ('A', 'B')}
    mover = areas[area]['movers'][i]
    mover['test'] = {'stage': test['stage'], 'a': ' '.join(str(test['a']).split())[:300], 'b': ' '.join(str(test['b']).split())[:300]}
    return {'area': area, 'mover': i, 'stage': test['stage'], 'a': test['a'], 'b': test['b'], 'checks': checks, 'days': days, 'title': mover['title']}


def validate(payload, expected):
    need(isinstance(payload, dict) and isinstance(payload.get('areas', {}), dict), 'send {"areas": {...}, "calls": [...]}.')
    need('movers' not in payload, 'movers live on each stage: areas.<stage>.movers.')
    stuck = expected['stuck']
    need(not expected.get('calls_to_grade'),
         'grade every call first, whatever the stuck stage: ' + ', '.join(c['job_id'] for c in expected.get('calls_to_grade') or []))
    areas = {}
    for area in AREAS:
        given = payload['areas'].get(area) or {}
        sections = {s.get('key'): s for s in given.get('sections') or [] if isinstance(s, dict)}
        coach = lines(given['coach'], f'{area}.coach', 1, 3, 300) if given.get('coach') else []
        rows = []
        for section in expected['areas'][area]['sections']:
            mine = {i.get('key'): i for i in (sections.get(section['key']) or {}).get('items') or [] if isinstance(i, dict)}
            items = []
            for base in section['items']:
                if base['how'] in ('code', 'calls'):
                    status, note = (base['status'], base['note']) if base['status'] else ('unknown', NOT_CHECKED)
                    need(not mine.get(base['key']), f"{area}.{section['key']}.{base['key']}: measured by code; leave it out.")
                elif base['note'] == NOT_CHECKED:
                    # Code found nothing to judge here (no proposal video sent), so it stays hidden.
                    status, note = 'unknown', NOT_CHECKED
                else:
                    given_item = mine.get(base['key'])
                    if given_item:
                        status, note = given_item.get('status'), ' '.join(str(given_item.get('note') or '').split())
                        need(status in STATUSES and note, f"{area}.{section['key']}.{base['key']}: status and a note from their own material.")
                    else:
                        need(area != stuck, f"{area}.{section['key']}.{base['key']}: the stuck stage is judged in full.")
                        status, note = 'unknown', NOT_CHECKED
                items.append(dict(key=base['key'], name=base['name'], status=status, note=note[:300],
                                  standard=base['standard'], source=base['source'], how=base['how']))
            rows.append({'key': section['key'], 'name': section['name'], 'rating': rating(items), 'items': items})
        areas[area] = {'title': TITLES[area], 'coach': coach, 'sections': rows}
    index = {f"{area}.{s['key']}.{i['key']}": dict(i, section=s['name']) for area in AREAS for s in areas[area]['sections'] for i in s['items']}
    for area in AREAS:
        areas[area]['movers'] = stage_movers(area, payload['areas'].get(area) or {}, areas[area], index, stuck)
    plan = mover_test(payload, areas, stuck, expected.get('test'))
    return {'week': expected['week'], 'stuck': stuck, 'areas': areas, 'saved_at': pipeline.now_iso(), 'new_test': plan}


def diagnosis_path():
    return pipeline.data_dir() / 'diagnosis.json'


def load():
    try:
        value = json.loads(diagnosis_path().read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    if not (isinstance(value, dict) and isinstance(value.get('areas'), dict)):
        return None
    # Call by call, read fresh from the grades saved beside each call.
    try:
        graded, _ = saved_grades(pipeline.load(), datetime.datetime.now(datetime.timezone.utc))
        value['areas'].get('calls', {})['calls'] = [{k: g[k] for k in ('job_id', 'title', 'date', 'better', 'checks')} for g in graded]
    except (OSError, ValueError, KeyError):
        pass
    return value


def cmd_facts(args):
    print(json.dumps(facts(), indent=2))


def cmd_media(args):
    """Download the profile photo and portfolio images so they can be looked at, not assumed."""
    import profile_checks
    data = pipeline.data_dir()
    try:
        profile = json.loads((data / 'profile.json').read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        pipeline.abort('no saved profile. /profile saves it (get_profile action=get to data/profile.json).')
    try:
        highlights = json.loads((data / 'highlights.json').read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        highlights = {}
    found = profile_checks.normalize(profile, highlights)
    out = data / 'profile-media'
    out.mkdir(parents=True, exist_ok=True)
    urls = [('photo', found.get('photo'))]
    for i, p in enumerate(highlights.get('portfolio_projects') or []):
        for key in ('thumbnail', 'thumbnailUrl', 'image', 'cover'):
            if isinstance(p, dict) and isinstance(p.get(key), str):
                urls.append((f'portfolio_{i + 1}', p[key]))
                break
    saved = []
    for name, url in urls:
        if not isinstance(url, str) or not url.startswith('https://'):
            continue
        path = out / f'{name}.jpg'
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                path.write_bytes(response.read(5_000_000))
            saved.append(str(path))
        except OSError as problem:
            print(f'{name}: could not download ({problem})', file=sys.stderr)
    print(json.dumps({'saved': saved, 'bio_video': bool(found.get('video'))}, indent=2))


def cmd_save(args):
    raw = sys.stdin.read() if args.file == '-' else pathlib.Path(args.file).read_text(encoding='utf-8')
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as problem:
        pipeline.abort(f'not JSON: {problem}')
    now = datetime.datetime.now(datetime.timezone.utc)
    if payload.get('calls'):
        need(isinstance(payload['calls'], list), 'calls: one graded object per call.')
        save_grades(payload['calls'], pipeline.load(), now)
    result = validate(payload, facts(now))
    plan = result.pop('new_test')
    if plan:
        test = split_test.start(plan['stage'], plan['a'], plan['b'], plan['checks'], plan['days'], plan['title'])
        result['areas'][plan['area']]['movers'][plan['mover']]['test'] = shown_test(test)
        print(f"Split test started on {test['stage']}: {test['b']}")
    path = diagnosis_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.json.tmp')
    temp.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)
    print(f"Saved: stuck at {TITLES[result['stuck']].lower()}, {len(result['areas'][result['stuck']]['movers'])} movers there, "
          f"{len(payload.get('calls') or [])} calls graded now.")


def cmd_show(args):
    value = load()
    if not value:
        print('No checks saved yet. /analytics saves them.')
        return
    print(f"Stuck at {TITLES[value['stuck']]} ({value['week']})")
    for area in AREAS:
        print(f"\n{TITLES[area]}")
        for m in value['areas'][area].get('movers') or []:
            print(f"* {m['title']}: {m['why']} Do: {m['do']}")
            if m.get('test'):
                print(f"  Split testing ({m['test']['stage']}): A {m['test']['a']} | B {m['test']['b']}")
        for s in value['areas'][area]['sections']:
            print(f"- {s['name']}: {s['rating']}")
            for i in s['items']:
                if i['note'] != NOT_CHECKED:
                    print(f"    [{i['status']}] {i['name']}: {i['note']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    sub.add_parser('facts').set_defaults(func=cmd_facts)
    sub.add_parser('media').set_defaults(func=cmd_media)
    p = sub.add_parser('save')
    p.add_argument('--file', required=True)
    p.set_defaults(func=cmd_save)
    sub.add_parser('show').set_defaults(func=cmd_show)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == '__main__':
    main()
