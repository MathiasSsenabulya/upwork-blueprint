#!/usr/bin/env python3
"""The facts behind the proposal step: how many went out, how fast, who opened, which jobs.

/analytics reads these when the leak is at the top of the funnel, the place it usually
is. Each block answers one question, and the answer points at one fix:

    sent       did you send your target, every working day?
    opened     never opened means the row lost (photo, title, rate, first two lines,
               how late you were); opened with no reply means the inside lost (the Loom,
               the letter, the profile)
    speed      which posting ages your replies came from
    crowd      how many bids landed on jobs that already had 15 or more proposals
    mix        one kind of job, or all over the place?

    python3 code/leak.py [--days 28] [--json]

Reads the pipeline only. Calls nothing and writes nothing.
"""
import argparse
import collections
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import analytics  # noqa: E402
import pipeline  # noqa: E402
from split_test import when  # noqa: E402

REPLY_DAYS = 7
SPEED_BANDS = (('<10m', 'under 10 min'), ('10-60m', '10 to 60 min'), ('1-6h', '1 to 6 hours'),
               ('>6h', 'over 6 hours'), ('unknown', 'unknown'))
CROWD_BANDS = (('<5', 'under 5 proposals'), ('5-15', '5 to 15'), ('15-50', '15 to 50'), ('50+', 'over 50'),
               ('unknown', 'unknown'))
NOT_TRACKS = {'sync', 'notification', 'demo', 'invite', 'recommended'}


def target():
    """Applications a day, working days a week and the weekly goal /analytics measures against."""
    per_day, days = analytics.daily_plan()
    return per_day, days, analytics.bars()['weekly_volume']


def outbound(jobs, start, now):
    rows = []
    for job in jobs:
        applied = when(job, 'applied')
        facts = job.get('application_facts') or {}
        if job.get('imported') or not applied or not (start <= applied <= now):
            continue
        if facts.get('source', 'outbound') != 'outbound':
            continue
        rows.append((job, applied))
    return rows


def replied(job, applied, now):
    """True, False, or None while the seven days are still running."""
    times = [t for t in (when(job, name) for name in ('replied', 'call', 'offer', 'won')) if t and t >= applied]
    if times and min(times) <= applied + datetime.timedelta(days=REPLY_DAYS):
        return True
    return False if now >= applied + datetime.timedelta(days=REPLY_DAYS) else None


def viewed(job):
    value = job.get('proposal_viewed', (job.get('lead_context') or {}).get('proposal_viewed'))
    value = value.get('value') if isinstance(value, dict) else value
    return value if isinstance(value, bool) else None


def track(job):
    names = [str(t).removeprefix('query-') for t in job.get('found_via') or [] if t not in NOT_TRACKS]
    return names[0] if names else 'other'


def finished_group(jobs, now, days=28):
    """The proposals the funnel follows, each with whether it got a reply inside its 7 days."""
    today = now.astimezone(pipeline.member_zone()).date()
    group = analytics.cohort(jobs, 'applied', REPLY_DAYS, today, analytics.span(today, days), 'outbound')
    return [(job, analytics.has_after(job, 'replied', analytics.event(job, 'applied'),
                                      analytics.event(job, 'applied') + datetime.timedelta(days=REPLY_DAYS)))
            for job in group]


def facts(jobs, days=28, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    zone = pipeline.member_zone()
    start = now - datetime.timedelta(days=days)
    rows = outbound(jobs, start, now)
    per_day, days_a_week, weekly = target()

    by_day = collections.Counter(applied.astimezone(zone).date() for _, applied in rows)
    # Working days only, and not today: today is still running.
    last = now.astimezone(zone).date() - datetime.timedelta(days=1)
    calendar = [last - datetime.timedelta(days=n) for n in range(days - 1)]
    working = [d for d in calendar if d.weekday() < days_a_week]
    # Measured over the finished working days, so a morning run is never "short" for today.
    done = sum(by_day[d] for d in calendar)
    goal = round(weekly / days_a_week * len(working))
    sent = {'sent': done, 'goal': goal, 'per_day': per_day, 'days_a_week': days_a_week, 'weekly': weekly,
            'short': max(0, goal - done), 'days_with_none': sum(1 for d in working if not by_day[d]),
            'working_days': len(working), 'days': days, 'best_day': max(by_day.values(), default=0)}

    # The same proposals the funnel follows: sent in the 4 weeks before this one, each with
    # its full 7 days to get a reply, so these counts add up to the funnel's first two boxes.
    finished = finished_group(jobs, now, days)
    opened = {'finished': len(finished), 'replied': sum(ok for _, ok in finished),
              'opened_no_reply': sum(1 for job, ok in finished if not ok and viewed(job) is True),
              'never_opened': sum(1 for job, ok in finished if not ok and viewed(job) is False),
              'open_unknown': sum(1 for job, ok in finished if not ok and viewed(job) is None)}

    speed = []
    for band, label in SPEED_BANDS:
        mine = [(job, ok) for job, ok in finished if (job.get('application_facts') or {}).get('posted_age_band', 'unknown') == band]
        speed.append({'band': band, 'label': label, 'sent': len(mine), 'replied': sum(ok for _, ok in mine)})

    crowd = []
    for band, label in CROWD_BANDS:
        mine = [(job, ok) for job, ok in finished if (job.get('application_facts') or {}).get('proposals_band', 'unknown') == band]
        crowd.append({'band': band, 'label': label, 'sent': len(mine), 'replied': sum(ok for _, ok in mine),
                      'opened': sum(viewed(job) is True for job, _ in mine)})

    tracks = collections.Counter(track(job) for job, _ in rows)
    top = tracks.most_common(1)[0][1] if tracks else 0
    mix = {'tracks': [{'track': name, 'sent': count} for name, count in tracks.most_common()],
           'top_share': round(100 * top / len(rows)) if rows else None,
           'titles': [job.get('title', '') for job, _ in rows][:40]}
    return {'days': days, 'sent': sent, 'opened': opened, 'speed': speed, 'crowd': crowd, 'mix': mix}


def show(result):
    s, o = result['sent'], result['opened']
    print(f"Proposal step, last {result['days']} days, your own applications only")
    plan = (f"{s['per_day']} a day, {s['days_a_week']} days a week" if s['weekly'] == s['per_day'] * s['days_a_week']
            else f"your weekly goal of {s['weekly']:g}")
    print(f"Sent: {s['sent']} against a goal of {s['goal']} ({plan})" + (f", {s['short']} short" if s['short'] else ''))
    print(f"  Working days with none sent: {s['days_with_none']} of {s['working_days']}")
    print(f"Finished (7 days to reply): {o['finished']} · replied {o['replied']}")
    print(f"  Opened, no reply: {o['opened_no_reply']} · never opened: {o['never_opened']}"
          f" · not known: {o['open_unknown']}")
    print('Speed, posting to sent, finished applications:')
    for row in result['speed']:
        if row['sent']:
            print(f"  {row['label']}: {row['sent']} sent, {row['replied']} replied")
    print('Competition when you bid, finished applications:')
    for row in result['crowd']:
        if row['sent']:
            print(f"  {row['label']}: {row['sent']} sent, {row['replied']} replied")
    mix = result['mix']
    print('Job mix by search track:' + (f" top track is {mix['top_share']}% of what you sent" if mix['top_share'] is not None else ''))
    for row in mix['tracks']:
        print(f"  {row['track']}: {row['sent']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--days', type=int, default=28)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)
    if not 1 <= args.days <= 120:
        pipeline.abort('--days must be between 1 and 120.')
    result = facts(pipeline.load(), args.days)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        show(result)


if __name__ == '__main__':
    main()
